"""Task 2 candidates, wide form (no gold): for every split/conflict question of the reference run, Supreme Court
opinions dated after the earliest side holding that cite the question's US Code section (usc/cites), or cite a
decision on each side (citation edges).  Flags: sub (same subsection cited), e_yes/e_no (side decisions cited).
 -> work/res_cand_wide.tsv: issue, scotus_node, date, same_sub, n_yes_cited, n_no_cited, has_key_row
    python res_candidates2.py <out dir>"""
import os, sys, glob, collections, re
import common as C
out = sys.argv[1]
TAG = os.environ.get("RES_TAG", "")
ONLY = os.environ.get("RES_KEYS", "")   # e.g. ":x" = only keys containing ":x" (the round-2 questions)
iss = C.load_issues()
keys = set()
for fn in ("splits.tsv", "splits_asof.tsv", "conflicts_asof.tsv"):
    for l in open(os.path.join(out, fn), encoding="utf-8"):
        keys.add(l.split("\t", 1)[0])
if ONLY:
    keys = {k for k in keys if ONLY in k}
H = C.load_holdings(pred=lambda f: f[2] in keys and f[4] in ("yes", "no"))
meta = C.node_meta({int(f[1]) for f in H})
cs = C.courts()
sides = collections.defaultdict(lambda: {"yes": set(), "no": set()})
scotus_has = collections.defaultdict(set)
for f in H:
    n = int(f[1]); m = meta[n]
    if C.court_kind(cs.get(m[0])) == "scotus": scotus_has[f[2]].add(n)
    else: sides[f[2]][f[4]].add(n)
side_nodes = collections.defaultdict(set)
for k, s in sides.items():
    for a in ("yes", "no"):
        for n in s[a]: side_nodes[n].add((k, a))
# Supreme Court opinions (scan: opinion text >= 1000 chars)
sc = {}
for l in open(os.path.join(C.C2, "data", "holdings_work", "scotus_scan.tsv"), encoding="utf-8"):
    f = l.rstrip("\n").split("\t")
    if int(f[2]) >= 1000 and f[5] != "memorandum" and int(f[1]) >= 19600000:
        sc[int(f[0])] = int(f[1])
cited = collections.defaultdict(lambda: collections.defaultdict(lambda: {"yes": set(), "no": set()}))
for fn in sorted(glob.glob(os.path.join(C.W, "lean-in-v3", "edges-*.tsv"))):
    with open(fn, encoding="utf-8") as fh:
        for l in fh:
            a, b = l.split("\t")[:2]
            b = int(b)
            if b in side_nodes:
                a = int(a)
                if a in sc:
                    for (k, ans) in side_nodes[b]: cited[a][k][ans].add(b)
by_sec = collections.defaultdict(dict)   # section -> scotus -> set(subs)
for l in open(os.path.join(C.W, "usc", "cites", "supreme-court.usc.tsv"), encoding="utf-8"):
    f = l.rstrip("\n").split("\t")
    n = int(f[0])
    if n in sc:
        by_sec[f[2] + ":" + f[3]].setdefault(n, set()).add(f[4])
rows = []
for k in sorted(keys):
    if not sides[k]["yes"] and not sides[k]["no"]: continue
    first = min(meta[n][1] for a in ("yes", "no") for n in sides[k][a])
    u = iss[k][3]; sec = C.sect(u); sub = re.sub(r"^.*?\((\w+)\).*$", r"\1", u) if "(" in u else ""
    cand = set(by_sec.get(sec, {}))
    cand |= {s for s, d in cited.items() if k in d and (d[k]["yes"] or d[k]["no"])}   # cites a side decision
    for s in sorted(cand):
        if sc[s] <= first: continue
        c = cited.get(s, {}).get(k, {"yes": (), "no": ()})
        rows.append([k, s, sc[s], int(sub in by_sec.get(sec, {}).get(s, ())), len(c["yes"]), len(c["no"]),
                     int(s in scotus_has.get(k, ()))])
with open(os.path.join(C.PRIV, "work", "res_cand_wide%s.tsv" % TAG), "w", encoding="utf-8", newline="\n") as f:
    for r in rows: f.write("\t".join(map(str, r)) + "\n")
import statistics
per = collections.Counter(r[0] for r in rows if not r[6])
print("questions", len(keys), "rows", len(rows), "no key row", sum(1 for r in rows if not r[6]), "same sub", sum(1 for r in rows if r[3] and not r[6]),
      "questions with cand", len(per), "median", statistics.median(per.values()), "max", max(per.values()),
      "distinct scotus", len({r[1] for r in rows}))
print(per.most_common(8))
