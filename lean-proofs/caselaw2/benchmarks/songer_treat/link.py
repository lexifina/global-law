#!/usr/bin/env python3
"""Build the answer key: Songer / Kuersten-Haire case -> appellate decision (citation) -> decision below (PRIORPUB).

Rules: MAPPING.md (classes, key items, LINKING, freshness exclusions). Reads only work/songer96.tsv and
work/songer_kh.tsv (from dta.py), the corpus (graph/nodes.tsv, graph/court_table.tsv), the citation graph
(graph/edges.bin, round6/history/citeforms/edges_delta.tsv.gz) and, for exclusion only, the case list of
round6/shepardized/results/links.tsv and benchmarks/fjc_idb_appeals/key_nodes.tsv. No model output is read.

Outputs:
  key.tsv          one row per Songer case: class, key_item, link status, reason, nodes, half
  key_nodes.tsv    one row per linked, non-excluded decision below (scoring unit): combined class, cited, half
  link_report.tsv  counts by reason (key items; all cases)
  link_summary.json
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

DS = "songer_treat"
WORK = os.path.join(HERE, "work")
APP_REPOS = {"ca%d" % i for i in range(1, 12)} | {"cadc"}
TREAT_CLASS = {"2": "NEG", "3": "NEG", "4": "NEG", "7": "NEG", "5": "PART", "6": "PART", "11": "PART", "1": "CLEAN"}
STATES = ["", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
          "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
          "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
          "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina",
          "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
          "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
          "Wisconsin", "Wyoming", "Virgin Islands", "Puerto Rico", "District of Columbia", "Guam", "",
          "Canal Zone", "Northern Mariana Islands"]
STATE_RX = sorted({s for s in STATES if s}, key=len, reverse=True)


def norm_cite(c):
    m = re.match(r"^\s*(\d+)\s+(.+?)\s+(\d+)\s*$", c)
    if not m:
        return None
    rep = re.sub(r"[\s.,']", "", m.group(2)).lower().replace("2nd", "2d").replace("3rd", "3d")
    rep = re.sub(r"[()]", "", rep)
    return "%d %s %d" % (int(m.group(1)), rep, int(m.group(3)))


REP_NORM = {"fs": "fsupp", "fsup": "fsupp", "fsupp": "fsupp", "fsupp2d": "fsupp2d", "fs2d": "fsupp2d",
            "fsup2d": "fsupp2d", "frd": "frd", "br": "br", "f2d": "f2d", "f2nd": "f2d", "f3d": "f3d", "f": "f",
            "fed": "f", "fcas": "fcas"}


def parse_priorpub(p):
    """-> (status, key, reporter) status: none | unparseable | ok"""
    s = (p or "").strip()
    if not s or s in ("0", "000000000"):
        return "none", None, None
    m = re.match(r"^0*(\d+)\s*([A-Za-z][A-Za-z0-9 .]*?)\s*0*(\d+)\s*z*\s*$", s, re.I)
    if not m:
        return "unparseable", None, None
    rep = re.sub(r"[\s.]", "", m.group(2)).lower()
    rep = REP_NORM.get(rep, rep)
    return "ok", "%d %s %d" % (int(m.group(1)), rep, int(m.group(3))), rep


def kh_date(s, year):
    m = re.match(r"^\s*(\d{1,2})/(\d{1,2})/(\d{2}|\d{4})\s*$", s or "")
    if not m:
        return None
    y = int(m.group(3))
    if y < 100:
        y += 1900 if y >= 50 else 2000
    if year and y != int(year):
        return None
    try:
        return int(datetime.date(y, int(m.group(1)), int(m.group(2))).strftime("%Y%m%d"))
    except ValueError:
        return None


STOPW = set("""v vs in re of the and inc co corp ltd united states america ex rel parte matter company corporation
    et al a an for on by to state people commonwealth commissioner internal revenue county city board bank national
    department secretary director estate trust insurance railway railroad mutual life fire association assn federal
    district court llc lp plaintiff defendant appellant appellee petitioner respondent""".split())


def name_toks(s):
    return {t for t in re.findall(r"[a-z]{3,}", (s or "").lower()) if t not in STOPW}


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)


def load_cases():
    out = []
    for r in rows(os.path.join(WORK, "songer96.tsv")):
        vol = int(r["vol"] or 0)
        app_key = ("%d f3d %d" % (vol - 3000, int(r["beginpg"] or 0)) if vol >= 3000
                   else "%d f2d %d" % (vol, int(r["beginpg"] or 0)))
        try:
            d = int(datetime.date(int(r["year"]), int(r["month"]), int(r["day"])).strftime("%Y%m%d"))
        except (ValueError, TypeError):
            d = None
        out.append({"casenum": r["casenum"], "src": "songer96", "year": int(r["year"]), "date": d,
                    "app_key": app_key, "circuit": r["circuit"], "state": r["state"], "district": r["district"],
                    "source": r["source"], "origin": r["origin"], "method": r["method"],
                    "priorpub": r["priorpub"], "treat": r["treat"]})
    for r in rows(os.path.join(WORK, "songer_kh.tsv")):
        out.append({"casenum": r["casenum"], "src": "kh_update", "year": int(r["year"]),
                    "date": kh_date(r["decisiondate"], r["year"]),
                    "app_key": "%d f3d %d" % (int(r["citevol"] or 0), int(r["beginpage"] or 0)),
                    "circuit": r["circuit"], "state": r["state"], "district": r["district"],
                    "source": r["source"], "origin": r["origin"], "method": r["method"],
                    "priorpub": r["priorpub"], "treat": r["treatment"]})
    return out


def court_info():
    ct = {}
    with open(os.path.join(benchlib.GRAPH, "court_table.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            name = p[1].replace("Sourthern", "Southern")
            fed_trial = (p[5] == "federal" and p[6] in ("trial", "special")
                         and ("District Court" in name or "Bankruptcy Court" in name) and "Appellate" not in name)
            st = ""
            if fed_trial:
                if re.search(r"Columbia|D\.\s?C\.", name):
                    st = "District of Columbia"
                else:
                    for s in STATE_RX:
                        if re.search(r"\b%s\b" % re.escape(s), name):
                            st = s
                            break
            ct[p[0]] = (name, fed_trial, st)
    return ct


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
    cases = load_cases()
    for c in cases:
        c["pp_status"], c["pp_key"], c["pp_rep"] = parse_priorpub(c["priorpub"])
        c["class"] = TREAT_CLASS.get(c["treat"], "OTHER")
    app_keys = {c["app_key"] for c in cases}
    below_keys = {c["pp_key"] for c in cases if c["pp_key"]}
    ct = court_info()

    app_idx = collections.defaultdict(list)    # key -> [(node, repo, date, name)]
    below_idx = collections.defaultdict(list)  # key -> [(node, repo, court, date, name)]
    with open(os.path.join(benchlib.GRAPH, "nodes.tsv"), encoding="utf-8", newline="\n") as f:
        for line in f:
            p = line.rstrip("\r\n").split("\t")
            if len(p) < 7 or not p[5]:
                continue
            keys = {k for k in (norm_cite(x) for x in re.split(r"[|;]", p[5])) if k}
            for k in keys:
                if p[1] in APP_REPOS and k in app_keys:
                    app_idx[k].append((p[0], p[1], int(p[4] or 0), p[6]))
                if k in below_keys:
                    below_idx[k].append((p[0], p[1], p[3], int(p[4] or 0), p[6]))

    # step 1: appellate decision
    for c in cases:
        repo = "cadc" if c["circuit"] in ("0", "00") else ("ca%d" % int(c["circuit"]) if c["circuit"].isdigit()
                                                           and 1 <= int(c["circuit"]) <= 11 else None)
        cands = app_idx.get(c["app_key"], [])
        inrepo = [x for x in cands if x[1] == repo]
        c["app_node"] = c["app_date"] = c["app_name"] = ""
        c["app_reason"] = ""
        if repo is None:
            c["app_reason"] = "app_circuit_not_mapped"
            continue
        exact = [x for x in inrepo if c["date"] and x[2] == c["date"]]
        year = [x for x in inrepo if x[2] // 10000 == c["year"]]
        pick = exact if len(exact) == 1 else (year if len(year) == 1 else None)
        if pick:
            c["app_node"], c["app_date"], c["app_name"] = pick[0][0], pick[0][2], pick[0][3]
        elif len(year) > 1:
            c["app_reason"] = "app_ambiguous"
        elif inrepo:
            c["app_reason"] = "app_wrong_year"
        elif cands:
            c["app_reason"] = "app_court_mismatch"
        else:
            c["app_reason"] = "app_not_in_corpus"

    # step 2: decision below
    pending_cite = []
    for c in cases:
        c["below_node"] = c["below_date"] = c["below_name"] = c["below_repo"] = ""
        c["below_reason"] = ""
        c["below_cands"] = []
        if c["pp_status"] == "none":
            c["below_reason"] = "no_priorpub"
            continue
        if c["pp_status"] == "unparseable":
            c["below_reason"] = "priorpub_unparseable"
            continue
        cands = below_idx.get(c["pp_key"], [])
        if not cands:
            c["below_reason"] = "below_not_in_corpus"
            continue
        dist = [x for x in cands if ct.get(x[2], ("", False, ""))[1]]
        if not dist:
            c["below_reason"] = "below_not_district_court"
            continue
        ref = c["app_date"] or c["date"] or (c["year"] * 10000 + 1231)
        dist = [x for x in dist if x[3] and ref - 150000 <= x[3] <= ref]
        if not dist:
            c["below_reason"] = "below_date_mismatch"
            continue
        sname = STATES[int(c["state"])] if c["state"].isdigit() and int(c["state"]) < len(STATES) else ""
        if sname:
            dist = [x for x in dist if not ct[x[2]][2] or ct[x[2]][2] == sname]
            if not dist:
                c["below_reason"] = "below_state_mismatch"
                continue
        c["below_cands"] = dist
        if len(dist) > 1:
            pending_cite.append(c)

    citing = {int(c["app_node"]) for c in cases if c["app_node"] and c["below_cands"]}
    edges = load_edges(citing)
    for c in cases:
        d = c["below_cands"]
        if not d:
            c["cited"] = ""
            continue
        cited_set = edges.get(int(c["app_node"]), set()) if c["app_node"] else set()
        if len(d) == 1:
            pick = d[0]
        else:
            cc = [x for x in d if int(x[0]) in cited_set]
            if len(cc) == 1:
                pick = cc[0]
            else:
                c["below_reason"] = "below_ambiguous"
                c["cited"] = ""
                continue
        cited = int(pick[0]) in cited_set
        # identity check (MAPPING.md amendment 1): shared distinctive party-name token, or the appellate decision
        # cites the decision below
        if c["app_node"] and not cited and not (name_toks(c["app_name"]) & name_toks(pick[4])):
            c["below_reason"] = "below_name_mismatch"
            c["cited"] = ""
            continue
        c["below_node"], c["below_repo"], c["below_date"], c["below_name"] = pick[0], pick[1], pick[3], pick[4]
        c["cited"] = "1" if cited else "0"

    # freshness exclusions
    fjc_dist, fjc_app = set(), set()
    for r in rows(os.path.join(benchlib.BENCH, "fjc_idb_appeals", "key_nodes.tsv")):
        fjc_dist.add(r["dist_node"])
        fjc_app.update(x for x in r["app_nodes"].split(";") if x)
    shep = set()
    for r in rows(os.path.join(benchlib.ROOT, "round6", "shepardized", "results", "links.tsv")):
        if r["node"]:
            shep.add(r["node"])

    excl = collections.Counter()
    for c in cases:
        c["key_item"] = "1" if (c["class"] != "OTHER" and c["pp_status"] != "none") else "0"
        if c["app_reason"]:
            reason = c["app_reason"]
        else:
            reason = c["below_reason"]
        c["reason"] = reason
        c["status"] = "linked" if not reason and c["below_node"] else "unlinked"
        c["excluded"] = ""
        if c["status"] == "linked":
            ex = []
            if c["below_node"] in fjc_dist:
                ex.append("fjc_dist_node")
            if c["app_node"] in fjc_app:
                ex.append("fjc_app_node")
            if c["below_node"] in shep:
                ex.append("shepardized_node")
            c["excluded"] = "+".join(ex)
            for e in ex:
                excl[(c["key_item"], e)] += 1
            if ex:
                excl[(c["key_item"], "any")] += 1
            if c["app_node"] in shep:
                excl[(c["key_item"], "info_app_node_in_shepardized_not_excluded")] += 1
        c["half"] = benchlib.split_half(DS, "district:%s" % c["below_node"] if c["status"] == "linked"
                                        else "songer:%s" % c["casenum"])

    cols = ["casenum", "src", "year", "date", "app_key", "circuit", "state", "district", "source", "origin", "method",
            "treat", "class", "priorpub", "pp_key", "key_item", "status", "reason", "excluded", "app_node",
            "app_date", "below_node", "below_repo", "below_date", "cited", "half", "app_name", "below_name"]
    with open(os.path.join(HERE, "key.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for c in cases:
            o.write("\t".join(str(c[k] if c[k] is not None else "").replace("\t", " ") for k in cols) + "\n")

    # scoring units
    units = collections.OrderedDict()
    for c in cases:
        if c["status"] == "linked" and not c["excluded"]:
            units.setdefault(c["below_node"], []).append(c)
    with open(os.path.join(HERE, "key_nodes.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(["below_node", "class", "cited", "half", "n_cases", "case_classes", "treats", "casenums",
                           "app_nodes", "below_date", "below_repo", "below_name"]) + "\n")
        for n, cs in units.items():
            scored = [c["class"] for c in cs if c["class"] != "OTHER"]
            if not scored:
                cls = "OTHER"
            elif all(x == "NEG" for x in scored):
                cls = "NEG"
            elif all(x == "CLEAN" for x in scored):
                cls = "CLEAN"
            else:
                cls = "PART"
            cited = "1" if any(c["cited"] == "1" for c in cs) else "0"
            o.write("\t".join([n, cls, cited, benchlib.split_half(DS, "district:%s" % n), str(len(cs)),
                               ";".join(c["class"] for c in cs), ";".join(c["treat"] for c in cs),
                               ";".join(c["casenum"] for c in cs), ";".join(c["app_node"] for c in cs),
                               str(cs[0]["below_date"]), cs[0]["below_repo"],
                               cs[0]["below_name"].replace("\t", " ")]) + "\n")
            for c in cs:
                c["unit_class"] = cls

    # report
    rep = collections.Counter()
    for c in cases:
        rep[("all", c["status"] if c["status"] == "linked" else c["reason"])] += 1
        if c["key_item"] == "1":
            rep[("key", c["status"] if c["status"] == "linked" else c["reason"])] += 1
            rep[("key_" + c["half"], c["status"] if c["status"] == "linked" else c["reason"])] += 1
    with open(os.path.join(HERE, "link_report.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("scope\treason\tn\n")
        for (s, r), n in sorted(rep.items(), key=lambda x: (x[0][0], -x[1])):
            o.write("%s\t%s\t%d\n" % (s, r, n))
    ucls = collections.Counter()
    for n, cs in units.items():
        ucls[(cs[0]["unit_class"], "cited" if any(c["cited"] == "1" for c in cs) else "uncited",
              benchlib.split_half(DS, "district:%s" % n))] += 1
    summ = {
        "cases": len(cases),
        "key_items": sum(c["key_item"] == "1" for c in cases),
        "key_items_linked": sum(c["key_item"] == "1" and c["status"] == "linked" for c in cases),
        "key_fail_reasons": dict(collections.Counter(c["reason"] for c in cases
                                                     if c["key_item"] == "1" and c["status"] != "linked")),
        "all_linked": sum(c["status"] == "linked" for c in cases),
        "exclusions": {"%s:%s" % k: v for k, v in sorted(excl.items())},
        "units": len(units),
        "units_by_class_cited_half": {"%s/%s/%s" % k: v for k, v in sorted(ucls.items())},
        "reporters_linked": dict(collections.Counter(c["pp_rep"] for c in cases if c["status"] == "linked")),
    }
    with open(os.path.join(HERE, "link_summary.json"), "w", encoding="utf-8", newline="\n") as o:
        json.dump(summ, o, indent=1, sort_keys=True)
        o.write("\n")
    print(json.dumps(summ, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
