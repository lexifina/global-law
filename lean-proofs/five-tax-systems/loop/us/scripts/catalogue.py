"""Recreate the catalogued US loopholes with the model (TY2025). Each item: households without and with the move,
the tax difference. `extra` adds FICA where the move changes payroll tax the model's return does not show (the
model's return carries SE tax and the 0.9% additional Medicare tax, not the 7.65% employee/employer FICA on wages).

    python3 catalogue.py            -> ../runs/catalogue.json and a table on stdout
"""
import json, os
from model import H, run, kid, fica

S = lambda **kw: H(filing="single", **kw)
J = lambda **kw: H(filing="mfj", **kw)
OLD = {"age": 66, "blind": False}
OLD73 = {"age": 73, "blind": False}

ITEMS = []


def item(kid_, name, base, move, note=""):
    """base/move: list of (case, coef, extra)."""
    ITEMS.append(dict(id=kid_, name=name, base=base, move=move, note=note))


def one(c, extra=0, coef=1):
    return (c, coef, extra)


# ---- searches that size a move first -------------------------------------------------------------------------------

def max_free(make, lo, hi, step=10):
    """Largest x in [lo, hi] (on `step`) with net(make(x)) == net(make(0))."""
    xs = list(range(lo, hi + 1, step))
    rs = run([make(0)] + [make(x) for x in xs])
    b = rs[0]["netTax"]
    best = 0
    for x, r in zip(xs, rs[1:]):
        if r["netTax"] <= b:
            best = x
        else:
            break
    return best


g04 = max_free(lambda g: J(wages=80000, longTermGains=g), 0, 200000)
x16 = max_free(lambda x: J(head=OLD, spouse=OLD, pensions=20000, iraDistributions=x), 0, 100000)


