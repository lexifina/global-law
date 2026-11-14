"""PolicyEngine-US on the Tax Court returns (oracle_work/returns.json), each in its own tax year, placed in Texas
(no state income tax). Mapping adapted from global-law-lean tools/taxcode/diff/run_policyengine.py.

    ~/pev/Scripts/python.exe oracle_pe.py
"""
import json, os
import importlib.metadata as md
from policyengine_us import Simulation
from policyengine_us.system import system as SYS

WORK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "oracle_work")
OUT = ["adjusted_gross_income", "taxable_income", "income_tax_before_credits", "alternative_minimum_tax", "eitc",
       "non_refundable_ctc", "refundable_ctc", "income_tax_capped_non_refundable_credits",
       "income_tax_refundable_credits", "self_employment_tax", "taxable_social_security", "income_tax",
       "net_investment_income_tax", "additional_medicare_tax", "standard_deduction", "tax_unit_itemizes",
       "itemized_taxable_income_deductions", "recovery_rebate_credit"]
OUT = [v for v in OUT if v in SYS.variables]
STATUS = {"single": "SINGLE", "mfj": "JOINT", "mfs": "SEPARATE", "hoh": "HEAD_OF_HOUSEHOLD", "qss": "SURVIVING_SPOUSE"}


def situation(h):
    Y = str(h["year"])
    people, members = {}, []

    def person(name, age, **inc):
        people[name] = {"age": {Y: age}, "medical_expense_health_insurance_premiums": {Y: 0},
                        **{k: {Y: v} for k, v in inc.items() if v}}
        members.append(name)
    joint = h["filing"] == "mfj"
    person("head", h["age"], employment_income=h["wages"] - h["wagesSpouse"],
           self_employment_income=h["se"] if joint else h["se"] + h["seSpouse"],
           taxable_interest_income=h["interest"], tax_exempt_interest_income=h["exemptInterest"],
           qualified_dividend_income=h["qualDiv"], non_qualified_dividend_income=h["ordDiv"] - h["qualDiv"],
           long_term_capital_gains=h["ltcg"], short_term_capital_gains=h["stcg"],
           taxable_pension_income=h["pensions"], taxable_ira_distributions=h["ira"],
           social_security_retirement=h["ss"], unemployment_compensation=h["ui"] - h["uiSpouse"],
           # PolicyEngine floors miscellaneous_income at 0 and, in 2020, leaves gambling_winnings out of gross income:
           # gambling winnings go in as other income, a net loss in other income as an above-the-line deduction
           # (the same AGI and the same §86 modified AGI)
           miscellaneous_income=max(0, h["other"]) + h["gamblingWin"],
           # the court's other adjustments (an allowed amount): an uncapped above-the-line deduction
           early_withdrawal_penalty=h["adjustments"] + max(0, -h["other"]),
           # the court's itemized deductions (an allowed total) and §165(d) losses (<= winnings here): interest has
           # no floor or cap
           deductible_mortgage_interest=h["itemized"] + h["gamblingLoss"], is_blind=h["blind"])
    if joint:
        person("spouse", h["spouseAge"], employment_income=h["wagesSpouse"], self_employment_income=h["seSpouse"],
               unemployment_compensation=h["uiSpouse"], is_blind=h["spouseBlind"])
    for i, d in enumerate(h["dependents"]):
        person(f"dep{i}", d["age"], is_full_time_student=d["student"])
        people[f"dep{i}"]["is_tax_unit_dependent"] = {Y: True}
    tu = {"members": members, "filing_status": {Y: STATUS[h["filing"]]},
          "state_and_local_sales_or_income_tax": {Y: 0}}
    if h["itemize"] is not None:
        tu["tax_unit_itemizes"] = {Y: bool(h["itemize"])}
    adults = members[:2] if joint else members[:1]
    mu = {"m": {"members": adults}}
    for n in members:
        if n not in adults:
            mu["m_" + n] = {"members": [n]}
    return {"people": people, "tax_units": {"tu": tu}, "spm_units": {"s": {"members": members}},
            "families": {"f": {"members": members}}, "marital_units": mu,
            "households": {"hh": {"members": members, "state_name": {Y: "TX"}}}}


rets = json.load(open(os.path.join(WORK, "returns.json"), encoding="utf-8"))
res = []
for h in rets:
    try:
        s = Simulation(situation=situation(h))
        r = {v: float(s.calculate(v, h["year"]).sum()) for v in OUT}
    except Exception as e:
        r = {"error": f"{type(e).__name__}: {str(e)[:300]}"}
    r.update(key=h["key"], which=h["which"])
    res.append(r)
    print(h["key"], h["which"], "error " + r["error"] if "error" in r else "ok", flush=True)
json.dump({"engine": "policyengine-us " + md.version("policyengine-us"), "results": res},
          open(os.path.join(WORK, "pe_out.json"), "w"), indent=1)
