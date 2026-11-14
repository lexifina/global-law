"""Count v3 treatments rows refused noAuthority, by acting court / target court / decade / bench / court size.

    python -X utf8 noauth.py
No answer-key file is read.
"""
import collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common8 import STAGE, OUT  # noqa: E402

ver = {}
for line in open(os.path.join(OUT, "certs.tsv"), encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if p[0] == "treatment":
        ver[p[1]] = p[2]
need = collections.defaultdict(list)
rows = []
for line in open(os.path.join(STAGE, "treatments.tsv"), encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if ver.get(p[0]) == "noAuthority":
        rows.append(p)
nodes = set()
for p in rows:
    nodes.add(int(p[1]))
    nodes.add(int(p[2]))
dec = {}
for line in open(os.path.join(STAGE, "decisions2.tsv"), encoding="utf-8"):
    p = line.split("\t", 6)
    n = int(p[0])
    if n in nodes:
        dec[n] = (int(p[1]), int(p[2]), p[4])
name = {}
for line in open(os.path.join(STAGE, "courts2.tsv"), encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    name[int(p[0])] = (p[3], p[5], p[4])
size = collections.defaultdict(list)
for line in open(os.path.join(STAGE, "court_size.tsv"), encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    size[int(p[0])].append((int(p[1]), int(p[2]), int(p[3])))


def csize(c, d):
    for a, b, k in size.get(c, []):
        if a <= d <= b:
            return k
    return None


cnt = collections.Counter()
for p in rows:
    b, x = int(p[1]), int(p[2])
    bc, bd, bb = dec.get(b, (None, 0, "?"))
    xc, xd, xb = dec.get(x, (None, 0, "?"))
    same = "same" if bc == xc else "other"
    rel = "%s(%s)->%s(%s)" % (name.get(bc, ("?",))[0][:40], name.get(bc, ("", "?"))[1], name.get(xc, ("?",))[0][:40],
                               name.get(xc, ("", "?"))[1])
    cnt[(rel, same, bb, csize(bc, bd) if same == "same" else "-")] += 1
for k, v in cnt.most_common(45):
    print(v, *k, sep="\t")
print("total", len(rows))
