"""diagnosis (h0-only file): rows' targets vs v11d h0 per-case classes, per rule class; new = pair not in v11d."""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h0check
H = h0check.h0()
C2 = h0check.C2
old = set()
for line in open(os.path.join(C2, "round11/stage/v11d/history.tsv"), encoding="utf-8"):
    p = line.split("\t", 3); old.add((int(p[2]), int(p[1])))
c = collections.Counter()
for f in sys.argv[1:]:
    for l in open(f, encoding="utf-8"):
        r = json.loads(l)
        if (r["by"], r["target"]) in old:
            c[(r["rule"], "old_pair")] += 1; continue
        h = H.get(r["target"])
        k = "not_h0" if h is None else "%s/%s model %s" % (h["class"], h["sub"], h["model_class"])
        c[(r["rule"], k)] += 1
for k, v in sorted(c.items()):
    print(v, *k)
