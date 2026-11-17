"""Federal <-> Alabama loop with PolicyEngine-US 2.138.1: federal SALT uses the state tax PAID in the year
(input state_withheld_income_tax, cash basis, sec. 164(a)/sec. 461); Alabama deducts federal income tax liability
(Ala. Code sec. 40-18-15(a)(2), r. 810-3-15-.20). Iterate paid = Alabama liability (taxpayer pays the exact
liability in the year, e.g. December estimate) and report the fixed point, convergence and the value of paying in
the year versus paying in the next year (the timing lever)."""
import sys
from policyengine_us import Simulation

def sim(year, state, wages, paid, itemize_extra, married):
    people = {"you": {"age": {year: 45}, "employment_income": {year: wages},
                      "real_estate_taxes": {year: itemize_extra}, "charitable_cash_donations": {year: 30000}}}
    members = ["you"]
    if married:
        people["spouse"] = {"age": {year: 45}}
        members.append("spouse")
    hh = {"people": people,
          "tax_units": {"tu": {"members": members, "state_withheld_income_tax": {year: paid}}},
          "families": {"f": {"members": members}}, "spm_units": {"s": {"members": members}},
          "marital_units": {"m": {"members": members}} if married else {"m": {"members": ["you"]}},
          "households": {"h": {"members": members, "state_name": {year: state}}}}
    s = Simulation(situation=hh)
    return (float(s.calculate("income_tax", year)[0]), float(s.calculate("state_income_tax", year)[0]),
            float(s.calculate("al_federal_income_tax_deduction", year)[0]) if state == "AL" else 0.0)

if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    for wages, re_tax, married in [(150000, 6000, False), (400000, 10000, True), (700000, 15000, True)]:
        paid = 0.0
        trace = []
        for k in range(8):
            fed, st, ded = sim(year, "AL", wages, paid, re_tax, married)
            trace.append((round(paid), round(fed), round(st), round(ded)))
            if abs(st - paid) < 1:
                break
            paid = st
        fed0, st0, _ = sim(year, "AL", wages, 0.0, re_tax, married)
        print(f"wages {wages} married {married} RE tax {re_tax}: iterations {trace}")
        print(f"   pay AL tax in the year: fed {trace[-1][1]} + AL {trace[-1][2]}; pay nothing in the year: fed {round(fed0)} + AL {round(st0)};"
              f" federal saving from paying in-year {round(fed0 - trace[-1][1])}")
