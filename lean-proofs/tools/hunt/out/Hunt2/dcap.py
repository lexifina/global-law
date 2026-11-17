"""2026: employer dependent-care benefits (sec. 129, $7,500 from 2026) versus the sec. 21 credit (50%..35%..20% from
2026, Pub. L. 119-21 sec. 70405), across 51 jurisdictions, PolicyEngine-US 2.138.1. Married, two children (3 and 6),
$14,000 of care, wages split 60/40. Move: take $7,500 through the employer plan (wages reduced by the same amount)
or not. Report federal and state change and flag where the federal and state answers point different ways.
Objective counts income tax only (the sec. 129 exclusion also saves FICA 7.65% of $7,500 = $574, reported apart)."""
import json
from policyengine_us import Simulation
STATES = "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split()
Y = 2026
def sit_for(fsa):
    sit = {k: {} for k in ("people", "tax_units", "families", "spm_units", "marital_units", "households")}
    keys = []
    for st in STATES:
        for agi in (40000, 80000, 150000, 250000):
            cid = f"{st}_{agi}"
            a, b, c1, c2 = cid + "a", cid + "b", cid + "c1", cid + "c2"
            sit["people"].update({
                a: {"age": {Y: 35}, "employment_income": {Y: agi * 0.6 - fsa}, "dependent_care_employer_benefits": {Y: fsa}},
                b: {"age": {Y: 35}, "employment_income": {Y: agi * 0.4}},
                c1: {"age": {Y: 3}}, c2: {"age": {Y: 6}}})
            m = [a, b, c1, c2]
            sit["tax_units"][cid] = {"members": m, "tax_unit_childcare_expenses": {Y: 14000}, "dependent_care_assistance_exclusion": {Y: fsa}}
            sit["families"][cid] = {"members": m}; sit["spm_units"][cid] = {"members": m}
            sit["marital_units"][cid] = {"members": [a, b]}
            sit["marital_units"][cid + "k1"] = {"members": [c1]}; sit["marital_units"][cid + "k2"] = {"members": [c2]}
            sit["households"][cid] = {"members": m, "state_name": {Y: st}}
            keys.append((st, agi))
    return sit, keys
res = {}
for fsa in (0, 7500):
    sit, keys = sit_for(fsa)
    s = Simulation(situation=sit)
    fed = s.calculate("income_tax", Y); st = s.calculate("state_income_tax", Y); cd = s.calculate("cdcc", Y)
    for i, k in enumerate(keys):
        res.setdefault(k, {})[fsa] = (float(fed[i]), float(st[i]), float(cd[i]))
rows = []
for (st, agi), r in res.items():
    df = r[7500][0] - r[0][0]; ds = r[7500][1] - r[0][1]
    rows.append(dict(state=st, agi=agi, dfed=round(df), dstate=round(ds), cdcc0=round(r[0][2]), cdcc1=round(r[7500][2])))
json.dump(rows, open("dcap_2026.json", "w"), indent=0)
print("employer plan vs credit, change in tax from taking the $7,500 employer plan (negative = plan better)")
for r in rows:
    flag = " <-- federal and state disagree" if (r["dfed"] < 0) != (r["dstate"] < 0) and r["dstate"] != 0 and r["dfed"] != 0 else ""
    if flag or r["state"] in ("NY", "CA", "TX"):
        print(r, flag)
