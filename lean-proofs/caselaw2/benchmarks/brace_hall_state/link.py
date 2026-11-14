#!/usr/bin/env python3
"""Link Brace & Hall records to corpus decisions (MAPPING.md, LINKING). No model output is read here.

Reads : work/bh_cases.tsv (parse_source.py), graph/nodes.tsv, graph/edges.bin,
        round6/history/citeforms/edges_delta.tsv.gz (corpus citation graph)
Writes: key.tsv        one row per source record (key items and excluded records), link status, reason, half
        key_nodes.tsv  one row per linked decision below (the scoring unit), combined class, half
        link_summary.json
"""
import bisect
import collections
import csv
import datetime
import gzip
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
import benchlib  # noqa: E402

DS = "brace_hall_state"
WORK = os.path.join(HERE, "work")
GRAPH = benchlib.GRAPH

STOP = set("""
state states people commonwealth united city county town township village borough parish
inc incorporated co company companies corp corporation ltd llc llp plc partnership assoc association assn
the and of in re ex parte rel matter estate et al etc for on by to from with at as
department dept division board commission commissioner commissioners authority agency office bureau council
insurance ins mutual casualty indemnity assurance underwriters fire life general national american bank trust
school schools district dist public services service system systems
petitioner petitioners respondent respondents appellant appellants appellee appellees plaintiff plaintiffs
defendant defendants intervenor cross minor child children guardian litem next friend interest application
petition adoption marriage unknown doe john jane others another other heirs deceased individually behalf
director secretary administrator administratrix executor executrix trustee trustees supervisor sheriff
mr mrs ms jr sr dba aka nka fka formerly now known
review disciplinary proceeding proceedings against discipline attorney lawyer bar
stated state's
education transportation commerce revenue taxation tax labor industry industrial industries employment security
health human resources welfare social family families youth motor motors vehicle vehicles highway highways police
water power electric light gas utility utilities telephone railroad railway hospital medical center university
college community development housing zoning planning appeals adjustment workers compensation unemployment
retirement pension employees employee coal oil land title savings loan federal financial finance credit care
nursing home construction contractors building investment investments property properties realty real
enterprises group international products mining corrections correctional prison penitentiary court courts
judge justice municipal environmental protection natural regulation regulatory license licensing medicine
com appeal workmen educ edn dept transp bldg const assn hts cabinet trustees park parks committee superior
""".split())
STATE_SLUG = {}


def slug(state):
    return state.lower().replace(" ", "-")


def toks(s, extra=()):
    out = set()
    for t in re.findall(r"[a-z]+", (s or "").lower()):
        if len(t) >= 3 and t not in STOP and t not in extra:
            out.add(t)
    return out


def norm_cite(c):
    m = re.match(r"^\s*(\d+)\s+(.+?)\s+(\d+)\s*$", c)
    if not m:
        return None
    rep = re.sub(r"[\s.,']", "", m.group(2)).lower().replace("2nd", "2d").replace("3rd", "3d")
    rep = re.sub(r"[()]", "", rep)
    return "%d %s %d" % (int(m.group(1)), rep, int(m.group(3)))


def dnum(s):
    try:
        return datetime.date(int(s[:4]), int(s[4:6]), int(s[6:8])).toordinal()
    except (ValueError, TypeError):
        return None


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)


