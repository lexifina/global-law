#!/usr/bin/env python3
"""Build the answer key: residual IDB appeal record -> district decision reviewed (district docket); reviewing
appellate decision found by appeal docket + JUDGDATE (for the `reviewed` population and the tie-break only).

Rules: MAPPING.md (Unit, classes, Populations, LINKING). Reads only work/ files from parse_source.py and
build_corpus.py and the citation graph (graph/edges.bin, round6 citeforms/edges_delta.tsv.gz). No model output is read.
Helper functions copied from benchmarks/fjc_idb_appeals/link.py.

Outputs:
  key.tsv           one row per key item (residual record, district/bankruptcy appeal type, class NEG/PART/CLEAN)
  key_nodes.tsv     one row per linked district decision (scoring unit): combined class, reviewed flag, half
  link_summary.json counts and failure reasons
"""
import array
import collections
import csv
import datetime
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
import benchlib  # noqa: E402

WORK = os.path.join(HERE, "work")
DS = "fjc_idb_unpub"
CIVIL = {"3", "4", "7"}
CRIM = {"5", "8"} | {str(i) for i in range(13, 23)}
BANKR = {"9", "10", "12"}
APP_WINDOW = 14  # days around JUDGDATE

STOPW = set("""United States America State States People Commonwealth Commissioner Commissioners Company Corporation
    Railway Railroad Insurance County City Town Village Board Bank National Department Dept Director Secretary
    Administrator Estate Matter Ex Parte Re In The Of And For Inc Co Corp Ltd Association Assn Mutual Life Fire
    Trust Savings Loan Federal District Court Mr Mrs Supreme Appeals Plaintiff Defendant Appellant Appellee
    Petitioner Respondent Others Al Et Use Ins Ry Bros Brothers Sons General Central Southern Northern Eastern
    Western American New Mexico York Texas Pacific Atlantic Missouri Union Steamship Ship Steamboat Lessee Lessees
    Heirs Executor Executors Executrix Administratrix Guardian Trustee Trustees Receiver Collector Warden Sheriff
    Treasurer Auditor Governor Attorney Superintendent Mayor Council Town Township School Schools Church Hospital
    Motor Motors Oil Gas Electric Power Light Water Telephone Telegraph Coal Iron Steel Lumber Mining Land Lands
    Title Guaranty Surety Casualty Indemnity Fidelity Accident Assurance Express Transportation Transit Bus Lines
    Line Mills Mill Manufacturing Products Services Service Industries Enterprises Holdings Group Partners Unknown
    Commission Authority Agency Division Office Officer Officers Employees Employee Workers Local International
    Florida California Illinois Ohio Michigan Pennsylvania Georgia Virginia Carolina Jersey Massachusetts Kentucky
    Tennessee Alabama Louisiana Washington Oregon Arizona Colorado Kansas Nebraska Iowa Minnesota Wisconsin Indiana
    Maryland Connecticut Maine Vermont Hampshire Island Delaware Dakota Montana Idaho Nevada Utah Wyoming Alaska Hawaii
    Oklahoma Arkansas Mississippi Hampshire Rhode Columbia Puerto Rico Doe Party Parties""".split())


def name_tokens(nm):
    nm = re.sub(r"\(.*?\)", " ", nm or "")
    return {t.lower() for t in re.findall(r"\b[A-Z][a-z][A-Za-z'\-]{2,}", nm)
            if t.rstrip("'s") not in STOPW and t not in STOPW}


def upper_tokens(nm):
    w = re.findall(r"[A-Za-z][A-Za-z'\-]+", nm or "")
    if len(nm or "") >= 15 and w:
        w = w[:-1]
    return {x.lower() for x in w if len(x) >= 4 and x.title() not in STOPW and x.upper() not in ("PARTY", "ETAL")}


