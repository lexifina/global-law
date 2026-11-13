"""Task 2 candidates (no gold): for every split/conflict question of the reference run, Supreme Court decisions after
the earliest side that cite a decision on each side (class both), or one side and the question's US Code section
(class side+usc).  -> work/res_candidates.tsv: issue, scotus_node, scotus_date, class, n_yes_cited, n_no_cited, has_key_row
    python res_candidates.py <out dir>"""
import os, sys, glob, collections
import common as C
out = sys.argv[1]
iss = C.load_issues()
keys = set()
for fn in ("splits.tsv", "splits_asof.tsv", "conflicts_asof.tsv"):
    for l in open(os.path.join(out, fn), encoding="utf-8"):
        keys.add(l.split("\t", 1)[0])
H = C.load_holdings(pred=lambda f: f[2] in keys and f[4] in ("yes", "no"))
meta = C.node_meta({int(f[1]) for f in H})
cs = C.courts()
sides = collections.defaultdict(lambda: {"yes": set(), "no": set()})
scotus_has = collections.defaultdict(set)
for f in H:
    n = int(f[1]); m = meta[n]
    if C.court_kind(cs.get(m[0])) == "scotus":
        scotus_has[f[2]].add(n)
    else:
        sides[f[2]][f[4]].add(n)
side_nodes = collections.defaultdict(set)   # node -> {(issue, answer)}
for k, s in sides.items():
    for a in ("yes", "no"):
        for n in s[a]: side_nodes[n].add((k, a))
# scotus nodes + dates
sc = {}
with open(os.path.join(C.W, "graph", "nodes.tsv"), encoding="utf-8") as fh:
    for l in fh:
        f = l.split("\t", 5)
        if f[1] == "supreme-court":
            sc[int(f[0])] = int(f[4])
print("questions", len(keys), "side nodes", len(side_nodes), "scotus nodes", len(sc))
cited = collections.defaultdict(lambda: collections.defaultdict(lambda: {"yes": set(), "no": set()}))  # scotus -> issue -> side -> nodes
for fn in sorted(glob.glob(os.path.join(C.W, "lean-in-v3", "edges-*.tsv"))):
    with open(fn, encoding="utf-8") as fh:
        for l in fh:
            a, b = l.split("\t")[:2]
            b = int(b)
            if b in side_nodes:
                a = int(a)
                if a in sc:
                    for (k, ans) in side_nodes[b]:
                        cited[a][k][ans].add(b)
# usc sections cited by scotus
usc = collections.defaultdict(set)
for l in open(os.path.join(C.W, "usc", "cites", "supreme-court.usc.tsv"), encoding="utf-8"):
    f = l.rstrip("\n").split("\t")
    usc[int(f[0])].add(f[2] + ":" + f[3])
rows = []; cnt = collections.Counter()
for s, d in cited.items():
    for k, c in d.items():
        first = min(meta[n][1] for a in ("yes", "no") for n in sides[k][a])
        if sc[s] <= first: continue
        sec = C.sect(iss[k][3])
        if c["yes"] and c["no"]: cls = "both"
        elif sec in usc.get(s, ()): cls = "side+usc"
        else: continue
        has = s in scotus_has.get(k, ())
        cnt[(cls, has)] += 1
        rows.append([k, s, sc[s], cls, len(c["yes"]), len(c["no"]), int(has),
                     ",".join(map(str, sorted(c["yes"]))), ",".join(map(str, sorted(c["no"])))])
rows.sort()
with open(os.path.join(C.PRIV, "work", "res_candidates.tsv"), "w", encoding="utf-8", newline="\n") as f:
    for r in rows: f.write("\t".join(map(str, r)) + "\n")
print(cnt, "rows", len(rows), "questions with a candidate", len({r[0] for r in rows}), "scotus", len({r[1] for r in rows}))
