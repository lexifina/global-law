"""Compare jptax and referee A on whole contract outputs (all fields, separate taxes included).
usage: python3 compare_full.py households.jsonl lean_out.jsonl ref_out.jsonl"""
import sys, json
from collections import Counter

hs = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
lo = [json.loads(l) for l in open(sys.argv[2]) if l.strip()]
ro = [json.loads(l) for l in open(sys.argv[3]) if l.strip()]
eq = Counter()
ex = {}
keys = ["incomeTax", "fukko", "localIncomeTax", "employeeSocial", "benefits"]
allok = 0
for h, a, b in zip(hs, lo, ro):
    ok = True
    for k in keys:
        x = a["surtaxes"]["復興特別所得税"] if k == "fukko" else a[k]
        y = b["surtaxes"]["復興特別所得税"] if k == "fukko" else b[k]
        if x == y:
            eq[k] += 1
        else:
            ok = False
            ex.setdefault(k, []).append((h["id"], x, y, x - y))
    allok += ok
print("households", len(hs), "all equal", allok)
for k in keys:
    print("  %-15s %d" % (k, eq[k]))
for k, l in ex.items():
    print("==", k, len(l), Counter(d[3] for d in l).most_common(6), l[:5])
