#!/usr/bin/env python3
"""Build the answer key: IDB appeal record -> appellate opinion (CCAD) -> district decision reviewed (district docket).

Rules: MAPPING.md (classes, LINKING). Reads only work/ files produced by build_idb.py, build_ccad.py, build_corpus.py
and the citation graph (graph/edges.bin, round6 citeforms/edges_delta.tsv.gz). No model output is read here.

Outputs:
  key.tsv          one row per crosswalked IDB record: link status, reason, class, half
  key_nodes.tsv    one row per linked district decision (scoring unit): combined class, cited flag, half
  link_report.tsv  failure reasons (key items only, and all records)
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
DS = "fjc_idb_appeals"
CIVIL = {"3", "4", "7"}
CRIM = {"5", "8"} | {str(i) for i in range(13, 23)}
BANKR = {"9", "10", "12"}

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
# (the reader's common.STOPW, plus "Party"/"Parties": the public IDB file writes "PARTY 1" for redacted names)


def name_tokens(nm):
    """Distinctive capitalised name tokens (reader common.name_tokens), case-folded."""
    nm = re.sub(r"\(.*?\)", " ", nm or "")
    return {t.lower() for t in re.findall(r"\b[A-Z][a-z][A-Za-z'\-]{2,}", nm)
            if t.rstrip("'s") not in STOPW and t not in STOPW}


def upper_tokens(nm):
    """IDB names are upper case and cut at 15/20 characters: whole words of 4+ letters, not the last (maybe cut)."""
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


def mdy(s):
    s = (s or "").strip()
    if len(s) != 10 or s[2] != "/" or s[5] != "/":
        return 0
    try:
        v = int(s[6:10]) * 10000 + int(s[0:2]) * 100 + int(s[3:5])
    except ValueError:
        return 0
    return 0 if v <= 19000101 else v


def norm_cite(c):
    m = re.match(r"^\s*(\d+)\s+(.+?)\s+(\d+)\s*$", c or "")
    if not m:
        return None
    rep = re.sub(r"[\s.,'()]", "", m.group(2)).lower().replace("2nd", "2d").replace("3rd", "3d")
    return "%d %s %d" % (int(m.group(1)), rep, int(m.group(3)))


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
    """citing node (int) -> set of cited nodes, for the given citing nodes only."""
    out = collections.defaultdict(set)
    p = os.path.join(benchlib.GRAPH, "edges.bin")
    a = array.array("I")
    with open(p, "rb") as f:
        a.fromfile(f, os.path.getsize(p) // 4)
    cs = a[0::2]
    cd = a[1::2]
    for i, c in enumerate(cs):
        if c in citing:
            out[c].add(cd[i])
    del a, cs, cd
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
    # appellate opinions
    ccad = {r["caseid"]: r for r in rows(os.path.join(WORK, "ccad_cases.tsv"))}
    app_by_cite = collections.defaultdict(list)
    with open(os.path.join(WORK, "app_nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            app_by_cite[p[0]].append((p[1], p[2], int(p[3] or 0), p[4]))
    # district decisions by (ddist, yy, num)
    dist_idx = collections.defaultdict(list)
    dist = {}
    with open(os.path.join(WORK, "dist_nodes.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            node, repo, court, ddist, kind, date, name, raw, dk, cites, parties = p
            dist[node] = {"repo": repo, "court": court, "ddist": ddist, "kind": kind, "date": int(date or 0),
                          "name": name, "raw": raw, "tok": name_tokens(name) | name_tokens(parties)}
            for x in dk.split(";"):
                if not x:
                    continue
                yy, num, t = x.split(":")
                dist_idx[(ddist, yy, int(num))].append((node, t))
    # every appeal from a district docket: for the "earlier appeal" bound
    prior = collections.defaultdict(list)
    with open(os.path.join(WORK, "ddocket_appeals.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            prior[(p[0], p[1])].append((int(p[2]), int(p[3]), p[4]))

    recs = list(rows(os.path.join(WORK, "idb_xw.tsv")))
    st_all = collections.Counter()
    out = []
    pend_cite = []  # records waiting for the citation tie-break
    for r in recs:
        cls, era = outcome_class(r)
        apptype = r["APPTYPE"]
        dtype = "civil" if apptype in CIVIL else "criminal" if apptype in CRIM else "bankruptcy" if apptype in BANKR else ""
        rec = {"idb_idx": r["idb_idx"], "caseid": r["caseid"], "alt": r["alt"], "apptype": apptype, "era": era,
               "disp": r["DISP"], "outcome": r["OUTCOME"], "class": cls, "dtype": dtype or "-",
               "key_item": "1" if (dtype and cls in ("NEG", "PART", "CLEAN")) else "0",
               "app_node": "", "app_date": "", "dist_node": "", "status": "", "reason": "", "n_cand": "0",
               "via": "", "ddist": r["DDIST"], "ddocket": r["DDOCKET"], "appdate": str(mdy(r["APPDATE"])),
               "appellant": r["APPELLAN"], "appellee": r["APPELLEE"]}
        out.append(rec)
        if not dtype:
            rec["status"], rec["reason"] = "excluded", "apptype_not_district"
            continue
        # 1. appellate opinion
        c = ccad.get(r["caseid"])
        if c is None:
            rec["status"], rec["reason"] = "unlinked", "ccad_row_missing"
            continue
        key = norm_cite(c["citation"])
        cdate = int(c["decision_date"] or 0)
        try:
            circ = int(float(c["circuit"]))
        except ValueError:
            circ = -1
        repo = "cadc" if circ == 0 else "ca%d" % circ if 1 <= circ <= 11 else ""
        cand = [x for x in app_by_cite.get(key, []) if x[1] == repo] if key else []
        if not key:
            rec["status"], rec["reason"] = "unlinked", "ccad_no_citation"
            continue
        if not cand:
            rec["status"], rec["reason"] = "unlinked", "app_not_in_corpus"
            continue
        pick = [x for x in cand if x[2] == cdate]
        if len(pick) != 1:
            pick = [x for x in cand if cdate and x[2] // 10000 == cdate // 10000]
        if len(pick) != 1:
            rec["status"], rec["reason"] = "unlinked", "app_ambiguous" if len(pick) > 1 else "app_date_mismatch"
            continue
        app_node, _, app_date, app_name = pick[0]
        rec["app_node"], rec["app_date"] = app_node, str(app_date)
        # 2. district docket
        ddist, ddocket = r["DDIST"].strip(), r["DDOCKET"].strip()
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
        # 3. date window
        appd = mdy(r["APPDATE"])
        lo = shift(mdy(r["DDKTDATE"]), -31) if mdy(r["DDKTDATE"]) else 0
        if appd:
            for pa, pj, pidx in prior.get((ddist, ddocket), []):
                if pidx != r["idb_idx"] and pa and pj and pa < shift(appd, -60) and pj < appd:
                    lo = max(lo, pj)
        hi = shift(app_date, -1)
        if appd:
            hi = min(hi, shift(appd, 60))
        c3 = [(n, t) for n, t in c2 if lo <= dist[n]["date"] <= hi]
        if not c3:
            rec["status"], rec["reason"] = "unlinked", "outside_date_window"
            continue
        # 4. identity
        app_tok = name_tokens(app_name) | upper_tokens(r["APPELLAN"]) | upper_tokens(r["APPELLEE"])
        c4 = sorted({n for n, t in c3 if dist[n]["tok"] & app_tok})
        if not c4:
            rec["status"], rec["reason"] = "unlinked", "name_mismatch" if app_tok else "name_unverifiable"
            continue
        rec["n_cand"] = str(len(c4))
        if len(c4) == 1:
            rec["status"], rec["via"], rec["dist_node"] = "linked", "docket", c4[0]
        else:
            rec["status"], rec["reason"], rec["_cands"] = "pending", "several_in_docket", c4
            pend_cite.append(rec)
    # citation graph: does the appellate opinion cite the district decision?
    app_nodes = {int(x["app_node"]) for x in out if x["app_node"]}
    edges = load_edges(app_nodes)
    for rec in pend_cite:
        cited = [n for n in rec["_cands"] if int(n) in edges.get(int(rec["app_node"]), ())]
        if len(cited) == 1:
            rec["status"], rec["reason"], rec["via"], rec["dist_node"] = "linked", "", "docket+cite", cited[0]
        else:
            rec["status"] = "unlinked"
        del rec["_cands"]
    for rec in out:
        rec["cited"] = ("1" if rec["dist_node"] and int(rec["dist_node"]) in edges.get(int(rec["app_node"]), ())
                        else "0" if rec["dist_node"] else "")
    # scoring units
    by_node = collections.defaultdict(list)
    for rec in out:
        if rec["status"] == "linked":
            by_node[rec["dist_node"]].append(rec)
    for rec in out:
        rec["half"] = benchlib.split_half(DS, "district:" + rec["dist_node"]) if rec["status"] == "linked" \
            else benchlib.split_half(DS, "idb:" + rec["idb_idx"])
    cols = ["idb_idx", "caseid", "alt", "apptype", "dtype", "era", "disp", "outcome", "class", "key_item", "status",
            "reason", "via", "app_node", "app_date", "dist_node", "n_cand", "cited", "half", "ddist", "ddocket",
            "appdate", "appellant", "appellee"]
    with open(os.path.join(HERE, "key.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for rec in out:
            o.write("\t".join(str(rec.get(k, "")).replace("\t", " ") for k in cols) + "\n")
    ncols = ["dist_node", "class", "cited", "half", "n_records", "record_classes", "idb_idx", "app_nodes",
             "dist_date", "dist_repo", "dist_name", "dist_docket"]
    with open(os.path.join(HERE, "key_nodes.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(ncols) + "\n")
        for node in sorted(by_node, key=int):
            rs = by_node[node]
            d = dist[node]
            o.write("\t".join([node, combine([x["class"] for x in rs]),
                               "1" if any(x["cited"] == "1" for x in rs) else "0",
                               benchlib.split_half(DS, "district:" + node), str(len(rs)),
                               ",".join(x["class"] for x in rs), ",".join(x["idb_idx"] for x in rs),
                               ",".join(sorted({x["app_node"] for x in rs})), str(d["date"]), d["repo"],
                               d["name"].replace("\t", " "), d["raw"].replace("\t", " ")]) + "\n")
    # report
    rep = collections.Counter()
    rep_all = collections.Counter()
    for rec in out:
        k = rec["status"] if rec["status"] in ("linked", "excluded") else rec["reason"]
        if rec["status"] == "linked":
            k = "linked:" + rec["via"]
        rep_all[k] += 1
        if rec["key_item"] == "1":
            rep[k] += 1
    with open(os.path.join(HERE, "link_report.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("status_or_reason\tkey_items\tall_records\n")
        for k in sorted(set(rep_all), key=lambda x: -rep_all[x]):
            o.write("%s\t%d\t%d\n" % (k, rep[k], rep_all[k]))
        o.write("total\t%d\t%d\n" % (sum(rep.values()), sum(rep_all.values())))
    nc = collections.Counter((combine([x["class"] for x in rs]),
                              "cited" if any(x["cited"] == "1" for x in rs) else "uncited") for rs in by_node.values())
    summ = {"key_items": sum(rep.values()), "records": len(out),
            "linked_key_items": sum(v for k, v in rep.items() if k.startswith("linked")),
            "district_nodes": len(by_node), "node_class_x_cited": {"%s/%s" % k: v for k, v in sorted(nc.items())},
            "reasons_key_items": dict(rep.most_common())}
    with open(os.path.join(HERE, "link_summary.json"), "w", encoding="utf-8", newline="\n") as o:
        json.dump(summ, o, indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
