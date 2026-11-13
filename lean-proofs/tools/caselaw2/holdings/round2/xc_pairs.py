"""Cross-circuit disagreement pairs from the reader's treatments.tsv (no gold): by and target are federal courts of
appeals of different circuits and the kind is a disagreement. -> work/xc_pairs.tsv"""
import os, collections
import common as C
cs = C.courts()
T = [l.rstrip("\n").split("\t") for l in open(os.path.join(C.DATA, "treatments.tsv"), encoding="utf-8")]
meta = C.node_meta({int(t[1]) for t in T} | {int(t[2]) for t in T})
cnt = collections.Counter(); out = []
for t in T:
    a, b = meta.get(int(t[1])), meta.get(int(t[2]))
    if not a or not b: continue
    ca, cb = cs.get(a[0]), cs.get(b[0])
    if C.court_kind(ca) == "coa" and C.court_kind(cb) == "coa" and ca[2] != cb[2]:
        cnt[t[4]] += 1
        if t[4] in ("declinedToFollow", "disapproved", "criticized", "questioned", "overruled", "abrogated", "limited"):
            out.append(t + [str(ca[2]), str(cb[2]), str(a[1]), str(b[1]), a[2], b[2]])
print(cnt, len(out))
dec = collections.Counter((int(o[-4]) // 100000) * 10 for o in out); print(sorted(dec.items()))
os.makedirs(os.path.join(C.PRIV, "work"), exist_ok=True)
with open(os.path.join(C.PRIV, "work", "xc_pairs.tsv"), "w", encoding="utf-8", newline="\n") as f:
    for o in out: f.write("\t".join(o) + "\n")
