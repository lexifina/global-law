#!/usr/bin/env python3
"""Link Beim-Hirsch-Kastellec en banc items to corpus decisions (MAPPING.md, LINKING). No model output is read.

Reads : work/items.tsv (parse_source.py), graph/nodes.tsv, graph/courts.tsv, graph/cite_index.tsv, graph/edges.bin,
        round6/history/citeforms/edges_delta.tsv.gz (corpus citation graph)
Writes: key.tsv        one row per source item, link status, reason, half
        key_nodes.tsv  one row per linked panel decision (the scoring unit), sub-class, half
        link_summary.json
"""
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

DS = "bhk_enbanc"
WORK = os.path.join(HERE, "work")
GRAPH = benchlib.GRAPH
csv.field_size_limit(10 ** 8)

# Brace & Hall / fedcir stop list (benchmarks/fedcir_dataset/link.py), generic caption words
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
america usa court courts judge justice warden attorney general
""".split())

ORD = {1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth", 6: "Sixth", 7: "Seventh", 8: "Eighth",
       9: "Ninth", 10: "Tenth", 11: "Eleventh"}
VARIANTS = {2: ["United States Court of Appeals for the Second Circuitt"],
            6: ["United States Court of Appeals for the Six Circuit"],
            9: ["United States Court of Appeals for the Ninth"],
            12: ["United States Court of Appeals for the District of Columbia Circuit",
                 "United States Court of Appeals for the District of Columbia"]}


def toks(s):
    return {t for t in re.findall(r"[a-z]+", (s or "").lower()) if len(t) >= 3 and t not in STOP}


def norm_cite(c):
    """'806 F.2d 318' / '267 F. 3d 45' -> '806 f2d 318'; anything else -> None."""
    m = re.match(r"^\s*(\d+)\s+F\.?\s*([23])d\.?\s+(\d+)\s*$", c or "", re.I)
    if not m:
        return None
    return "%d f%sd %d" % (int(m.group(1)), m.group(2), int(m.group(3)))


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
    if not citing:
        return out
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
    src = list(rows(os.path.join(WORK, "items.tsv")))
    court_name = {}
    with open(os.path.join(GRAPH, "courts.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\r\n").split("\t")
            court_name[p[0]] = p[1]
    by_name = collections.defaultdict(set)
    for cid, nm in court_name.items():
        by_name[nm].add(cid)
    circ_courts = {}
    for c in range(1, 13):
        names = (["United States Court of Appeals for the %s Circuit" % ORD[c]] if c in ORD else []) + VARIANTS.get(c, [])
        circ_courts[c] = set().union(*(by_name.get(n, set()) for n in names))
        assert circ_courts[c], c
    coa = set().union(*circ_courts.values())

    # cites wanted
    want = set()
    for r in src:
        for k in (norm_cite(r["p_cite"]), norm_cite(r["eb_cite"])):
            if k:
                want.add(k)
    cite_nodes = collections.defaultdict(list)
    with open(os.path.join(GRAPH, "cite_index.tsv"), encoding="utf-8") as f:
        for line in f:
            if " f" not in line:
                continue
            k, _, n = line.rstrip("\r\n").rpartition("\t")
            k2 = norm_cite(k.replace("f2d", "F.2d").replace("f3d", "F.3d")) if re.search(r" f[23]d ", k) else None
            if k2 in want:
                cite_nodes[k2].append(int(n))
    need = {n for v in cite_nodes.values() for n in v}

    lo_d, hi_d = dnum("19840101"), dnum("20101231")
    node = {}  # id -> (repo, court, date_ord, date_str, name)
    coa_by_date = collections.defaultdict(list)
    with open(os.path.join(GRAPH, "nodes.tsv"), encoding="utf-8", newline="\n") as f:
        for line in f:
            p = line.rstrip("\r\n").split("\t")
            if len(p) < 7:
                continue
            nid = int(p[0])
            if nid in need or p[3] in coa:
                d = dnum(p[4])
                if nid in need:
                    node[nid] = (p[1], p[3], d, p[4], p[6])
                if p[3] in coa and d is not None and lo_d <= d <= hi_d:
                    node[nid] = (p[1], p[3], d, p[4], p[6])
                    coa_by_date[d].append(nid)
    print("nodes loaded", len(node), "cites found", len(cite_nodes), "of", len(want), file=sys.stderr)

    def link_cite(cite, circuit, d0, lo, hi, other_name):
        """Returns (node or None, reason)."""
        k = norm_cite(cite)
        if not k:
            return None, "no_reporter_cite"
        allc = [n for n in cite_nodes.get(k, []) if n in node]
        if not allc:
            return None, "cite_not_in_corpus"
        inc = [n for n in allc if node[n][1] in circ_courts[circuit]]
        if not inc:
            return None, "cite_other_court"
        cands = [n for n in inc if node[n][2] is not None and lo <= node[n][2] <= hi]
        if not cands:
            return None, "cite_date_mismatch"
        if len(cands) > 1 and d0 is not None:
            c2 = [n for n in cands if node[n][2] == d0]
            cands = c2 or cands
        if len(cands) > 1 and other_name:
            c3 = [n for n in cands if toks(node[n][4]) & toks(other_name)]
            cands = c3 or cands
        if len(cands) > 1:
            return None, "ambiguous"
        return cands[0], "cite"

    # ---- en banc decisions first (needed for rule 2 and caption tie-breaks)
    for r in src:
        r["circ"] = int(r["circuit"])
        pd, ed = dnum(r["p_date"]), dnum(r["eb_date"])
        r["_pd"], r["_ed"] = pd, ed
        if ed is not None:
            lo, hi = ed - 400, ed + 400
        elif pd is not None:
            lo, hi = pd, pd + 6 * 366
        else:
            lo, hi = dnum("19860101"), dnum("20101231")
        n, why = link_cite(r["eb_cite"], r["circ"], ed, lo, hi, None)
        r["eb_node"], r["eb_reason"] = (str(n) if n is not None else ""), ("eb_" + why if n is None else "cite")

    # ---- panel decisions
    eb_nodes = {int(r["eb_node"]) for r in src if r["eb_node"]}
    edges = load_edges(eb_nodes)
    for r in src:
        r.update({"status": "unlinked", "reason": "", "via": "", "panel_node": "", "confirmed": "0"})
        pd = r["_pd"]
        eb_name = node[int(r["eb_node"])][4] if r["eb_node"] else ""
        if pd is not None:
            lo, hi = pd - 400, pd + 400
        else:
            y = int(r["p_year"]) if r["p_year"].isdigit() else 1986
            lo, hi = dnum("%04d0101" % y) - 400, dnum("%04d1231" % y) + 400
        n, why = link_cite(r["p_cite"], r["circ"], pd, lo, hi, eb_name)
        via = "cite"
        if n is None and why == "no_reporter_cite" and r["eb_node"] and pd is not None:  # rule 2
            en = int(r["eb_node"])
            cands = [m for dd in range(pd - 3, pd + 4) for m in coa_by_date.get(dd, [])
                     if node[m][1] in circ_courts[r["circ"]] and m in edges.get(en, ()) and m != en
                     and toks(node[m][4]) & toks(eb_name)]
            if len(cands) == 1:
                n, via = cands[0], "enbanc_citation"
        if n is None:
            r["reason"] = why if why == "no_reporter_cite" else "panel_" + why
            continue
        if r["eb_node"] and int(r["eb_node"]) == n:
            r["reason"] = "panel_equals_enbanc"
            continue
        if r["eb_node"] and node[int(r["eb_node"])][2] <= node[n][2]:
            r["eb_reason"] = "eb_not_after_panel"
            r["eb_node"] = ""
        r["panel_node"], r["via"], r["status"] = str(n), via, "linked"
        if r["eb_node"] and n in edges.get(int(r["eb_node"]), ()):
            r["confirmed"] = "1"

    # ---- units
    units = collections.OrderedDict()
    for r in src:
        if r["status"] != "linked":
            continue
        u = units.setdefault(r["panel_node"], {"rows": [], "subs": set(), "eb": set(), "eb_conf": set(), "confirmed": "0",
                                               "via": set(), "source": set()})
        u["rows"].append(r["uid"])
        u["subs"].add(r["sub"])
        if r["eb_node"]:
            u["eb"].add(r["eb_node"])
        if r["confirmed"] == "1":
            u["confirmed"] = "1"
            u["eb_conf"].add(r["eb_node"])
        u["via"].add(r["via"])
        u["source"].add(r["source"])
    for r in src:
        r["half"] = benchlib.split_half(DS, "panel:%s" % r["panel_node"]) if r["status"] == "linked" \
            else benchlib.split_half(DS, "bhk:%s" % r["uid"])

    def sub_of(subs):
        return "R" if "R" in subs else ("S" if "S" in subs else "U")

    cols = ["uid", "unique_id_new", "source", "circuit", "p_cite", "p_date", "eb_cite", "eb_date", "eb_reverse", "sub",
            "class", "status", "reason", "via", "panel_node", "panel_repo", "panel_date", "panel_name", "eb_node",
            "eb_reason", "eb_date_corpus", "eb_name", "confirmed", "half"]
    with open(os.path.join(HERE, "key.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for r in src:
            pn = int(r["panel_node"]) if r["panel_node"] else None
            en = int(r["eb_node"]) if r["eb_node"] else None
            r["class"] = "NEG"
            r["panel_repo"] = node[pn][0] if pn is not None else ""
            r["panel_date"] = node[pn][3] if pn is not None else ""
            r["panel_name"] = node[pn][4] if pn is not None else ""
            r["eb_date_corpus"] = node[en][3] if en is not None else ""
            r["eb_name"] = node[en][4] if en is not None else ""
            o.write("\t".join(str(r[c]).replace("\t", " ") or "-" for c in cols) + "\n")

    ucols = ["panel_node", "half", "class", "sub", "confirmed", "eb_nodes", "eb_confirmed", "item_uids", "source", "via", "panel_repo",
             "panel_court", "panel_date", "panel_name"]
    with open(os.path.join(HERE, "key_nodes.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(ucols) + "\n")
        for pn, u in units.items():
            nd = node[int(pn)]
            o.write("\t".join([pn, benchlib.split_half(DS, "panel:%s" % pn), "NEG", sub_of(u["subs"]), u["confirmed"],
                               ";".join(sorted(u["eb"])) or "-", ";".join(sorted(u["eb_conf"])) or "-", ";".join(u["rows"]), ";".join(sorted(u["source"])),
                               ";".join(sorted(u["via"])), nd[0], nd[1], nd[3], nd[4].replace("\t", " ")]) + "\n")

    summ = {
        "items": len(src),
        "linked": sum(r["status"] == "linked" for r in src),
        "fail_reasons": dict(collections.Counter(r["reason"] for r in src if r["status"] != "linked").most_common()),
        "panel_via": dict(collections.Counter(r["via"] for r in src if r["status"] == "linked").most_common()),
        "eb_linked": sum(bool(r["eb_node"]) for r in src),
        "eb_fail_reasons": dict(collections.Counter(r["eb_reason"] for r in src if not r["eb_node"]).most_common()),
        "items_confirmed": sum(r["confirmed"] == "1" for r in src),
        "linked_by_source": {s: "%d/%d" % (sum(r["status"] == "linked" for r in src if r["source"] == s),
                                           sum(r["source"] == s for r in src)) for s in ("bhk_ebs", "clark_ebs")},
        "linked_by_circuit": {str(c): "%d/%d" % (sum(r["status"] == "linked" for r in src if r["circ"] == c),
                                                 sum(r["circ"] == c for r in src)) for c in range(1, 13)},
        "units": len(units),
        "units_confirmed": sum(u["confirmed"] == "1" for u in units.values()),
        "units_with_eb": sum(bool(u["eb"]) for u in units.values()),
        "unit_sub": dict(collections.Counter(sub_of(u["subs"]) for u in units.values()).most_common()),
        "unit_half": dict(collections.Counter(benchlib.split_half(DS, "panel:%s" % p) for p in units)),
        "unit_class": {"NEG": len(units)},
        "generated": benchlib.now(),
    }
    with open(os.path.join(HERE, "link_summary.json"), "w", encoding="utf-8", newline="\n") as o:
        json.dump(summ, o, indent=1)
        o.write("\n")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
