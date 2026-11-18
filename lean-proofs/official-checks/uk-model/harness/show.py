"""Show one household side by side: canonical input, Lean per-person detail, PE per-person values.
usage: python3 -I show.py base id   (base = runs/<name> without .jsonl)"""
import json, sys
base, hid = sys.argv[1], sys.argv[2]
def find(p):
    for l in open(p):
        d = json.loads(l)
        if d["id"] == hid: return d
h = find(base + ".jsonl"); lo = find(base + ".lean.jsonl"); po = find(base + ".pe.jsonl")
print("IN ", json.dumps(h))
print("LEAN", {k: lo[k] for k in ["incomeTax", "surtaxes", "employeeSocial", "benefits"]}, "election:", lo["detail"]["election"],
      "liab", lo["detail"]["liabilityITA2007s23"], "ras", lo["detail"]["reliefAtSource"], "CB", lo["detail"]["childBenefit"], "hicbc", lo["detail"]["hicbc"])
print("PE  CB", round(po["childBenefit"], 2))
keys = ["totalIncome", "netIncome", "adjustedNetIncome", "personalAllowance", "step3Income", "basicRateLimit", "taxAtStep5",
        "marriageAllowanceReduction", "marriedCouplesAllowanceReduction", "giftAidCharge", "liability", "reliefAtSource",
        "capitalGainsTax", "class1", "class4"]
for i, (lp, pp) in enumerate(zip(lo["detail"]["persons"], po["persons"])):
    print(f"-- person {i+1}")
    print("  lean", {k: lp[k] for k in keys})
    print("  lean charged", {k: v for k, v in lp["charged"].items() if v})
    print("  pe  ", {k: round(v, 2) for k, v in pp.items() if v and v == v})
