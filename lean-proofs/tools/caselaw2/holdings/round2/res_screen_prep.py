"""Lexical score for wide candidates: IDF-weighted overlap of the split question (+label) with the Supreme Court
decision's recorded holdings (propositions; questions of its split holdings). -> work/res_cand_scored.tsv"""
import os, re, math, collections
import common as C
iss = C.load_issues()
TAG = os.environ.get("RES_TAG", "")
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(C.PRIV, "work", "res_cand_wide%s.tsv" % TAG), encoding="utf-8")]
rows = [r for r in rows if r[6] == "0"]
scn = {int(r[1]) for r in rows}
doc = collections.defaultdict(list)
for f in C.load_holdings(pred=lambda f: int(f[1]) in scn):
    doc[int(f[1])].append(f[3] + " " + (iss[f[2]][4] if iss[f[2]][4] != "-" else iss[f[2]][1]))
STOP = set("the a an of to in for and or is are be does do did under that which this with by on as at it its from not any may can whether when section usc u s c court courts statute act".split())
def toks(s):
    return {w for w in re.findall(r"[a-z][a-z\-']{2,}", s.lower()) if w not in STOP}
dtok = {n: toks(" ".join(v)) for n, v in doc.items()}
df = collections.Counter(w for t in dtok.values() for w in t)
N = len(dtok) or 1
def idf(w): return math.log((N + 1) / (df.get(w, 0) + 1))
out = []
for r in rows:
    k, n = r[0], int(r[1])
    q = toks(iss[k][4] + " " + iss[k][1])
    d = dtok.get(n, set())
    num = sum(idf(w) for w in q & d); den = sum(idf(w) for w in q) or 1
    out.append(r + ["%.3f" % (num / den), str(len(doc.get(n, ())))])
with open(os.path.join(C.PRIV, "work", "res_cand_scored%s.tsv" % TAG), "w", encoding="utf-8", newline="\n") as f:
    for o in out: f.write("\t".join(o) + "\n")
import statistics
sc = [float(o[7]) for o in out]
for thr in (0.1, 0.15, 0.2, 0.25, 0.3, 0.4):
    print(thr, sum(1 for o in out if float(o[7]) >= thr), sum(1 for o in out if float(o[7]) >= thr or o[3] == "1" or int(o[4]) + int(o[5]) > 0))
print("nohold", sum(1 for o in out if o[8] == "0"))
for o in out:
    if o[1] in ("6323676", "6239495"): print(o)