def d2(v):
    try:
        return datetime.date(v // 10000, v // 100 % 100, v % 100)
    except (ValueError, TypeError):
        return None


def shift(v, days):
    d = d2(v)
    if d is None:
        return 0
    return int((d + datetime.timedelta(days=days)).strftime("%Y%m%d"))


def ddiff(a, b):
    x, y = d2(a), d2(b)
    return None if x is None or y is None else abs((x - y).days)


def mdy(s):
    s = (s or "").strip()
    if len(s) != 10 or s[2] != "/" or s[5] != "/":
        return 0
    try:
        v = int(s[6:10]) * 10000 + int(s[0:2]) * 100 + int(s[3:5])
    except ValueError:
        return 0
    return 0 if v <= 19000101 else v


def outcome_class(r):
    try:
        tape = int(r["TAPEYEAR"])
    except ValueError:
        return "OTHER", "?"
    era = "sy71_84" if tape < 1985 else "sy85on"
    o, disp = r["OUTCOME"], r["DISP"]
    if era == "sy85on" and disp not in ("1", "2", "3"):
        return "OTHER", era
    return {"1": "CLEAN", "2": "NEG", "3": "PART", "6": "REMAND"}.get(o, "OTHER"), era


def combine(classes):
    sc = [c for c in classes if c in ("NEG", "PART", "CLEAN")]
    if sc:
        s = set(sc)
        if s == {"NEG"}:
            return "NEG"
        if s == {"CLEAN"}:
            return "CLEAN"
        return "PART"
    return "REMAND" if "REMAND" in classes else "OTHER"


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)