def load_edges(citing):
    """citing node ids (set of int) -> set of cited node ids (edges.bin + edges_delta)."""
    out = collections.defaultdict(set)
    a = np.fromfile(os.path.join(GRAPH, "edges.bin"), dtype=np.uint32).reshape(-1, 2)
    keys = np.array(sorted(citing), dtype=np.uint32)
    sel = a[np.isin(a[:, 0], keys)]
    del a
    for c, d in sel.tolist():
        out[c].add(d)
    dp = os.path.join(benchlib.ROOT, "round6", "history", "citeforms", "edges_delta.tsv.gz")
    with gzip.open(dp, "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.split("\t", 2)
            c = int(p[0])
            if c in citing:
                out[c].add(int(p[1]))
    return out


def main():
    src = list(rows(os.path.join(WORK, "bh_cases.tsv")))
    states = sorted({r["state"] for r in src if r["state"] != "-"})
    repo_kind = {}
    for st in states:
        s = slug(st)
        repo_kind[s] = (st, "ssc")
        if st == "New York":
            repo_kind["new-york-appellate-1934-1991"] = (st, "app")
            repo_kind["new-york-appellate-1992-2018"] = (st, "app")
        else:
            repo_kind[s + "-appellate"] = (st, "app")
        repo_kind[s + "-other-courts"] = (st, "trial")

    lo_d, hi_d = dnum("19880101"), dnum("19991231")
    node = {}  # id -> (repo, court, date_ord, date_str, name, path)
    ssc_cite = collections.defaultdict(list)  # (state, citekey) -> [id]
    ssc_date = collections.defaultdict(list)  # (state, date_ord) -> [id]
    low_idx = collections.defaultdict(lambda: collections.defaultdict(list))  # (state, kind) -> tok -> [(d, id)]
    with open(os.path.join(GRAPH, "nodes.tsv"), encoding="utf-8", newline="\n") as f:
        for line in f:
            p = line.rstrip("\r\n").split("\t")
            if len(p) < 7 or p[1] not in repo_kind:
                continue
            d = dnum(p[4])
            if d is None or not lo_d <= d <= hi_d:
                continue
            st, kind = repo_kind[p[1]]
            nid = int(p[0])
            node[nid] = (p[1], p[3], d, p[4], p[6], p[2])
            if kind == "ssc":
                for c in re.split(r"[|;]", p[5]):
                    k = norm_cite(c)
                    if k:
                        ssc_cite[(st, k)].append(nid)
                ssc_date[(st, d)].append(nid)
            else:
                stx = set(st.lower().split())
                for t in toks(p[6], stx):
                    low_idx[(st, kind)][t].append((d, nid))
    for k in low_idx:
        for t in low_idx[k]:
            low_idx[k][t].sort()

    # ---- 1. supreme court decision
    for r in src:
        r["key_item"] = int(r["class"] in ("NEG", "PART", "CLEAN") and r["rev_ct"] in ("1", "2", "3")
                            and r["state"] != "-")
        r["ssc_node"], r["ssc_via"], r["ssc_reason"] = "", "", ""
        if r["state"] == "-":
            r["ssc_reason"] = "no_state"
            continue
        st = r["state"]
        stx = set(st.lower().split())
        title_t = toks(r["title_p1"] + " " + r["title_p2"], stx)
        sd = dnum(r["decs_date"]) if r["decs_date"] != "-" else None
        cands = []
        if r["cite"] != "-":
            cands = [n for n in ssc_cite.get((st, r["cite"]), [])
                     if sd is None or abs(node[n][2] - sd) <= 366]
        if len(cands) > 1:
            c2 = [n for n in cands if sd is not None and node[n][2] == sd] or cands
            if len(c2) > 1:
                c3 = [n for n in c2 if toks(node[n][4], stx) & title_t]
                c2 = c3 if c3 else c2
            cands = c2
            via = "cite+disambig"
        else:
            via = "cite"
        if not cands and sd is not None:
            cands = [n for n in ssc_date.get((st, sd), []) if toks(node[n][4], stx) & title_t]
            via = "date+caption"
            if not cands:
                r["ssc_reason"] = "ssc_not_in_corpus"
                continue
        elif not cands:
            r["ssc_reason"] = "ssc_not_in_corpus"
            continue
        if len(cands) > 1:
            r["ssc_reason"] = "ssc_ambiguous"
            continue
        r["ssc_node"], r["ssc_via"] = str(cands[0]), via

    # ---- 2./3. decision below
    citing = {int(r["ssc_node"]) for r in src if r["ssc_node"] and r["key_item"]}
    edges = load_edges(citing)
    win = 1826
    for r in src:
        r.update({"status": "excluded" if not r["key_item"] else "unlinked", "reason": "", "via": "",
                  "below_node": "", "n_cited": 0, "n_uncited": 0, "cited": ""})
        if not r["key_item"]:
            r["reason"] = ("class_" + r["class"].lower()) if r["class"] not in ("NEG", "PART", "CLEAN") \
                else "rev_ct_" + r["rev_ct"]
            continue
        if not r["ssc_node"]:
            r["reason"] = r["ssc_reason"]
            continue
        st = r["state"]
        stx = set(st.lower().split())
        kind = "app" if r["rev_ct"] == "3" else "trial"
        pre = "" if kind == "app" else "trial_"
        sn = int(r["ssc_node"])
        sdate = node[sn][2]
        # party sides from the corpus caption of the supreme court decision (cleaner than the coders' abbreviated
        # titles); a caption without " v. " (In re X, Ex parte X) is one side, with the source title added
        if " v. " in node[sn][4]:
            sl, sr = node[sn][4].split(" v. ", 1)
            side_a, side_b = toks(sl, stx), toks(sr, stx)
        else:
            side_a, side_b = toks(node[sn][4], stx) | toks(r["title_p1"] + " " + r["title_p2"], stx), set()
        id_t = side_a | side_b
        idx = low_idx.get((st, kind), {})
        shared = collections.defaultdict(set)
        for t in id_t:
            lst = idx.get(t, [])
            i = bisect.bisect_left(lst, (sdate - win, -1))
            j = bisect.bisect_left(lst, (sdate, -1))
            for _, nid in lst[i:j]:
                shared[nid].add(t)

        def pair(n):  # one token from each side, distinct
            s = shared[n]
            return any(x != y for x in s & side_a for y in s & side_b)

        def strong_cited(n):
            s = shared[n]
            if not side_a or not side_b:
                return len(s) >= 1
            return pair(n) or bool(s & side_a & side_b)  # same-name parties (Smith v. Smith)

        def strong_uncited(n):
            if not side_a or not side_b:
                return len(shared[n]) >= 2
            return pair(n)

        cited = [n for n in shared if n in edges.get(sn, ()) and strong_cited(n)]
        r["n_cited"] = len(cited)
        if len(cited) == 1:
            r["below_node"], r["via"], r["cited"] = str(cited[0]), "cite", "1"
        elif len(cited) > 1:
            ds = sorted((node[n][2] for n in cited), reverse=True)
            if ds[0] != ds[1]:
                best = max(cited, key=lambda n: node[n][2])
                r["below_node"], r["via"], r["cited"] = str(best), "cite+latest", "1"
            else:
                r["reason"] = pre + "below_several_cited"
                continue
        else:
            unc = [n for n in shared if strong_uncited(n)]
            r["n_uncited"] = len(unc)
            if len(unc) == 1:
                r["below_node"], r["via"], r["cited"] = str(unc[0]), "caption", "0"
            elif len(unc) > 1:
                r["reason"] = pre + "below_several_uncited"
                continue
            else:
                r["reason"] = pre + "below_not_found"
                continue
        r["status"] = "linked"

    # ---- units
    units = collections.OrderedDict()
    for r in src:
        if r["status"] == "linked":
            u = units.setdefault(r["below_node"], {"rows": [], "classes": [], "cited": "0", "ssc": set(),
                                                   "rev": set(), "via": set()})
            u["rows"].append(r["row"])
            u["classes"].append(r["class"])
            u["ssc"].add(r["ssc_node"])
            u["rev"].add(r["rev_ct"])
            u["via"].add(r["via"])
            if r["cited"] == "1":
                u["cited"] = "1"
    for r in src:
        r["half"] = benchlib.split_half(DS, "below:%s" % r["below_node"]) if r["status"] == "linked" \
            else benchlib.split_half(DS, "bh:%s" % r["row"])

    cols = ["row", "masterid", "id_1", "state", "title_p1", "title_p2", "docket", "cite", "decs_date", "juris",
            "rev_ct", "genissue", "disp_vars", "disp_codes", "class", "key_item", "status", "reason", "ssc_node",
            "ssc_via", "ssc_date", "ssc_name", "via", "cited", "below_node", "below_repo", "below_date",
            "below_name", "n_cited", "n_uncited", "half"]
    with open(os.path.join(HERE, "key.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for r in src:
            sn = int(r["ssc_node"]) if r["ssc_node"] else None
            bn = int(r["below_node"]) if r["below_node"] else None
            r["ssc_date"] = node[sn][3] if sn is not None else ""
            r["ssc_name"] = node[sn][4] if sn is not None else ""
            r["below_repo"] = node[bn][0] if bn is not None else ""
            r["below_date"] = node[bn][3] if bn is not None else ""
            r["below_name"] = node[bn][4] if bn is not None else ""
            o.write("\t".join(str(r[c]).replace("\t", " ") or "-" for c in cols) + "\n")

    def combine(cs):
        if all(c == "NEG" for c in cs):
            return "NEG"
        if all(c == "CLEAN" for c in cs):
            return "CLEAN"
        return "PART"

    ucols = ["below_node", "half", "class", "cited", "ia", "record_classes", "bh_rows", "ssc_nodes", "via",
             "state", "below_repo", "below_court", "below_date", "below_name"]
    st_of = {r["below_node"]: r["state"] for r in src if r["status"] == "linked"}
    with open(os.path.join(HERE, "key_nodes.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(ucols) + "\n")
        for bn, u in units.items():
            nd = node[int(bn)]
            o.write("\t".join([bn, benchlib.split_half(DS, "below:%s" % bn), combine(u["classes"]), u["cited"],
                               "1" if u["rev"] == {"3"} else "0", ";".join(u["classes"]), ";".join(u["rows"]),
                               ";".join(sorted(u["ssc"])), ";".join(sorted(u["via"])), st_of[bn], nd[0], nd[1],
                               nd[3], nd[4].replace("\t", " ")]) + "\n")

    # ---- summary
    items = [r for r in src if r["key_item"]]
    ia = [r for r in items if r["rev_ct"] == "3"]
    summ = {
        "records": len(src),
        "key_items": len(items),
        "key_items_rev_ct3": len(ia),
        "linked": sum(r["status"] == "linked" for r in items),
        "linked_rev_ct3": sum(r["status"] == "linked" for r in ia),
        "linked_rev_ct3_cited": sum(r["status"] == "linked" and r["cited"] == "1" for r in ia),
        "fail_reasons": dict(collections.Counter(r["reason"] for r in items if r["status"] != "linked")
                             .most_common()),
        "fail_reasons_rev_ct3": dict(collections.Counter(r["reason"] for r in ia if r["status"] != "linked")
                                     .most_common()),
        "excluded_reasons": dict(collections.Counter(r["reason"] for r in src if not r["key_item"]).most_common()),
        "ssc_via": dict(collections.Counter(r["ssc_via"] or r["ssc_reason"] for r in items).most_common()),
        "below_via": dict(collections.Counter(r["via"] for r in items if r["status"] == "linked").most_common()),
        "units": len(units),
        "units_cited": sum(u["cited"] == "1" for u in units.values()),
        "unit_class": dict(collections.Counter(combine(u["classes"]) for u in units.values()).most_common()),
        "unit_class_cited": dict(collections.Counter(combine(u["classes"]) for u in units.values()
                                                     if u["cited"] == "1").most_common()),
        "unit_half": dict(collections.Counter(benchlib.split_half(DS, "below:%s" % b) for b in units)),
        "unit_half_cited": dict(collections.Counter(benchlib.split_half(DS, "below:%s" % b)
                                                    for b, u in units.items() if u["cited"] == "1")),
        "key_class": dict(collections.Counter(r["class"] for r in items)),
        "linked_by_state_rev_ct3": {st: "%d/%d" % (sum(r["status"] == "linked" for r in ia if r["state"] == st),
                                                   sum(1 for r in ia if r["state"] == st)) for st in states},
        "generated": benchlib.now(),
    }
    with open(os.path.join(HERE, "link_summary.json"), "w", encoding="utf-8", newline="\n") as o:
        json.dump(summ, o, indent=1)
        o.write("\n")
    print(json.dumps({k: v for k, v in summ.items() if k != "linked_by_state_rev_ct3"}, indent=1))


if __name__ == "__main__":
    main()
