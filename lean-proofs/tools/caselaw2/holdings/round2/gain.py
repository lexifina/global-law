"""Measure only: where the section-level recall gain comes from, and a stricter node-level measure
(a split question, first split before the resolution, that has a holding of one of the gold row's conflict decisions).
    python gain.py <out before> <data before> <out after> <data after>"""
import sys, os, collections, json
import common as C
o0, d0, o1, d1 = sys.argv[1:5]
gold = []; hdr = None
for l in open(os.path.join(C.C2, "gold", "splits_resolved.tsv"), encoding="utf-8"):
    f = l.rstrip("\n").split("\t")
    if hdr is None: hdr = f; continue
    r = dict(zip(hdr, f))
    if r["statutory"] == "1": gold.append(r)
def verdicts(o):
    v = {}
    for l in open(os.path.join(o, "splits_recall_splits.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t"); v[(f[0], f[2])] = f[4]
    return v
v0, v1 = verdicts(o0), verdicts(o1)
newly = collections.Counter(); 
for g in gold:
    k = (g["node"], g["usc"])
    if v0.get(k) == "missed" and v1.get(k) != "missed": newly[C.sect(g["usc"])] += 1
print("gold rows newly found:", sum(newly.values()), "over", len(newly), "sections; top:", newly.most_common(12))
def node_level(o, d):
    iss = C.load_issues(d)
    first = {}
    for l in open(os.path.join(o, "splits.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t"); first[f[0]] = min(first.get(f[0], 99999999), int(f[5]))
    nodes_of = collections.defaultdict(set)
    for f in C.load_holdings(d, lambda f: f[2] in first): nodes_of[f[2]].add(int(f[1]))
    hit = tot = hit_sec = 0
    for g in gold:
        cn = {int(x) for x in g["conflict_nodes"].split(",") if x.isdigit()}
        if not cn: continue
        tot += 1
        ok = any(first[k] < int(g["date"]) and (nodes_of[k] & cn) for k in first)
        hit += ok
    return hit, tot
print("node-level before", node_level(o0, d0), "after", node_level(o1, d1))
