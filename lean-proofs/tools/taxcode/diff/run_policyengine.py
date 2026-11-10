"""Run PolicyEngine-US on the households (tax year 2025, placed in Texas: no state income tax).

    <pev python> run_policyengine.py households.json pe.json [batch size]
"""
import json, sys
from policyengine_us import Simulation

hs = json.load(open(sys.argv[1], encoding="utf-8"))
YEAR = "2025"
OUT = ["adjusted_gross_income", "taxable_income", "income_tax_before_credits", "eitc", "ctc", "refundable_ctc",
       "non_refundable_ctc", "cdcc", "income_tax", "self_employment_tax", "alternative_minimum_tax", "net_investment_income_tax",
       "standard_deduction", "itemized_taxable_income_deductions", "taxable_social_security", "qualified_business_income_deduction",
       "american_opportunity_credit", "savers_credit", "tip_income_deduction", "overtime_income_deduction",
       "auto_loan_interest_deduction", "additional_senior_deduction", "income_tax_capped_non_refundable_credits"]


# Inputs passed even when zero. PolicyEngine imputes Medicare Part B premiums for people over 65 and counts them as
# medical expenses; the households record medical expenses directly, so premiums are pinned at 0.
ALWAYS = {"employment_income", "medical_expense_health_insurance_premiums"}


def situation(h):
    people, members = {}, []
    def person(name, age, **inc):
        people[name] = {"age": {YEAR: age}, **{k: {YEAR: v} for k, v in inc.items() if v or k in ALWAYS}}
        members.append(name)
    head_w = h["wages"] - h["wagesSpouse"]
    joint = h["filing"] == "mfj"
    ira_head = h["iraContributions"] - (h["iraContributions"] // 2 if joint else 0)  # Lean splits joint saver
    person("head", h["head"]["age"], employment_income=head_w, self_employment_income=h["seIncome"],
           taxable_interest_income=h["taxableInterest"], tax_exempt_interest_income=h["taxExemptInterest"],
           qualified_dividend_income=h["qualifiedDividends"],
           non_qualified_dividend_income=h["ordinaryDividends"] - h["qualifiedDividends"],
           long_term_capital_gains=h["longTermGains"], short_term_capital_gains=h["shortTermGains"],
           taxable_pension_income=h["pensions"], social_security_retirement=h["socialSecurity"],
           unemployment_compensation=h["unemployment"], real_estate_taxes=h["stateLocalTaxes"],
           deductible_mortgage_interest=h["mortgageInterest"], charitable_cash_donations=h["charitableCash"],
           other_medical_expenses=h["medicalExpenses"], is_blind=h["head"].get("blind", False),
           tip_income=h["qualifiedTips"], tip_income_deduction_occupation_requirement_met=True,
           fsla_overtime_premium=h["qualifiedOvertime"],
           qualified_passenger_vehicle_loan_interest_person=h["carLoanInterest"],
           student_loan_interest=h["studentLoanInterest"], educator_expense=h["educatorExpenses"],
           traditional_ira_contributions=ira_head, medical_expense_health_insurance_premiums=0)
    if h["spouse"]:
        person("spouse", h["spouse"]["age"], employment_income=h["wagesSpouse"], is_blind=h["spouse"].get("blind", False),
               traditional_ira_contributions=h["iraContributions"] // 2 if joint else 0,
               medical_expense_health_insurance_premiums=0)
    tuition = list(h.get("qualifiedTuition", []))
    for i, d in enumerate(h["dependents"]):
        extra = {"is_full_time_student": bool(d.get("student"))}
        if d.get("student") and tuition:
            extra.update(qualified_tuition_expenses=tuition.pop(0), is_eligible_for_american_opportunity_credit=True)
        person(f"dep{i}", d["age"], **extra)
        people[f"dep{i}"]["is_tax_unit_dependent"] = {YEAR: True}
    # Placed in Texas (no state income tax). PolicyEngine would otherwise impute a sales-tax deduction under
    # §164(b)(5); the households' SALT is entered entirely as real-estate tax, so the imputation is switched off.
    tu = {"members": members, "tax_unit_childcare_expenses": {YEAR: h["childCareExpenses"]},
          "state_and_local_sales_or_income_tax": {YEAR: 0}, "health_savings_account_ald": {YEAR: h["hsaContributions"]}}
    tu["filing_status"] = {YEAR: {"single": "SINGLE", "mfj": "JOINT", "mfs": "SEPARATE", "hoh": "HEAD_OF_HOUSEHOLD",
                                  "qss": "SURVIVING_SPOUSE"}[h["filing"]]}
    return {"people": people, "tax_units": {"tu": tu}, "spm_units": {"s": {"members": members}},
            "families": {"f": {"members": members}}, "marital_units": {"m": {"members": members[:2] if h["spouse"] else members[:1]}},
            "households": {"hh": {"members": members, "state_name": {YEAR: "TX"}}}}


from policyengine_us.system import system as _sys
_full = dict(hs[0], **{k: 1 for k in ("qualifiedTips", "qualifiedOvertime", "carLoanInterest", "studentLoanInterest",
            "educatorExpenses", "iraContributions", "taxExemptInterest", "hsaContributions")}, qualifiedTuition=[1],
            dependents=[{"age": 20, "student": True}])
_probe = situation(_full)
_missing = sorted(({k for p in _probe["people"].values() for k in p} | set(_probe["tax_units"]["tu"]) - {"members"}) - set(_sys.variables)) +     sorted(v for v in OUT if v not in _sys.variables)
if _missing:
    sys.exit(f"unknown PolicyEngine variables: {_missing}")

def batch(chunk, base):
    """Many households in one simulation: each gets its own people and group entities, prefixed by its index."""
    sit = {k: {} for k in ("people", "tax_units", "spm_units", "families", "marital_units", "households")}
    for j, h in enumerate(chunk):
        one, p = situation(h), f"h{base + j}_"
        ren = lambda names: [p + n for n in names]
        sit["people"].update({p + n: v for n, v in one["people"].items()})
        tu = dict(one["tax_units"]["tu"]); tu["members"] = ren(tu["members"])
        sit["tax_units"][p + "tu"] = tu
        sit["spm_units"][p + "s"] = {"members": ren(one["spm_units"]["s"]["members"])}
        sit["families"][p + "f"] = {"members": ren(one["families"]["f"]["members"])}
        adults = one["marital_units"]["m"]["members"]
        sit["marital_units"][p + "m"] = {"members": ren(adults)}
        for n in one["people"]:
            if n not in adults:
                sit["marital_units"][p + "m_" + n] = {"members": [p + n]}
        hh = dict(one["households"]["hh"]); hh["members"] = ren(hh["members"])
        sit["households"][p + "hh"] = hh
    return sit


res = []
B = int(sys.argv[3]) if len(sys.argv) > 3 else 100
for base in range(0, len(hs), B):
    chunk = hs[base:base + B]
    try:
        s = Simulation(situation=batch(chunk, base))
        cols = {v: s.calculate(v, int(YEAR), map_to="tax_unit") for v in OUT}
        res.extend({v: float(cols[v][j]) for v in OUT} for j in range(len(chunk)))
    except Exception as e:  # fall back to one household at a time, recording failures
        for h in chunk:
            try:
                s = Simulation(situation=situation(h))
                res.append({v: float(s.calculate(v, int(YEAR)).sum()) for v in OUT})
            except Exception as e1:
                res.append({"error": str(e1)[:200]})
    print(base + len(chunk), flush=True)
json.dump(res, open(sys.argv[2], "w"))
print("done", len(res))
