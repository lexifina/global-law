"""Conformity probe, tax year given on the command line (default 2025), PolicyEngine-US 2.138.1.
For every state + DC, one batched Simulation of single filers (age 40 unless stated) with variants that change only
one federal item, recording federal income tax, state income tax and state AGI:
  base      wages 60,000
  tips      wages 40,000 + qualified tips 20,000 (Treasury tipped occupation code 1)
  ot        wages 50,000 + FLSA overtime premium 10,000 (+ the same 10,000 in wages: premium is part of pay)
  auto      wages 60,000 + qualified passenger vehicle loan interest 8,000
  senior    age 67, wages 60,000   vs  senior0: age 67 with the federal senior deduction switched off is not
            available as an input, so 'senior' is compared to base and confounded with state age benefits (flagged)
  k401      wages 60,000, 10,000 elective deferral
  hsa       wages 60,000, 4,000 HSA deduction (self-only)
State tax change relative to base tells whether the state base moved with the federal item."""
import sys, json
from policyengine_us import Simulation

STATES = "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY".split()
VARIANTS = {
    "base":   dict(employment_income=60000),
    "tips":   dict(employment_income=60000, tip_income=20000, treasury_tipped_occupation_code=1),
    "ot":     dict(employment_income=60000, fsla_overtime_premium=10000),
    "auto":   dict(employment_income=60000, qualified_passenger_vehicle_loan_interest_person=8000),
    "senior": dict(employment_income=60000, age=67),
    "k401":   dict(employment_income=60000, traditional_401k_contributions=10000),
    "hsa":    dict(employment_income=60000, health_savings_account_ald=4000),
    "base_hi": dict(employment_income=120000),
    "ot_hi":  dict(employment_income=120000, fsla_overtime_premium=10000),
}

TU_VARS = {"health_savings_account_ald"}

def build(year):
    people, tus, hhs, fams, spms, mus = {}, {}, {}, {}, {}, {}
    keys = []
    for st in STATES:
        for v, inp in VARIANTS.items():
            pid = f"{st}_{v}"
            p = {"age": {year: 40}}
            for d in (tus, fams, spms, mus):
                d[pid] = {"members": [pid]}
            for k, val in inp.items():
                (tus[pid] if k in TU_VARS else p)[k] = {year: val}
            people[pid] = p
            hhs[pid] = {"members": [pid], "state_name": {year: st}}
            keys.append((st, v))
    return {"people": people, "tax_units": tus, "families": fams, "spm_units": spms,
            "marital_units": mus, "households": hhs}, keys

if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    sit, keys = build(year)
    s = Simulation(situation=sit)
    fed = s.calculate("income_tax", year)
    st = s.calculate("state_income_tax", year)
    agi = s.calculate("adjusted_gross_income", year)
    ti = s.calculate("taxable_income", year)
    out = {}
    for i, (state, v) in enumerate(keys):
        out.setdefault(state, {})[v] = dict(fed=round(float(fed[i])), state=round(float(st[i])),
                                            agi=round(float(agi[i])), ti=round(float(ti[i])))
    json.dump(out, open(f"probe_{year}.json", "w"), indent=1)
    print("state  " + "  ".join(f"{v:>14}" for v in VARIANTS if v != "base") + "   (state tax change vs base; federal change in brackets)")
    for state in STATES:
        b = out[state]["base"]
        cells = []
        for v in VARIANTS:
            if v in ("base", "base_hi"):
                continue
            r = out[state][v]
            b = out[state]["base_hi" if v.endswith("_hi") else "base"]
            cells.append(f"{r['state'] - b['state']:>6}[{r['fed'] - b['fed']:>6}]")
        print(f"{state:5} base {b['state']:>5}  " + "  ".join(cells))
