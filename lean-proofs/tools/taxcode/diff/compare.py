"""Compare the Lean model with PolicyEngine-US and Tax-Calculator, household by household.

    python compare.py households.json lean.json pe.json tc.json report.json [ustaxes.json]

Quantities compared (all 2025, federal):
  agi           adjusted gross income
  taxable       taxable income
  taxBefore     income tax before credits (regular tax + AMT)
  eitc          earned income credit
  actc          refundable (additional) child tax credit
  nonref        nonrefundable credits used against the tax (the tools split this total between credits differently
                where it is capped by the tax, so the total is compared, not each credit)
  incomeTax     income tax after all credits, plus net investment income tax (excluding SE and payroll taxes)

A difference of more than $tolerance counts as a disagreement. The Tax Table midpoint rule alone moves the regular tax
by up to $6 below $100,000 of taxable income (group C, `table_within_6`); the tolerance used here is $10.
"""
import json, sys
from collections import Counter, defaultdict

hs, lean, pe, tc = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:5])
ut = json.load(open(sys.argv[6], encoding="utf-8")) if len(sys.argv) > 6 else None
TOL = 10


def lean_q(r):
    return {"agi": r["agi"], "taxable": r["taxableIncome"], "taxBefore": r["taxBeforeCredits"], "eitc": r["eitc"],
            "actc": r["actc"], "nonref": r["nonrefundableCredits"],
            "incomeTax": r["incomeTaxAfterCredits"] + r["niit"] - r["refundableCredits"]}


def pe_q(r):
    if "error" in r:
        return None
    return {"agi": r["adjusted_gross_income"], "taxable": r["taxable_income"], "taxBefore": r["income_tax_before_credits"],
            "eitc": r["eitc"], "actc": r["refundable_ctc"],
            "nonref": r["income_tax_capped_non_refundable_credits"],
            "incomeTax": r["income_tax"]}


def tc_q(r):
    return {"agi": r["c00100"], "taxable": r["c04800"], "taxBefore": r["taxbc"] + r["c09600"], "eitc": r["eitc"],
            "actc": r["c11070"], "nonref": r["c07100"], "incomeTax": r["iitax"]}


def ut_q(r):
    """UsTaxes (run_ustaxes.ts). It reports no total of nonrefundable credits, so that quantity is not compared."""
    if r is None or "error" in r:
        return None
    return {"agi": r["agi"], "taxable": r["taxableIncome"], "taxBefore": r["taxBeforeCredits"], "eitc": r["eitc"],
            "actc": r["actc"], "incomeTax": r["incomeTax"]}


QS = ["agi", "taxable", "taxBefore", "eitc", "actc", "nonref", "incomeTax"]


def tc_unsupported(h):
    """Quantities Tax-Calculator cannot compute for this household: it takes the saver's credit (e07240) and the
    American opportunity credit (e87521) as inputs rather than computing them, takes the student loan interest
    deduction as an input, and its surviving-spouse status is not compared."""
    if h["filing"] == "qss":
        return set(QS)
    if h.get("studentLoanInterest"):   # e03210 is the deduction after the §221 limits, not the interest paid
        return set(QS) - {"eitc"}
    if h.get("retirementContributions") or h.get("qualifiedTuition"):
        return {"incomeTax", "nonref", "actc"}
    return set()
rows, stats = [], defaultdict(Counter)
for i, h in enumerate(hs):
    L = lean_q(lean[i]); P = pe_q(pe[i]); T = tc_q(tc[i]); U = ut_q(ut[i]) if ut else None
    row = {"i": i, "filing": h["filing"], "deps": len(h["dependents"]), "wages": h["wages"], "lean": L, "pe": P, "tc": T, "ut": U}
    skip_tc = tc_unsupported(h)
    for q in QS:
        for name, other in (("pe", P), ("tc", T)) + ((("ut", U),) if ut else ()):
            if name == "tc" and q in skip_tc:
                stats[f"{name}:{q}"]["n/a"] += 1
                continue
            if name == "ut" and other is not None and q not in other:
                continue
            if other is None:
                stats[f"{name}:{q}"]["error"] += 1
                continue
            d = L[q] - other[q]
            stats[f"{name}:{q}"]["agree" if abs(d) <= TOL else "disagree"] += 1
        if q in skip_tc:
            pass
        elif P and abs(P[q] - T[q]) > TOL:
            stats[f"pe-vs-tc:{q}"]["disagree"] += 1
        elif P:
            stats[f"pe-vs-tc:{q}"]["agree"] += 1
    rows.append(row)

json.dump({"tolerance": TOL, "stats": {k: dict(v) for k, v in stats.items()}, "rows": rows},
          open(sys.argv[5], "w", encoding="utf-8"))
print(f"{len(hs)} households, tolerance ${TOL}")
for q in QS:
    line = [f"{q:10}"]
    for name in ("pe", "tc") + (("ut",) if ut else ()) + ("pe-vs-tc",):
        c = stats[f"{name}:{q}"]
        n = (sum(c.values()) - c["n/a"])
        if n == 0:
            line.append(f"{name}: —")
            continue
        line.append(f"{name}: {c['agree']}/{n} agree" + (f" ({c['n/a']} n/a)" if c["n/a"] else ""))
    print("  " + " | ".join(line))