def load_edges(citing):
    out = collections.defaultdict(set)
    p = os.path.join(benchlib.GRAPH, "edges.bin")
    a = array.array("I")
    with open(p, "rb") as f:
        a.fromfile(f, os.path.getsize(p) // 4)
    cs = a[0::2]
    cd = a[1::2]
    del a
    for i, c in enumerate(cs):
        if c in citing:
            out[c].add(cd[i])
    del cs, cd
    dp = os.path.join(benchlib.ROOT, "round6", "history", "citeforms", "edges_delta.tsv.gz")
    with gzip.open(dp, "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            p2 = line.split("\t", 2)
            c = int(p2[0])
            if c in citing:
                out[c].add(int(p2[1]))
    return out


def main():
    dist_idx = collections.defaultdict(list)
    dist = {}
    with open(os.path.join(WORK, "dist_nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            node, repo, court, ddist, kind, date, name, raw, dk, cites, parties = p
            dks = []
            for x in dk.split(";"):
                if not x:
                    continue
                yy, num, t = x.split(":")
                dist_idx[(ddist, yy, int(num))].append((node, t))
                dks.append("%s%05d" % (yy, int(num)))
            dist[node] = {"repo": repo, "ddist": ddist, "kind": kind, "date": int(date or 0), "name": name,
                          "raw": raw, "tok": name_tokens(name) | name_tokens(parties), "dks": dks}
    excl = set()
    with open(os.path.join(WORK, "excl_dockets.tsv"), encoding="utf-8") as f:
        for line in f:
            a, b = line.rstrip("\n").split("\t")
            excl.add((a, b))
    app_idx = collections.defaultdict(list)
    with open(os.path.join(WORK, "app_dk.tsv"), encoding="utf-8") as f:
        for line in f:
            repo, yy, num, node, date = line.rstrip("\n").split("\t")
            app_idx[(repo, yy, int(num))].append((node, int(date or 0)))
    prior = collections.defaultdict(list)
    with open(os.path.join(WORK, "ddocket_appeals.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            prior[(p[0], p[1])].append((int(p[2]), int(p[3]), p[4]))

    st_all = collections.Counter()
    out = []
    pend = []
    for r in rows(os.path.join(WORK, "idb_resid.tsv")):
        cls, era = outcome_class(r)
        apptype = r["APPTYPE"]
        dtype = "civil" if apptype in CIVIL else "criminal" if apptype in CRIM else "bankruptcy" if apptype in BANKR else ""
        st_all["records"] += 1
        if not dtype:
            st_all["excluded_apptype_not_district"] += 1
            continue
        if cls not in ("NEG", "PART", "CLEAN"):
            st_all["not_scored_class_" + cls] += 1
            continue
        judg, appd = mdy(r["JUDGDATE"]), mdy(r["APPDATE"])
        rec = {"idb_idx": r["idb_idx"], "apptype": apptype, "dtype": dtype, "era": era, "disp": r["DISP"],
               "outcome": r["OUTCOME"], "pubstat": r["PUBSTAT"] or "-", "class": cls, "status": "", "reason": "",
               "via": "", "app_node": "", "dist_node": "", "n_cand": "0", "ddist": r["DDIST"], "ddocket": r["DDOCKET"],
               "circuit": r["CIRCUIT"], "docket": r["DOCKET"], "appdate": str(appd), "judgdate": str(judg)}
        out.append(rec)
        # reviewing appellate decision (population + tie-break only; never required for a link)
        circ, dkt = r["CIRCUIT"], r["DOCKET"]
        repo = "cadc" if circ == "0" else "ca%s" % circ if circ in {str(i) for i in range(1, 12)} else ""
        if repo and judg and dkt.isdigit() and len(dkt) in (6, 7):
            cand = [(ddiff(d, judg), n) for n, d in app_idx.get((repo, dkt[:2], int(dkt[2:])), [])]
            cand = sorted((x, n) for x, n in cand if x is not None and x <= APP_WINDOW)
            if cand and (len(cand) == 1 or cand[0][0] < cand[1][0]):
                rec["app_node"] = cand[0][1]
        ddist, ddocket = r["DDIST"], r["DDOCKET"]
        if ddist in ("", "-8"):
            rec["status"], rec["reason"] = "unlinked", "idb_no_district"
            continue
        if not (len(ddocket) == 7 and ddocket.isdigit() and ddocket != "0000000"):
            rec["status"], rec["reason"] = "unlinked", "idb_no_district_docket"
            continue
        yy, num = ddocket[:2], int(ddocket[2:])
        kinds = {"district", "bankruptcy"} if dtype == "bankruptcy" else {"district"}
        c1 = [(n, t) for n, t in dist_idx.get((ddist, yy, num), []) if dist[n]["kind"] in kinds]
        if not c1:
            rec["status"], rec["reason"] = "unlinked", "no_decision_with_docket"
            continue
        ok_t = {"civil": {"cv", "?", "misc"}, "criminal": {"cr", "?", "misc"},
                "bankruptcy": {"cv", "bk", "?", "misc"}}[dtype]
        c2 = [(n, t) for n, t in c1 if t in ok_t]
        if not c2:
            rec["status"], rec["reason"] = "unlinked", "docket_type_mismatch"
            continue
        if not appd and not judg:
            rec["status"], rec["reason"] = "unlinked", "no_dates"
            continue
        lo = shift(mdy(r["DDKTDATE"]), -31) if mdy(r["DDKTDATE"]) else 0
        if appd:
            for pa, pj, pidx in prior.get((ddist, ddocket), []):
                if pidx != r["idb_idx"] and pa and pj and pa < shift(appd, -60) and pj < appd:
                    lo = max(lo, pj)
        his = []
        if appd:
            his.append(shift(appd, 60))
        if judg:
            his.append(shift(judg, -1))
        hi = min(his)
        c3 = [(n, t) for n, t in c2 if lo <= dist[n]["date"] <= hi]
        if not c3:
            rec["status"], rec["reason"] = "unlinked", "outside_date_window"
            continue
        tok = upper_tokens(r["APPELLAN"]) | upper_tokens(r["APPELLEE"])
        c4 = sorted({n for n, t in c3 if dist[n]["tok"] & tok})
        if not c4:
            rec["status"], rec["reason"] = "unlinked", "name_mismatch" if tok else "name_unverifiable"
            continue
        rec["n_cand"] = str(len(c4))
        if len(c4) == 1:
            rec["status"], rec["via"], rec["dist_node"] = "linked", "docket", c4[0]
        else:
            rec["status"], rec["reason"], rec["_cands"] = "pending", "several_in_docket", c4
            pend.append(rec)
    app_nodes = {int(x["app_node"]) for x in out if x["app_node"]}
    edges = load_edges(app_nodes)
    for rec in pend:
        cited = [n for n in rec["_cands"] if rec["app_node"] and int(n) in edges.get(int(rec["app_node"]), ())]
        if len(cited) == 1:
            rec["status"], rec["reason"], rec["via"], rec["dist_node"] = "linked", "", "docket+cite", cited[0]
        else:
            rec["status"] = "unlinked"
        del rec["_cands"]
    # node exclusion (MAPPING Unit / LINKING 6)
    for rec in out:
        if rec["status"] == "linked":
            d = dist[rec["dist_node"]]
            if any((d["ddist"], k) in excl for k in d["dks"]):
                rec["status"], rec["reason"], rec["excl_node"] = "unlinked", "excluded_docket", rec["dist_node"]
                rec["dist_node"] = ""
    for rec in out:
        rec["reviewed"] = ("1" if rec["dist_node"] and rec["app_node"]
                           and int(rec["dist_node"]) in edges.get(int(rec["app_node"]), ()) else
                           "0" if rec["dist_node"] else "")
        rec["half"] = (benchlib.split_half(DS, "district:" + rec["dist_node"]) if rec["status"] == "linked"
                       else benchlib.split_half(DS, "idb:" + rec["idb_idx"]))
    by_node = collections.defaultdict(list)
    for rec in out:
        if rec["status"] == "linked":
            by_node[rec["dist_node"]].append(rec)
    cols = ["idb_idx", "apptype", "dtype", "era", "disp", "outcome", "pubstat", "class", "status", "reason", "via",
            "app_node", "dist_node", "n_cand", "reviewed", "half", "circuit", "docket", "ddist", "ddocket", "appdate",
            "judgdate"]
    with open(os.path.join(HERE, "key.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for rec in out:
            o.write("\t".join(str(rec.get(k, "")).replace("\t", " ") for k in cols) + "\n")
    ncols = ["dist_node", "class", "reviewed", "half", "n_records", "record_classes", "idb_idx", "app_nodes",
             "dist_date", "dist_repo", "dist_name", "dist_docket"]
    units = {}
    with open(os.path.join(HERE, "key_nodes.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(ncols) + "\n")
        for node in sorted(by_node, key=int):
            rs = by_node[node]
            d = dist[node]
            c = combine([x["class"] for x in rs])
            rv = "1" if any(x["reviewed"] == "1" for x in rs) else "0"
            h = benchlib.split_half(DS, "district:" + node)
            units[node] = (c, rv, h)
            o.write("\t".join([node, c, rv, h, str(len(rs)), ",".join(x["class"] for x in rs),
                               ",".join(x["idb_idx"] for x in rs),
                               ",".join(sorted({x["app_node"] for x in rs if x["app_node"]})) or "-", str(d["date"]),
                               d["repo"], d["name"].replace("\t", " "), d["raw"].replace("\t", " ")]) + "\n")
    rep = collections.Counter()
    for rec in out:
        rep["linked:" + rec["via"] if rec["status"] == "linked" else rec["reason"]] += 1
    pop = collections.Counter()
    for node, (c, rv, h) in units.items():
        for split in (h, "all"):
            pop["%s/all/%s" % (split, c)] += 1
            if rv == "1":
                pop["%s/reviewed/%s" % (split, c)] += 1
    summ = {"records_residual": st_all["records"], "source_counts": dict(st_all),
            "key_items": len(out), "linked_key_items": sum(v for k, v in rep.items() if k.startswith("linked")),
            "district_units": len(units), "reviewed_units": sum(1 for v in units.values() if v[1] == "1"),
            "units_by_half_population_class": dict(sorted(pop.items())),
            "items_by_half": dict(collections.Counter(r["half"] for r in out)),
            "reasons_key_items": dict(rep.most_common()),
            "app_node_found_items": sum(1 for r in out if r["app_node"])}
    with open(os.path.join(HERE, "link_summary.json"), "w", encoding="utf-8", newline="\n") as o:
        json.dump(summ, o, indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
