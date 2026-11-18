"""Run PolicyEngine-UK on canonical households with the same mapping as lean/UkTax/Household.lean.
usage: venv-pe/bin/python -I pe_run.py in.jsonl out.jsonl [batch]"""
import json, sys, time
from policyengine_uk import Simulation

Y = "2025"

def share1(x): return x - x // 2
def share2(x): return x // 2

def persons_of(h):
    """Mirror of UkTax.persons (Household.lean)."""
    ad = h["adults"]
    g = lambda k: h.get(k, 0) or 0
    if len(ad) == 1:
        a = ad[0]
        return [dict(age=a["age"], blind=a.get("blind", False), employment=a.get("wages", 0), trading=a.get("selfEmployment", 0),
                     pension=a.get("pension", 0), property=g("rentalIncome"), interest=g("interest"), dividends=g("dividends"),
                     gains=g("capitalGains"), giftAid=g("charitable"), rasGross=g("pensionContributions"))]
    a, b = ad
    def base(x, k):
        return dict(age=x["age"], blind=x.get("blind", False), employment=x.get("wages", 0), trading=x.get("selfEmployment", 0),
                    pension=x.get("pension", 0), property=k(g("rentalIncome")), interest=k(g("interest")),
                    dividends=k(g("dividends")), gains=k(g("capitalGains")))
    pa, pb = base(a, share1), base(b, share2)
    tot = lambda p: max(0, p["employment"] + p["trading"] + p["pension"] + p["property"]) + max(0, p["interest"]) + max(0, p["dividends"])
    a_gives = tot(pa) >= tot(pb)
    ea = max(0, a.get("wages", 0) + a.get("selfEmployment", 0)); eb = max(0, b.get("wages", 0) + b.get("selfEmployment", 0))
    pc = g("pensionContributions")
    ca = (pc * ea // (ea + eb)) if ea + eb > 0 else share1(pc)
    pa.update(giftAid=g("charitable") if a_gives else 0, rasGross=ca)
    pb.update(giftAid=0 if a_gives else g("charitable"), rasGross=pc - ca)
    return [pa, pb]

def situation(hs):
    people, benunits, households = {}, {}, {}
    index = []
    for hi, h in enumerate(hs):
        ps = persons_of(h)
        names = []
        for k, p in enumerate(ps):
            nm = f"h{hi}a{k}"
            names.append(nm)
            people[nm] = {
                "age": {Y: p["age"]},
                "employment_income": {Y: p["employment"]},
                "self_employment_income": {Y: p["trading"]},
                "private_pension_income": {Y: p["pension"]},
                "property_income": {Y: p["property"]},
                "savings_interest_income": {Y: p["interest"]},
                "dividend_income": {Y: p["dividends"]},
                "capital_gains": {Y: p["gains"]},
                "gift_aid": {Y: p["giftAid"]},
                "personal_pension_contributions": {Y: p["rasGross"]},
                "trading_allowance_deduction": {Y: 0},
                "property_allowance_deduction": {Y: 0},
                "is_blind": {Y: bool(p.get("blind", False))},
                "is_claimant_or_partner": {Y: True},
            }
        kids = []
        for c, ch in enumerate(h.get("children", [])):
            nm = f"h{hi}c{c}"
            kids.append(nm)
            d = {"age": {Y: ch["age"]}, "is_claimant_or_partner": {Y: False}}
            if 16 <= ch["age"] < 20:
                d["meets_qualifying_young_person_education_or_training_condition_for_child_benefit"] = {Y: True}
                d["meets_qualifying_young_person_entry_condition_for_child_benefit"] = {Y: True}
            people[nm] = d
        bu = {"members": names + kids}
        if len(names) == 2:
            bu["is_married"] = {Y: bool(h.get("married", False))}
        benunits[f"b{hi}"] = bu
        households[f"hh{hi}"] = {"members": names + kids}
        if str(h.get("region", "")).lower() == "scotland":
            households[f"hh{hi}"]["region"] = {Y: "SCOTLAND"}
        index.append((h["id"], names))
    return {"people": people, "benunits": benunits, "households": households}, index

PERSON_VARS = ["income_tax", "income_tax_before_winter_fuel_payment_charge", "winter_fuel_payment_charge",
               "CB_HITC", "personal_pension_contributions_tax", "adjusted_net_income", "net_income", "personal_allowance", "marriage_allowance",
               "marriage_allowance_tax_reduction", "capital_gains_tax", "ni_class_1_employee", "ni_class_2",
               "ni_class_4", "national_insurance", "savings_allowance", "income_tax_pre_charges",
               "income_tax_reductions", "income_tax_charges", "pension_contributions_relief",
               "gift_aid_grossed_up", "received_allowances_savings_income", "received_allowances_dividend_income"]

def run(hs):
    sit, index = situation(hs)
    sim = Simulation(situation=sit)
    pv = {}
    for v in PERSON_VARS:
        try:
            pv[v] = dict(zip(sit["people"].keys(), sim.calculate(v, 2025)))
        except Exception as e:
            pv[v] = {}
            print("var failed", v, e, file=sys.stderr)
    cb = dict(zip(sit["benunits"].keys(), sim.calculate("child_benefit", 2025)))
    out = []
    for hi, (hid, names) in enumerate(index):
        out.append({"id": hid, "childBenefit": float(cb[f"b{hi}"]),
                    "persons": [{v: float(pv[v].get(nm, float('nan'))) for v in PERSON_VARS} for nm in names]})
    return out

if __name__ == "__main__":
    inp, outp = sys.argv[1], sys.argv[2]
    batch = int(sys.argv[3]) if len(sys.argv) > 3 else 250
    hs = [json.loads(l) for l in open(inp) if l.strip()]
    t0 = time.time()
    with open(outp, "w") as f:
        for i in range(0, len(hs), batch):
            for o in run(hs[i:i + batch]):
                f.write(json.dumps(o) + "\n")
            print(f"{min(i + batch, len(hs))}/{len(hs)} {time.time() - t0:.1f}s", file=sys.stderr, flush=True)
