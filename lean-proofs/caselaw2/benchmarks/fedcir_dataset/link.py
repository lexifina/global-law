#!/usr/bin/env python3
"""Link Federal Circuit Dataset Project documents to corpus decisions (MAPPING.md, LINKING). No model output is read.

Reads : work/fc_docs.tsv (parse_source.py), graph/nodes.tsv, graph/courts.tsv, graph/edges.bin,
        round6/history/citeforms/edges_delta.tsv.gz (corpus citation graph)
Writes: key.tsv        one row per source document (key items and excluded documents), link status, reason, half
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

DS = "fedcir_dataset"
WORK = os.path.join(HERE, "work")
GRAPH = benchlib.GRAPH
csv.field_size_limit(10 ** 8)

# Brace & Hall stop list (benchmarks/brace_hall_state/link.py) + Federal Circuit generic words + VA Secretaries
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
america usa secretary veterans veteran affairs army navy air force forces defense homeland customs border
patent patents trademark trademarks technologies technology tech systems solutions holdings global networks
network communications pharmaceuticals pharmaceutical pharma laboratories labs manufacturing industries
trade order nonprecedential precedential errata corrected opinion modified
derwinski brown west gober principi nicholson peake shinseki gibson mcdonald shulkin wilkie mcdonough collins
""".split())

STATES = {
    "ala": "Alabama", "alaska": "Alaska", "ariz": "Arizona", "ark": "Arkansas", "cal": "California",
    "colo": "Colorado", "conn": "Connecticut", "dc": "Columbia", "del": "Delaware", "fla": "Florida",
    "ga": "Georgia", "guam": "Guam", "haw": "Hawaii", "idaho": "Idaho", "ill": "Illinois", "ind": "Indiana",
    "iowa": "Iowa", "kan": "Kansas", "ky": "Kentucky", "la": "Louisiana", "me": "Maine", "md": "Maryland",
    "mass": "Massachusetts", "mich": "Michigan", "minn": "Minnesota", "miss": "Mississippi", "mo": "Missouri",
    "mont": "Montana", "neb": "Nebraska", "nev": "Nevada", "nh": "New Hampshire", "nj": "New Jersey",
    "nm": "New Mexico", "ny": "New York", "nc": "North Carolina", "nd": "North Dakota", "ohio": "Ohio",
    "okla": "Oklahoma", "or": "Oregon", "pa": "Pennsylvania", "ri": "Rhode Island", "sc": "South Carolina",
    "sd": "South Dakota", "tenn": "Tennessee", "tex": "Texas", "utah": "Utah", "vt": "Vermont", "va": "Virginia",
    "wash": "Washington", "wva": "West Virginia", "wis": "Wisconsin", "wyo": "Wyoming", "vi": "Virgin Islands",
    "pr": "Puerto Rico",
}
DIRS = {"N": "Northern", "S": "Southern", "E": "Eastern", "W": "Western", "M": "Middle", "C": "Central"}

SPECIAL = {
    "CFC": ("United States Court of Federal Claims", "United States Claims Court"),
    "CIT": ("United States Court of International Trade",),
    "CAVC": ("United States Court of Appeals for Veterans Claims", "United States Court of Veterans Appeals"),
}


def district_name(trib):
    t = trib.strip().rstrip(".")
    m = re.match(r"^([NSEWMC])\.D\.(.+)$", t)
    if m:
        pre, rest = DIRS[m.group(1)] + " District of ", m.group(2)
    else:
        m = re.match(r"^D\.(.+)$", t)
        if not m:
            return None
        pre, rest = "District of ", m.group(1)
    st = STATES.get(re.sub(r"[^a-z]", "", rest.lower()))
    if not st:
        return None
    if st == "Columbia":
        st = "the District of Columbia"
        return "United States District Court for " + st
    return "United States District Court for the " + pre + st


def toks(s):
    return {t for t in re.findall(r"[a-z]+", (s or "").lower()) if len(t) >= 3 and t not in STOP}


