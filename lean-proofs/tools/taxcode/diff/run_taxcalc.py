"""Run Tax-Calculator (Policy Simulation Library) on the households, tax year 2025, current-law policy.

    <refs-venv python> run_taxcalc.py households.json tc.json
"""
import json, sys
import pandas as pd
import taxcalc as tc

hs = json.load(open(sys.argv[1], encoding="utf-8"))
rows = []
for i, h in enumerate(hs):
    deps = h["dependents"]
    mars = {"single": 1, "mfj": 2, "mfs": 3, "hoh": 4, "qss": 5}[h["filing"]]
    eic = sum(1 for d in deps if d["age"] < 19 or (d.get("student") and d["age"] < 24))
    rows.append(dict(
        RECID=i + 1, MARS=mars,
         XTOT=(2 if h["spouse"] else 1) + len(deps), FLPDYR=2025,
        age_head=h["head"]["age"], age_spouse=(h["spouse"]["age"] if h["spouse"] else 0),
        n24=sum(1 for d in deps if d["age"] < 17), nu18=sum(1 for d in deps if d["age"] < 18),
        nu06=sum(1 for d in deps if d["age"] < 6), nu13=sum(1 for d in deps if d["age"] < 13),
        EIC=min(3, eic), f2441=min(2, sum(1 for d in deps if d["age"] < 13)),
        e00200=h["wages"], e00200p=h["wages"] - h["wagesSpouse"], e00200s=h["wagesSpouse"],
        e00900=h["seIncome"], e00900p=h["seIncome"], e00300=h["taxableInterest"],
        e00600=h["ordinaryDividends"], e00650=h["qualifiedDividends"], p23250=h["longTermGains"],
        p22250=h["shortTermGains"], e01500=h["pensions"], e01700=h["pensions"], e02400=h["socialSecurity"],
        e02300=h["unemployment"], e18500=h["stateLocalTaxes"], e19200=h["mortgageInterest"],
        blind_head=int(h["head"].get("blind", False)), blind_spouse=int(bool(h["spouse"] and h["spouse"].get("blind"))),
        tip_income=h["qualifiedTips"], overtime_income=h["qualifiedOvertime"], auto_loan_interest=h["carLoanInterest"],
        e03150=h["iraContributions"], e03210=h["studentLoanInterest"], e03220=h["educatorExpenses"],
        e03290=h["hsaContributions"], e00400=h["taxExemptInterest"],
        e19800=h["charitableCash"], e17500=h["medicalExpenses"], e32800=h["childCareExpenses"]))
df = pd.DataFrame(rows)
# exact_calculations: the forms' "$1,000 or fraction thereof" steps rather than smooth phase-outs
recs = tc.Records(data=df, start_year=2025, gfactors=None, weights=None, adjust_ratios=None, exact_calculations=True)
pol = tc.Policy()
# Tax-Calculator simulates EITC and ACTC non-take-up with a random draw; a scale of 9e99 means everyone claims.
pol.implement_reform({"eitc_claim_prob_scale": {2025: 9e99}, "actc_claim_prob_scale": {2025: 9e99}})
calc = tc.Calculator(policy=pol, records=recs)
calc.advance_to_year(2025) if calc.current_year != 2025 else None
calc.calc_all()
cols = ["c00100", "c04800", "taxbc", "eitc", "c07220", "c11070", "c32800", "c07180", "iitax", "setax", "c09600", "niit",
        "standard", "c04470", "c02500", "odc", "qbided", "c07100"]
out = calc.dataframe(cols).to_dict(orient="records")
json.dump(out, open(sys.argv[2], "w"))
print("done", len(out), "taxcalc", tc.__version__)
