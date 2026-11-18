"""Novel search, part 2: interactions and elections (TY2025 model). Output ../runs/scan2.json.

T1  §86 'torpedo' x senior deduction (§151(d)(5)(C)): marginal rate on IRA withdrawals with the senior deduction
    and without it (switched off through its SSN condition, (C)(iv), facts headSsn/spouseSsn = false).
T2  Most cash a retired couple / single can receive with zero federal income tax (SS + LTCG, SS + IRA).
T3  Separate vs joint returns over a grid of couples and expense allocations (both spouses make the same §63(e)
    choice, §63(c)(6)(A)); flags every couple for which the best pair of separate returns beats the joint one.
T9  §63(e): households for which the smaller deduction is cheaper (AMT), with the 2025 $40,000 SALT cap.
"""
import json
from model import H, run, kid, fica

O = lambda a: {"age": a, "blind": False}
OUT = {}


def t1():
    res = []
    for filing, ages, ss_list in (("single", (67,), (20000, 30000, 40000, 50000)),
                                  ("mfj", (67, 67), (40000, 60000, 80000))):
        for ss in ss_list:
            for senior in (True, False):
                xs = list(range(0, 200001, 500))
                f = {} if senior else {"headSsn": False, "spouseSsn": False}
                mk = lambda x: H(filing=filing, head=O(ages[0]), spouse=O(ages[1]) if len(ages) > 1 else None,
                                 socialSecurity=ss, iraDistributions=x, facts=f)
                rs = run([mk(x) for x in xs] + [mk(x + 1000) for x in xs])
                n = len(xs)
                rates = [((rs[n + i]["netTax"] - rs[i]["netTax"]) / 1000, x) for i, x in enumerate(xs)]
                top = max(rates)
                band = [x for r, x in rates if r >= 0.40]
                res.append(dict(filing=filing, ss=ss, senior=senior, top=top,
                                band40=[band[0], band[-1]] if band else None, n40=len(band)))
                print("T1", filing, ss, "senior" if senior else "no-senior", top, res[-1]["band40"], len(band))
    OUT["T1"] = res


def t2():
    res = []
    for filing, ages in (("mfj", (67, 67)), ("single", (67,))):
        for ss in (0, 20000, 40000, 60000):
            for kind in ("longTermGains", "iraDistributions"):
                xs = list(range(0, 300001, 100))
                mk = lambda x: H(filing=filing, head=O(ages[0]), spouse=O(ages[1]) if len(ages) > 1 else None,
                                 socialSecurity=ss, **{kind: x})
                rs = run([mk(x) for x in xs])
                zero = [x for x, r in zip(xs, rs) if r["netTax"] <= 0]
                mx = max(zero) if zero else None
                res.append(dict(filing=filing, ss=ss, kind=kind, max_zero=mx, cash=(mx or 0) + ss))
                print("T2", filing, ss, kind, mx, (mx or 0) + ss)
    OUT["T2"] = res


def t3():
    """Couples: wages a >= b. Variants allocate expenses to one spouse. Returns MFJ - best MFS."""
    rows = []
    grid = list(range(0, 600001, 25000))
    variants = {
        "plain": lambda a, b: (dict(), dict(), dict()),
        "salt_lower_pays": lambda a, b: (dict(stateLocalTaxes=a // 20 + b // 20 + 20000, mortgageInterest=15000),
                                         dict(stateLocalTaxes=a // 20), dict(stateLocalTaxes=b // 20 + 20000,
                                                                              mortgageInterest=15000)),
        "salt_split": lambda a, b: (dict(stateLocalTaxes=a // 20 + b // 20 + 20000, mortgageInterest=15000),
                                    dict(stateLocalTaxes=a // 20 + 10000, mortgageInterest=7500),
                                    dict(stateLocalTaxes=b // 20 + 10000, mortgageInterest=7500)),
        "carloan_lower": lambda a, b: (dict(carLoanInterest=8000), dict(), dict(carLoanInterest=8000)),
        "medical_lower": lambda a, b: (dict(medicalExpenses=30000), dict(), dict(medicalExpenses=30000)),
        "kids2_with_lower": lambda a, b: (dict(dependents=[kid(5), kid(8)]), dict(), dict(dependents=[kid(5), kid(8)])),
        "kids2_with_higher": lambda a, b: (dict(dependents=[kid(5), kid(8)]), dict(dependents=[kid(5), kid(8)]), dict()),
        "student_loan_lower": lambda a, b: (dict(studentLoanInterest=2500), dict(), dict(studentLoanInterest=2500)),
        "charity_lower": lambda a, b: (dict(charitableCash=40000, stateLocalTaxes=20000),
                                       dict(stateLocalTaxes=10000), dict(charitableCash=40000, stateLocalTaxes=10000)),
    }
    cases, meta = [], []
    for vn, v in variants.items():
        for a in grid:
            for b in grid:
                if b > a:
                    continue
                j, ea, eb = v(a, b)
                cases.append(H(filing="mfj", wages=a + b, wagesSpouse=b, **j)); meta.append((vn, a, b, "mfj", None))
                for el in (True, False):
                    fa = {"electItemize": el, "spouseItemizes": el}
                    cases.append(H(filing="mfs", wages=a, facts=fa, **ea)); meta.append((vn, a, b, "A", el))
                    cases.append(H(filing="mfs", wages=b, facts=fa, **eb)); meta.append((vn, a, b, "B", el))
    rs = run(cases)
    tab = {}
    for (vn, a, b, who, el), r in zip(meta, rs):
        tab.setdefault((vn, a, b), {})[(who, el)] = r["netTax"]
    wins = []
    for (vn, a, b), d in tab.items():
        mfj = d[("mfj", None)]
        mfs = min(d[("A", e)] + d[("B", e)] for e in (True, False))
        if mfj - mfs > 500:
            wins.append((mfj - mfs, vn, a, b))
    wins.sort(reverse=True)
    byv = {}
    for g, vn, a, b in wins:
        byv.setdefault(vn, []).append((g, a, b))
    summary = {vn: dict(n=len(l), best=l[:3]) for vn, l in byv.items()}
    print("T3", json.dumps(summary)[:1500])
    OUT["T3"] = dict(n_couples=len(tab), summary=summary)


def t9():
    cases, meta = [], []
    for w in range(100000, 2000001, 25000):
        for salt in (10000, 25000, 40000):
            for ltcg in (0, 200000, 1000000):
                for filing in ("mfj", "single"):
                    h = dict(filing=filing, wages=w, stateLocalTaxes=salt, mortgageInterest=5000, longTermGains=ltcg)
                    for el in (True, False):
                        cases.append(H(facts={"electItemize": el}, **h)); meta.append((filing, w, salt, ltcg, el))
    rs = run(cases)
    hits = []
    for i in range(0, len(rs), 2):
        ri, rsd = rs[i], rs[i + 1]
        small_wins = (ri["itemized"] < ri["standardDeduction"] and ri["netTax"] < rsd["netTax"]) or \
                     (ri["itemized"] > ri["standardDeduction"] and rsd["netTax"] < ri["netTax"])
        if small_wins:
            hits.append((abs(ri["netTax"] - rsd["netTax"]), meta[i][:4], ri["itemized"], ri["standardDeduction"],
                         ri["amt"], rsd["amt"]))
    hits.sort(reverse=True)
    print("T9", len(hits), hits[:5])
    OUT["T9"] = dict(n=len(hits), top=hits[:20])


if __name__ == "__main__":
    t1(); t2(); t3(); t9()
    json.dump(OUT, open("../runs/scan2.json", "w"), indent=1)