def norm_cite(c):
    m = re.match(r"^\s*(\d+)\s+(.+?)\s+(\d+)\s*$", c or "")
    if not m:
        return None
    rep = re.sub(r"[\s.,'()]", "", m.group(2)).lower().replace("2nd", "2d").replace("3rd", "3d")
    rep = rep.replace("fappx", "fapp'x").replace("fapp'x", "fappx")
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
    src = list(rows(os.path.join(WORK, "fc_docs.tsv")))
    court_name = {}
    with open(os.path.join(GRAPH, "courts.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\r\n").split("\t")
            court_name[p[0]] = p[1]
    by_name = collections.defaultdict(set)
    for cid, nm in court_name.items():
        by_name[nm].add(cid)
    cafc_courts = by_name["United States Court of Appeals for the Federal Circuit"]
    dist_courts = {cid for cid, nm in court_name.items() if nm.startswith("United States District Court for ")}
    group = {}  # court id -> group key (origin code or district court name)
    for code, names in SPECIAL.items():
        for nm in names:
            for cid in by_name.get(nm, ()):
                group[cid] = code
    for cid in dist_courts:
        group[cid] = "DCT:" + court_name[cid]

    lo_d, hi_d = dnum("19990101"), dnum("20261231")
    node = {}  # id -> (repo, court, date_ord, date_str, name)
    cafc_cite = collections.defaultdict(list)
    cafc_date = collections.defaultdict(list)
    low_idx = collections.defaultdict(lambda: collections.defaultdict(list))  # group -> tok -> [(d, id)]
    with open(os.path.join(GRAPH, "nodes.tsv"), encoding="utf-8", newline="\n") as f:
        for line in f:
            p = line.rstrip("\r\n").split("\t")
            if len(p) < 7:
                continue
            is_cafc = p[3] in cafc_courts
            if not is_cafc and p[3] not in group:
                continue
            d = dnum(p[4])
            if d is None or not lo_d <= d <= hi_d:
                continue
            nid = int(p[0])
            node[nid] = (p[1], p[3], d, p[4], p[6])
            if is_cafc:
                for c in re.split(r"[|;]", p[5]):
                    k = norm_cite(c)
                    if k:
                        cafc_cite[k].append(nid)
                cafc_date[d].append(nid)
            else:
                g = group[p[3]]
                for t in toks(p[6]):
                    low_idx[g][t].append((d, nid))
                    if g.startswith("DCT:"):
                        low_idx["DCT:*"][t].append((d, nid))
    for g in low_idx:
        for t in low_idx[g]:
            low_idx[g][t].sort()
    print("nodes loaded", len(node), "cafc dates", len(cafc_date), file=sys.stderr)

    # ---- 1. Federal Circuit decision
    for r in src:
        r["cafc_node"], r["cafc_via"], r["cafc_reason"] = "", "", ""
        if r["key_item"] != "1":
            continue
        title_t = toks(r["case_name"])
        sd = dnum(r["doc_date"])
        cands, via = [], ""
        k = norm_cite(r["full_cite"]) if r["full_cite"] != "-" else None
        if k:
            cands = [n for n in cafc_cite.get(k, []) if abs(node[n][2] - sd) <= 366]
            via = "cite"
            if len(cands) > 1:
                c2 = [n for n in cands if node[n][2] == sd] or cands
                if len(c2) > 1:
                    c3 = [n for n in c2 if toks(node[n][4]) & title_t]
                    c2 = c3 if c3 else c2
                cands, via = c2, "cite+disambig"
        if not cands:
            cands = [n for n in cafc_date.get(sd, []) if toks(node[n][4]) & title_t]
            via = "date+caption"
            if len(cands) > 1:
                c2 = [n for n in cands if len(toks(node[n][4]) & title_t) >= 2]
                cands = c2 if len(c2) == 1 else cands
        if not cands:
            r["cafc_reason"] = "cafc_not_in_corpus"
            continue
        if len(cands) > 1:
            r["cafc_reason"] = "cafc_ambiguous"
            continue
        r["cafc_node"], r["cafc_via"] = str(cands[0]), via

    # ---- 2./3. decision below
    citing = {int(r["cafc_node"]) for r in src if r["cafc_node"]}
    edges = load_edges(citing)
    win = 1826
    for r in src:
        r.update({"status": "excluded" if r["key_item"] != "1" else "unlinked", "reason": "", "via": "",
                  "below_node": "", "n_cited": 0, "n_uncited": 0, "cited": "", "below_group": ""})
        if r["key_item"] != "1":
            r["reason"] = r["excl_reason"]
            continue
        if not r["cafc_node"]:
            r["reason"] = r["cafc_reason"]
            continue
        if r["origin"] == "DCT":
            dn = district_name(r["trib"]) if r["trib"] != "-" else None
            g = "DCT:" + dn if dn and ("DCT:" + dn) in low_idx else "DCT:*"
        else:
            g = r["origin"]
        r["below_group"] = g
        sn = int(r["cafc_node"])
        sdate = node[sn][2]
        nm = node[sn][4]
        if " v. " in nm:
            sl, sr = nm.split(" v. ", 1)
            side_a, side_b = toks(sl), toks(sr)
            if not side_a or not side_b:  # one side generic (United States, Secretary): one-sided caption
                side_a, side_b = side_a | side_b | toks(r["case_name"]), set()
        else:
            side_a, side_b = toks(nm) | toks(r["case_name"]), set()
        id_t = side_a | side_b
        idx = low_idx.get(g, {})
        shared = collections.defaultdict(set)
        for t in id_t:
            lst = idx.get(t, [])
            i = bisect.bisect_left(lst, (sdate - win, -1))
            j = bisect.bisect_left(lst, (sdate, -1))
            for _, nid in lst[i:j]:
                shared[nid].add(t)

        def pair(n):
            s = shared[n]
            return any(x != y for x in s & side_a for y in s & side_b)

        def strong_cited(n):
            s = shared[n]
            if not side_a or not side_b:
                return len(s) >= 1
            return pair(n) or bool(s & side_a & side_b)

        def strong_uncited(n):  # MAPPING.md Amendment 1
            s = shared[n]
            if not side_a or not side_b:
                return len(s) >= 2
            return pair(n) and len(s & side_a) >= min(2, len(side_a)) and len(s & side_b) >= min(2, len(side_b))

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
                r["reason"] = "below_several_cited"
                continue
        else:
            unc = [n for n in shared if strong_uncited(n)]
            r["n_uncited"] = len(unc)
            if len(unc) == 1:
                r["below_node"], r["via"], r["cited"] = str(unc[0]), "caption", "0"
            elif len(unc) > 1:
                r["reason"] = "below_several_uncited"
                continue
            else:
                r["reason"] = "below_not_found"
                continue
        r["status"] = "linked"

    # ---- units
    units = collections.OrderedDict()
    for r in src:
        if r["status"] == "linked":
            u = units.setdefault(r["below_node"], {"rows": [], "classes": [], "cited": "0", "cafc": set(),
                                                   "origin": set(), "via": set()})
            u["rows"].append(r["uid"])
            u["classes"].append(r["class"])
            u["cafc"].add(r["cafc_node"])
            u["origin"].add(r["origin"])
            u["via"].add(r["via"])
            if r["cited"] == "1":
                u["cited"] = "1"
    for r in src:
        r["half"] = benchlib.split_half(DS, "below:%s" % r["below_node"]) if r["status"] == "linked" \
            else benchlib.split_half(DS, "fc:%s" % r["uid"])

    cols = ["uid", "case_name", "appeal", "origin", "trib", "doc_date", "doc_type", "disp", "full_cite", "class",
            "key_item", "status", "reason", "cafc_node", "cafc_via", "cafc_date", "cafc_name", "below_group", "via",
            "cited", "below_node", "below_repo", "below_date", "below_name", "n_cited", "n_uncited", "half"]
    with open(os.path.join(HERE, "key.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for r in src:
            sn = int(r["cafc_node"]) if r["cafc_node"] else None
            bn = int(r["below_node"]) if r["below_node"] else None
            r["cafc_date"] = node[sn][3] if sn is not None else ""
            r["cafc_name"] = node[sn][4] if sn is not None else ""
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

    ucols = ["below_node", "half", "class", "cited", "origin", "record_classes", "fc_uids", "cafc_nodes", "via",
             "below_repo", "below_court", "below_date", "below_name"]
    with open(os.path.join(HERE, "key_nodes.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(ucols) + "\n")
        for bn, u in units.items():
            nd = node[int(bn)]
            o.write("\t".join([bn, benchlib.split_half(DS, "below:%s" % bn), combine(u["classes"]), u["cited"],
                               ";".join(sorted(u["origin"])), ";".join(u["classes"]), ";".join(u["rows"]),
                               ";".join(sorted(u["cafc"])), ";".join(sorted(u["via"])), nd[0], nd[1], nd[3],
                               nd[4].replace("\t", " ")]) + "\n")

    items = [r for r in src if r["key_item"] == "1"]
    pre = [r for r in items if r["doc_date"] < "20190101"]
    summ = {
        "documents": len(src),
        "key_items": len(items),
        "key_items_pre2019": len(pre),
        "linked": sum(r["status"] == "linked" for r in items),
        "linked_cited": sum(r["status"] == "linked" and r["cited"] == "1" for r in items),
        "linked_pre2019": sum(r["status"] == "linked" for r in pre),
        "fail_reasons": dict(collections.Counter(r["reason"] for r in items if r["status"] != "linked")
                             .most_common()),
        "fail_reasons_pre2019": dict(collections.Counter(r["reason"] for r in pre if r["status"] != "linked")
                                     .most_common()),
        "excluded_reasons": dict(collections.Counter(r["reason"] for r in src if r["key_item"] != "1")
                                 .most_common()),
        "cafc_via": dict(collections.Counter(r["cafc_via"] or r["cafc_reason"] for r in items).most_common()),
        "below_via": dict(collections.Counter(r["via"] for r in items if r["status"] == "linked").most_common()),
        "below_group_all_districts": sum(r["below_group"] == "DCT:*" for r in items),
        "linked_by_origin": {o: "%d/%d" % (sum(r["status"] == "linked" for r in items if r["origin"] == o),
                                           sum(1 for r in items if r["origin"] == o))
                             for o in ("DCT", "CFC", "CIT", "CAVC")},
        "units": len(units),
        "units_cited": sum(u["cited"] == "1" for u in units.values()),
        "unit_class": dict(collections.Counter(combine(u["classes"]) for u in units.values()).most_common()),
        "unit_class_cited": dict(collections.Counter(combine(u["classes"]) for u in units.values()
                                                     if u["cited"] == "1").most_common()),
        "unit_half": dict(collections.Counter(benchlib.split_half(DS, "below:%s" % b) for b in units)),
        "unit_half_cited": dict(collections.Counter(benchlib.split_half(DS, "below:%s" % b)
                                                    for b, u in units.items() if u["cited"] == "1")),
        "key_class": dict(collections.Counter(r["class"] for r in items)),
        "generated": benchlib.now(),
    }
    with open(os.path.join(HERE, "link_summary.json"), "w", encoding="utf-8", newline="\n") as o:
        json.dump(summ, o, indent=1)
        o.write("\n")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
