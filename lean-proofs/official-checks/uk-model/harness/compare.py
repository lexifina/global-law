"""Compare uktax (Lean) with PolicyEngine-UK on the same canonical households.
usage: python3 -I compare.py in.jsonl lean_out.jsonl pe_out.jsonl report.json [tol]"""
import json, sys, collections

def load(p): return [json.loads(l) for l in open(p) if l.strip()]

def features(h, lo):
    f = []
    ad = h["adults"]
    f.append(f"adults{len(ad)}")
    if len(ad) == 2 and h.get("married"): f.append("married")
    if h.get("children"): f.append("kids")
    if any(a.get("selfEmployment", 0) for a in ad): f.append("se")
    if any(a.get("pension", 0) for a in ad): f.append("pension")
    if any(a["age"] >= 66 for a in ad): f.append("spa")
    for k in ["interest", "dividends", "capitalGains", "rentalIncome", "charitable", "pensionContributions"]:
        if h.get(k, 0): f.append(k)
    el = lo["detail"]["election"]
    if el != "none": f.append("elect:" + el)
    if lo["detail"]["hicbc"]: f.append("hicbc")
    return f

def main():
    ins, lean, pe = load(sys.argv[1]), load(sys.argv[2]), load(sys.argv[3])
    tol = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    assert len(ins) == len(lean) == len(pe)
    fields = ["incomeTax", "employeeSocial", "cgt", "childBenefit", "hicbc"]
    ok = collections.Counter(); bad = collections.defaultdict(list)
    for h, lo, po in zip(ins, lean, pe):
        assert h["id"] == lo["id"] == po["id"]
        P = po["persons"]
        pe_vals = {
            "incomeTax": sum(p["income_tax_before_winter_fuel_payment_charge"] - p["CB_HITC"] - p["personal_pension_contributions_tax"] for p in P),
            "employeeSocial": sum(p["national_insurance"] for p in P),
            "cgt": sum(p["capital_gains_tax"] for p in P),
            "childBenefit": po["childBenefit"],
            "hicbc": sum(p["CB_HITC"] for p in P),
        }
        d = lo["detail"]
        lean_vals = {"incomeTax": lo["incomeTax"], "employeeSocial": lo["employeeSocial"],
                     "cgt": lo["surtaxes"].get("capitalGainsTax", 0), "childBenefit": d["childBenefit"], "hicbc": d["hicbc"]}
        for f in fields:
            diff = lean_vals[f] - pe_vals[f]
            if abs(diff) <= tol: ok[f] += 1
            else:
                bad[f].append({"id": h["id"], "lean": lean_vals[f], "pe": round(pe_vals[f], 2), "diff": round(diff, 2),
                               "features": features(h, lo)})
        if all(abs(lean_vals[f] - pe_vals[f]) <= tol for f in fields): ok["all"] += 1
    n = len(ins)
    summary = {"n": n, "tol": tol, "match": {f: ok[f] for f in fields + ["all"]},
               "mismatch": {f: len(bad[f]) for f in fields}}
    # feature profile of mismatches
    prof = {}
    for f in fields:
        c = collections.Counter(x for b in bad[f] for x in b["features"])
        prof[f] = c.most_common(20)
    summary["mismatchFeatures"] = prof
    json.dump({"summary": summary, "mismatches": bad}, open(sys.argv[4], "w"), indent=1)
    print(json.dumps(summary, indent=1))

main()