def build():
    item("K01", "Long-term capital gain instead of ordinary income (§1(h))",
         [one(S(wages=100000, otherIncome=50000))], [one(S(wages=100000, longTermGains=50000))])
    item("K02", "Qualified instead of ordinary dividends (§1(h)(11))",
         [one(J(wages=200000, ordinaryDividends=40000))],
         [one(J(wages=200000, ordinaryDividends=40000, qualifiedDividends=40000))])
    item("K03", "Carried interest: $1m of fund profit share as LTCG (§1061 3-yr holding met) vs as a fee (SE income, SSTB)",
         [one(J(wages=500000, seIncome=1000000, facts={"qbiSstb": True}))],
         [one(J(wages=500000, longTermGains=1000000))])
    item("K04", f"0% LTCG gain harvesting: ${g04:,} realised at zero tax (MFJ, $80k wages) instead of in a $200k year",
         [one(J(wages=200000, longTermGains=g04)), one(J(wages=200000), coef=-1)],
         [one(J(wages=80000, longTermGains=g04)), one(J(wages=80000), coef=-1)])
    item("K05", "Tax-loss harvesting: $23k loss offsets $20k gain and $3k of wages (§1211(b))",
         [one(S(wages=150000, longTermGains=20000))], [one(S(wages=150000, longTermGains=-3000))])
    item("K06", "Crypto loss harvest with immediate buy-back (§1091 reaches only stock or securities; Notice 2014-21)",
         [one(S(wages=150000, longTermGains=20000))], [one(S(wages=150000, longTermGains=-3000))],
         "same arithmetic as K05: the model has no §1091, so the crypto-vs-stock difference is the rule's absence")
    item("K07", "Step-up in basis at death: heir sells a $1m asset with $100k basis (§1014)",
         [one(J(wages=150000, longTermGains=900000))], [one(J(wages=150000))])
    item("K08", "Home sale exclusion $500k (§121)",
         [one(J(wages=150000, longTermGains=500000))], [one(J(wages=150000))])
    item("K09", "QSBS: $5m gain on qualified small business stock excluded (§1202(a)(4); no §57(a)(7) preference)",
         [one(J(wages=300000, longTermGains=5000000))], [one(J(wages=300000))])
    item("K10", "Municipal bond interest (§103): $50k exempt instead of taxable",
         [one(J(wages=300000, taxableInterest=50000))], [one(J(wages=300000, taxExemptInterest=50000))],
         "equal pre-tax yield; break-even muni yield is (1 - marginal rate incl. NIIT) of the taxable yield")
    item("K12", "401(k) elective deferral $23,500 (§402(g)); FICA unchanged (§3121(a)(5)(A) excludes nothing)",
         [one(S(wages=80000))], [one(S(wages=56500, retirementContributions=23500))], "deferral, not exclusion")
    item("K13", "Deductible IRA $2k each + saver's credit 50% tier (§219, §25B)",
         [one(J(wages=50000, wagesSpouse=25000))],
         [one(J(wages=50000, wagesSpouse=25000, iraContributions=4000, retirementContributions=4000))],
         "the deduction moves AGI from the 20% to the 50% tier: $1 saved earns more than $1 of credit band")
    item("K16", f"Roth conversion room at zero tax: ${x16:,} converted by a 66/66 couple with $20k pension (std + §63(f) + senior)",
         [one(J(head=OLD, spouse=OLD, pensions=80000, iraDistributions=x16)),
          one(J(head=OLD, spouse=OLD, pensions=80000), coef=-1)],
         [one(J(head=OLD, spouse=OLD, pensions=20000, iraDistributions=x16)),
          one(J(head=OLD, spouse=OLD, pensions=20000), coef=-1)],
         "vs the same conversion in an $80k-pension year")
    item("K17", "HSA family $8,550 through a cafeteria plan (§223, §106(d), §3121(a)(2)(B)): no income tax, no FICA",
         [one(J(wages=120000, wagesSpouse=60000), extra=fica(60000) * 4)],
         [one(J(wages=111450, wagesSpouse=51450), extra=fica(60000) * 2 + fica(51450) * 2)],
         "extra = employee + employer FICA")
    item("K18", "Dependent-care FSA $5,000 (§129) instead of the credit (§21(c) limit cut by the exclusion)",
         [one(J(wages=150000, wagesSpouse=75000, dependents=[kid(4), kid(6)], childCareExpenses=10000),
              extra=2 * fica(75000))],
         [one(J(wages=145000, wagesSpouse=72500, dependents=[kid(4), kid(6)], childCareExpenses=1000),
              extra=2 * fica(72500))], "extra = employee FICA")
    nq = -(100000 - 7065)
    item("K19", "§199A 20% deduction on $100k Schedule C profit (non-SSTB, under the threshold)",
         [one(S(seIncome=100000, qbi=nq))], [one(S(seIncome=100000))], "base nets QBI to zero (counterfactual)")
    item("K22", "S corporation: $200k profit, $80k salary + distribution vs Schedule C (§1402 vs §§3101/3111; Rev. Rul. 74-44)",
         [one(S(seIncome=200000))],
         [one(S(wages=80000, qbi=200000 - 80000 - fica(80000), otherIncome=200000 - 80000 - fica(80000),
                facts={"qbiW2Wages": 80000}), extra=2 * fica(80000))],
         "extra = employee + employer FICA on the salary; the employer half is deducted from the K-1")
    item("K23", "Hiring a 15-year-old child in a sole proprietorship: $15k wages (§3121(b)(3)(A), §63(c)(5))",
         [one(J(seIncome=200000, dependents=[kid(15)]))],
         [one(J(seIncome=185000, dependents=[kid(15)])),
          one(S(head={"age": 15, "blind": False}, canBeClaimedAsDependent=True, wages=15000))],
         "both returns counted; no FICA on a parent's sole-proprietorship wages to a child under 18")
    item("K24", "Head of household instead of single (§2(b), §1(b))",
         [one(S(wages=60000, dependents=[kid(8)]))], [one(H(filing="hoh", wages=60000, dependents=[kid(8)]))])
    item("K25a", "Marriage bonus: one earner ($200k) marries before 31 December (§7703(a)(1))",
         [one(S(wages=200000)), one(S())], [one(J(wages=200000))])
    item("K25b", "Marriage penalty avoided: two $25k earners with two children stay unmarried (EIC §32, HOH)",
         [one(J(wages=50000, wagesSpouse=25000, dependents=[kid(4), kid(7)]))],
         [one(H(filing="hoh", wages=25000, dependents=[kid(4), kid(7)])), one(S(wages=25000))])
    item("K26", "Unmarried parents: the $20k earner claims both children instead of the $60k earner (§152(c)(4))",
         [one(H(filing="hoh", wages=60000, dependents=[kid(4), kid(7)])), one(S(wages=20000))],
         [one(S(wages=60000)), one(H(filing="hoh", wages=20000, dependents=[kid(4), kid(7)]))],
         "recreates Household hunt plan 6")
    item("K27", "EIC investment-income cliff: $1 of interest over $11,950 (§32(i)); keep it at $11,950",
         [one(H(filing="hoh", wages=25000, dependents=[kid(6)], taxableInterest=11951))],
         [one(H(filing="hoh", wages=25000, dependents=[kid(6)], taxableInterest=11950))], "known cliff")
    item("K28", "CTC notch: $1 of wages over $400,000 MFJ costs $50 (§24(b)(1) 'or fraction thereof')",
         [one(J(wages=400001, dependents=[kid(5), kid(8)]))], [one(J(wages=400000, dependents=[kid(5), kid(8)]))])
    b29 = dict(wages=200000, stateLocalTaxes=10000, mortgageInterest=12000)
    item("K29", "Bunching two years of gifts ($10k/yr) into one year via a donor-advised fund (§170, §63(e))",
         [one(J(charitableCash=10000, **b29)), one(J(charitableCash=10000, **b29))],
         [one(J(charitableCash=20000, **b29)), one(J(charitableCash=0, **b29))], "two years at 2025 law")
    item("K30", "Giving $50k of stock (basis $10k) instead of selling and giving cash (§170(e)(1), 30% limit not binding)",
         [one(J(wages=300000, longTermGains=40000, charitableCash=50000))],
         [one(J(wages=300000, charitableCash=50000))])
    item("K31", "Qualified charitable distribution $10k from an IRA at 73 (§408(d)(8)) vs withdraw and give",
         [one(J(head=OLD73, spouse=OLD73, socialSecurity=50000, iraDistributions=100000, charitableCash=10000))],
         [one(J(head=OLD73, spouse=OLD73, socialSecurity=50000, iraDistributions=90000))],
         "standard-deduction household; also cuts taxable Social Security (§86)")
    f32 = {"qbiW2Wages": 300000}
    item("K32", "SALT cap workaround: pass-through entity tax on $27.5k of state income tax (Notice 2020-75)",
         [one(J(qbi=550000, otherIncome=550000, stateLocalTaxes=42500, facts=f32))],
         [one(J(qbi=522500, otherIncome=522500, stateLocalTaxes=15000, facts=f32))],
         "K-1 income carried as otherIncome + qbi; PTET also lowers MAGI under §164(b)(7)(B)'s $500k line")
    item("K33", "401(k) $23,500 deferral inside the SALT phase-down band (§164(b)(7)(B)): MFJ $510k wages, $60k SALT",
         [one(J(wages=510000, stateLocalTaxes=60000))],
         [one(J(wages=486500, stateLocalTaxes=60000, retirementContributions=23500))])
    item("K34", "No tax on tips: $20k qualified tips of $60k wages (§224)",
         [one(S(wages=60000))], [one(S(wages=60000, qualifiedTips=20000))])
    item("K35", "No tax on overtime: $8k premium pay (§225)",
         [one(J(wages=90000))], [one(J(wages=90000, qualifiedOvertime=8000))])
    item("K36", "Car loan interest $5k (§163(h)(4))",
         [one(S(wages=80000))], [one(S(wages=80000, carLoanInterest=5000))])
    item("K37", "Senior deduction kept: a 66/66 couple draws $30k of $180k from a Roth instead of a traditional IRA (§151(d)(5)(C))",
         [one(J(head=OLD, spouse=OLD, iraDistributions=180000))],
         [one(J(head=OLD, spouse=OLD, iraDistributions=150000))])
    item("K39", "Premium tax credit raised by a $7,000 deductible IRA (§36B(d)(2), §219): single 60, $70k wages",
         [one(S(head={"age": 60, "blind": False}, wages=70000, marketplacePremium=13000, benchmarkPremium=13000))],
         [one(S(head={"age": 60, "blind": False}, wages=70000, iraContributions=7000, marketplacePremium=13000,
                benchmarkPremium=13000))])
    item("K42", "Employer health insurance $20k excluded (§106, §3121(a)(2)) vs paid as wages",
         [one(J(wages=120000, wagesSpouse=0), extra=2 * fica(120000))],
         [one(J(wages=100000, wagesSpouse=0), extra=2 * fica(100000))], "extra = employee + employer FICA")
    item("K43", "Installment sale (§453): $400k gain over four years instead of one (MFJ, $60k wages each year)",
         [one(J(wages=60000, longTermGains=400000))] + [one(J(wages=60000))] * 3,
         [one(J(wages=60000, longTermGains=100000))] * 4, "four years at 2025 law")
    f52 = {"electItemize": True, "spouseItemizes": True}
    item("K52", "Separate returns double the SALT cap: $350k + $250k, the lower earner pays the property tax and mortgage",
         [one(J(wages=600000, wagesSpouse=250000, stateLocalTaxes=60000, mortgageInterest=20000))],
         [one(H(filing="mfs", wages=350000, stateLocalTaxes=17500, facts=f52)),
          one(H(filing="mfs", wages=250000, stateLocalTaxes=42500, mortgageInterest=20000, facts=f52))],
         "recreates NewDeductions plan 2 (one year)")
    item("K54", "Supporting a parent: head of household + $500 credit for other dependents (§2(b)(1)(B), §24(h)(4))",
         [one(S(wages=50000))], [one(H(filing="hoh", wages=50000, dependents=[kid(75)]))])
    item("K55", "'Augusta rule': business rents the owner's home 14 days for $20k (§280A(g), §162)",
         [one(J(seIncome=250000))], [one(J(seIncome=230000))], "rent deducted by the business, excluded by the owner")
    item("K61", "Net unrealised appreciation: $500k of employer stock (basis $100k) out of a 401(k) (§402(e)(4))",
         [one(J(head=OLD, spouse=OLD, iraDistributions=500000))],
         [one(J(head=OLD, spouse=OLD, iraDistributions=100000, longTermGains=400000))])


