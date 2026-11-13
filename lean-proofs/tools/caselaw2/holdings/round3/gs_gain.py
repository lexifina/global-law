"""Measure only (reads gold): where the round-3 section-level gain comes from.
    python gs_gain.py <out before> <out after> <data after>
Needs splits_recall_splits.tsv in both out dirs (round2/score_splits.py). A newly found gold row is
  honest_opposite: its conflict decisions are on both sides of one split question dated before the resolution;
  honest_any:      one of its conflict decisions is a holding on such a question;
  coincidental:    otherwise (same section, another question, or the gold row names no conflict decision)."""
import collections, json, os, re, sys
HT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HT)
import text
C2 = os.path.join(text.WORK, "caselaw-lean-2")
o0, o1, d1 = sys.argv[1:4]


def sect(u):
    return re.sub(r"\(.*$", "", u or "-")


def verdicts(o):
    v = {}
    for l in open(os.path.join(o, "splits_recall_splits.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        v[(f[0], f[2])] = f[4]
    return v


gold, hdr = [], None
for l in open(os.path.join(C2, "gold", "splits_resolved.tsv"), encoding="utf-8"):
    f = l.rstrip("\n").split("\t")
    if hdr is None:
        hdr = f
        continue
    r = dict(zip(hdr, f))
    if r["statutory"] == "1":
        gold.append(r)
v0, v1 = verdicts(o0), verdicts(o1)
first, usc = {}, {}
for l in open(os.path.join(o1, "splits.tsv"), encoding="utf-8"):
    f = l.rstrip("\n").split("\t")
    first[f[0]] = min(first.get(f[0], 99999999), int(f[5]))
by = collections.defaultdict(lambda: collections.defaultdict(set))
for l in open(os.path.join(d1, "holdings.tsv"), encoding="utf-8"):
    f = l.split("\t", 5)
    if f[2] in first and f[4] in ("yes", "no"):
        by[f[2]][f[4]].add(int(f[1]))
target = collections.Counter()
for l in open(os.path.join(C2, "work", "round3", "splits", "w", "sections.tsv"), encoding="utf-8"):
    f = l.rstrip("\n").split("\t")
    if f[0] != "section":
        target[f[0]] = int(f[5])
res = collections.Counter()
rows = []
for g in gold:
    k = (g["node"], g["usc"])
    if not (v0.get(k) == "missed" and v1.get(k) != "missed"):
        continue
    cn = {int(x) for x in g["conflict_nodes"].split(",") if x.isdigit()}
    d = int(g["date"])
    ks = [q for q in by if first[q] < d]
    opp = [q for q in ks if (by[q]["yes"] & cn) and (by[q]["no"] & cn)]
    anyq = [q for q in ks if (by[q]["yes"] | by[q]["no"]) & cn]
    cls = "honest_opposite" if opp else "honest_any" if anyq else "coincidental" if cn else "coincidental_no_conflict_nodes"
    res[cls] += 1
    res["newly_found"] += 1
    res["on_round3_target_section"] += sect(g["usc"]) in target
    rows.append([g["node"], g["date"], g["name"], g["usc"], v1[k], cls, ",".join(opp or anyq)])
with open(os.path.join(o1, "gain_rows.tsv"), "w", encoding="utf-8", newline="\n") as f:
    for r in rows:
        f.write("\t".join(r) + "\n")
print(json.dumps(dict(res), indent=1))
