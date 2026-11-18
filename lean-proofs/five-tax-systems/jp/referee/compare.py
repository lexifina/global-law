"""Compare jptax (Lean) outputs with referee A outputs, field by field.
usage: python3 compare.py households.jsonl lean_out.jsonl ref_out.jsonl [max_examples]"""
import sys, json
from collections import Counter, defaultdict

hs = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
lo = [json.loads(l) for l in open(sys.argv[2]) if l.strip()]
ro = [json.loads(l) for l in open(sys.argv[3]) if l.strip()]
maxex = int(sys.argv[4]) if len(sys.argv) > 4 else 5
assert len(hs) == len(lo) == len(ro)


def lean_fields(o):
    sep = o["detail"]["separateTaxation"]
    return {"incomeTax": o["incomeTax"] - sep["national15pct"],
            "fukko": o["surtaxes"]["復興特別所得税"] - sep["reconstruction0315pct"],
            "local": o["localIncomeTax"] - sep["local5pct"],
            "social": o["employeeSocial"], "benefits": o["benefits"]}


def ref_fields(o):
    return {"incomeTax": o["incomeTax"], "fukko": o["surtaxes"]["復興特別所得税"], "local": o["localIncomeTax"],
            "social": o["employeeSocial"], "benefits": o["benefits"]}


agree = Counter()
diffs = defaultdict(list)
allok = 0
for h, a, b in zip(hs, lo, ro):
    fa, fb = lean_fields(a), ref_fields(b)
    ok = True
    for k in fa:
        if fa[k] == fb[k]:
            agree[k] += 1
        else:
            ok = False
            diffs[k].append((h["id"], fa[k], fb[k], fa[k] - fb[k]))
    allok += ok
print("households:", len(hs), " all fields equal:", allok)
for k in ["incomeTax", "fukko", "local", "social", "benefits"]:
    print("  %-10s equal %d / %d" % (k, agree[k], len(hs)))
for k, lst in diffs.items():
    print("\n== %s: %d differences; (lean - referee) distribution:" % (k, len(lst)), Counter(d[3] for d in lst).most_common(8))
    for d in lst[:maxex]:
        print("  ", d)