def special():
    """K20: §199A W-2 wage planning; K21: SSTB phase-in deferral; K38: §86 torpedo marginal rate; K37b senior band."""
    out = {}
    # K20: MFJ, S corp non-SSTB, $1m profit, owner salary W; total = income tax + FICA both halves
    rows = []
    for W in range(0, 500001, 5000):
        k1 = 1000000 - W - fica(W)
        rows.append((W, J(wages=W, qbi=k1, otherIncome=0, facts={"qbiW2Wages": W})))
    # K-1 income must be in AGI: carry it as otherIncome too
    cases = []
    for W, c in rows:
        c["h"]["otherIncome"] = c["h"]["qbi"]
        cases.append(c)
    rs = run(cases)
    tot = [(W, r["netTax"] + 2 * fica(W), r["qbiDeduction"]) for (W, _), r in zip(rows, rs)]
    best = min(tot, key=lambda t: t[1])
    out["K20"] = dict(name="§199A(b)(2)(B) wage limit: S-corp owner ($1m profit, MFJ, no other employees) sizes salary",
                      best_salary=best[0], best_total=best[1], qbi_ded=best[2],
                      at_0=tot[0], at_100k=[t for t in tot if t[0] == 100000][0],
                      saving_vs_zero_salary=tot[0][1] - best[1],
                      saving_vs_100k=[t for t in tot if t[0] == 100000][0][1] - best[1])
    # K21: SSTB S-corp owner MFJ, salary 150k + K-1 300k; 401(k) deferral 23,500
    f = {"qbiSstb": True, "qbiW2Wages": 150000}
    a = J(wages=150000, qbi=300000, otherIncome=300000, facts=f)
    b = J(wages=126500, qbi=300000, otherIncome=300000, retirementContributions=23500, facts=f)
    ra, rb = run([a, b])
    out["K21"] = dict(name="SSTB phase-in (§199A(d)(3)): $23,500 401(k) deferral by an SSTB owner at $450k MFJ",
                      base=ra["netTax"], move=rb["netTax"], saving=ra["netTax"] - rb["netTax"],
                      rate=round((ra["netTax"] - rb["netTax"]) / 23500, 4),
                      qbi_base=ra["qbiDeduction"], qbi_move=rb["qbiDeduction"])
    # K38: §86 torpedo: single 67, SS 30k, IRA withdrawals 0..80k: max marginal rate over $1,000 steps
    xs = list(range(0, 80001, 1000))
    rs = run([S(head={"age": 67, "blind": False}, socialSecurity=50000, iraDistributions=x) for x in xs])
    m = [((rs[i + 1]["netTax"] - rs[i]["netTax"]) / 1000, xs[i]) for i in range(len(xs) - 1)]
    out["K38"] = dict(name="Social Security 'tax torpedo' (§86): single 67, $50k benefits, IRA withdrawals",
                      max_rate=max(m), band=[x for r, x in m if r >= 0.3])
    # K37b: senior band marginal rate MFJ 66/66 at $160k IRA
    r0, r1 = run([J(head=OLD, spouse=OLD, iraDistributions=160000), J(head=OLD, spouse=OLD, iraDistributions=161000)])
    out["K37b"] = dict(name="Marginal rate in the senior-deduction phase-out (MFJ 66/66, $160k)",
                       rate=(r1["netTax"] - r0["netTax"]) / 1000)
    # K33b: SALT phase-down band marginal rate
    r0, r1 = run([J(wages=550000, stateLocalTaxes=60000), J(wages=551000, stateLocalTaxes=60000)])
    out["K33b"] = dict(name="Marginal rate inside the SALT phase-down (MFJ $550k wages, $60k SALT)",
                       rate=(r1["netTax"] - r0["netTax"]) / 1000)
    return out


def main():
    build()
    flat = []
    for it in ITEMS:
        for side in ("base", "move"):
            for c, coef, extra in it[side]:
                flat.append(c)
    rs = run(flat)
    k = 0
    res = []
    for it in ITEMS:
        tot = {}
        for side in ("base", "move"):
            s = 0
            for c, coef, extra in it[side]:
                s += coef * (rs[k]["netTax"] + extra)
                k += 1
            tot[side] = s
        res.append(dict(id=it["id"], name=it["name"], base=tot["base"], move=tot["move"],
                        saving=tot["base"] - tot["move"], note=it["note"]))
    sp = special()
    out = dict(items=res, special=sp, g04=g04, x16=x16)
    os.makedirs("../runs", exist_ok=True)
    json.dump(out, open("../runs/catalogue.json", "w"), indent=1)
    for r in res:
        print(f"{r['id']:5} {r['base']:>10,} {r['move']:>10,} {r['saving']:>9,}  {r['name'][:80]}")
    for k_, v in sp.items():
        print(k_, json.dumps(v)[:400])


if __name__ == "__main__":
    main()
