"""Generate a fixed sample of households for differential testing (tax year 2025).

    python gen_households.py N out.json [seed] [profile]

profile "common" (default) varies the features below; profile "hard" adds the 2025 changes and the less common
provisions: married filing separately and qualifying surviving spouses, blindness, student and adult dependents,
qualified tips and overtime (§§224, 225), car-loan interest (§163(h)(4)), IRA, HSA, student-loan and educator
adjustments, tax-exempt interest, the saver's credit, the American opportunity credit, and high incomes with large gains
(AMT, NIIT, the 20% rate). Some of these are outside what Tax-Calculator computes itself; compare.py marks them.

Only features every reference calculator models are varied: filing status, ages, dependents, wages (both spouses),
self-employment income, interest, dividends, capital gains, pensions, Social Security, unemployment, property tax,
mortgage interest, cash charity, medical expenses and child care. Everything else is zero.
"""
import json, random, sys

N = int(sys.argv[1]); out = sys.argv[2]; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 2025
PROFILE = sys.argv[4] if len(sys.argv) > 4 else "common"
R = random.Random(seed)

ZERO = dict(seIncome=0, taxableInterest=0, taxExemptInterest=0, ordinaryDividends=0, qualifiedDividends=0,
            shortTermGains=0, longTermGains=0, iraDistributions=0, pensions=0, socialSecurity=0, unemployment=0,
            otherIncome=0, qbi=0, iraContributions=0, activeParticipant=False, hsaContributions=0, studentLoanInterest=0,
            educatorExpenses=0, qualifiedTips=0, qualifiedOvertime=0, carLoanInterest=0, stateLocalTaxes=0,
            mortgageInterest=0, charitableCash=0, medicalExpenses=0, childCareExpenses=0, qualifiedTuition=[],
            retirementContributions=0, marketplacePremium=0, benchmarkPremium=0, canBeClaimedAsDependent=False)


def money(scale):
    """Heavy-tailed whole-dollar amount around `scale`."""
    return int(round(R.lognormvariate(0, 1.0) * scale))


def household(i):
    filing = R.choices(["single", "mfj", "hoh"], [0.42, 0.43, 0.15])[0]
    older = R.random() < 0.2
    age = R.randint(66, 85) if older else R.randint(19, 64)
    head = {"age": age, "blind": False}
    spouse = {"age": max(19, age + R.randint(-5, 5)), "blind": False} if filing == "mfj" else None
    ndep = 0 if (older or (filing == "single")) else R.choices([0, 1, 2, 3], [0.3, 0.3, 0.28, 0.12])[0]
    if filing == "hoh" and ndep == 0:
        ndep = 1
    deps = [{"age": R.randint(0, 18), "ssn": True, "student": False, "disabled": False, "monthsWithTaxpayer": 12}
            for _ in range(ndep)]
    h = dict(ZERO, filing=filing, head=head, spouse=spouse, dependents=deps)
    band = R.choices([8000, 25000, 60000, 140000, 400000], [0.15, 0.3, 0.3, 0.18, 0.07])[0]
    w1 = 0 if older and R.random() < 0.7 else money(band)
    w2 = money(band * 0.7) if (filing == "mfj" and R.random() < 0.6) else 0
    h["wages"], h["wagesSpouse"] = w1 + w2, w2
    if R.random() < 0.12:
        h["seIncome"] = money(band * 0.5)
    if R.random() < 0.35:
        h["taxableInterest"] = money(800)
    if R.random() < 0.25:
        od = money(2500); h["ordinaryDividends"] = od; h["qualifiedDividends"] = int(od * R.choice([0.6, 0.8, 1.0]))
    if R.random() < 0.15:
        h["longTermGains"] = money(8000)
    if R.random() < 0.05:
        h["shortTermGains"] = money(2000)
    if older:
        h["socialSecurity"] = money(22000)
        if R.random() < 0.5:
            h["pensions"] = money(18000)
    if R.random() < 0.04:
        h["unemployment"] = money(5000)
    if R.random() < 0.35:
        h["stateLocalTaxes"] = money(5000)        # property tax only (households are placed in a no-income-tax state)
        h["mortgageInterest"] = money(9000) if R.random() < 0.7 else 0
        h["charitableCash"] = money(2500) if R.random() < 0.6 else 0
        h["medicalExpenses"] = money(4000) if R.random() < 0.2 else 0
    if deps and R.random() < 0.3 and any(d["age"] < 13 for d in deps):
        h["childCareExpenses"] = money(4000)
    return h


def hard(i):
    h = household(i)
    R2 = R
    if R2.random() < 0.12:                       # married filing separately: one spouse's return, no spouse fields
        h.update(filing="mfs", spouse=None, wagesSpouse=0, socialSecurity=0, pensions=h["pensions"])
    elif R2.random() < 0.03 and h["dependents"]:  # qualifying surviving spouse with a dependent child
        h.update(filing="qss", spouse=None, wages=h["wages"] - h["wagesSpouse"], wagesSpouse=0)
    if R2.random() < 0.04:
        h["head"]["blind"] = True
    if h["spouse"] and R2.random() < 0.04:
        h["spouse"]["blind"] = True
    if h["filing"] in ("mfj", "hoh", "qss") and R2.random() < 0.25:   # an older child: 17-23, a student when 19+
        a = R2.randint(17, 23)
        h["dependents"].append({"age": a, "ssn": True, "student": a >= 19 or R2.random() < 0.5, "disabled": False,
                                "monthsWithTaxpayer": 12})
    head_w = h["wages"] - h["wagesSpouse"]
    if head_w > 0 and R2.random() < 0.15:
        h["qualifiedTips"] = min(head_w, money(6000))
    if head_w > 0 and R2.random() < 0.15:
        h["qualifiedOvertime"] = min(head_w // 3, money(4000))
    if R2.random() < 0.12:
        h["carLoanInterest"] = money(1800)
    earned = head_w + max(0, h["seIncome"])
    if earned > 2000 and R2.random() < 0.15:
        h["iraContributions"] = min(earned // 2, R2.choice([1000, 2000, 3500, 7000]))
        h["retirementContributions"] = h["iraContributions"]   # §25B(d)(1)(A): IRA contributions qualify
    if earned > 0 and R2.random() < 0.08:
        h["hsaContributions"] = min(4300, money(2000))
    if R2.random() < 0.10:
        h["studentLoanInterest"] = min(2500, money(1200))
    if head_w > 0 and R2.random() < 0.05:
        h["educatorExpenses"] = R2.choice([150, 300])
    if R2.random() < 0.06:
        h["taxExemptInterest"] = money(1500)
    students = [d for d in h["dependents"] if d.get("student")]
    if students and R2.random() < 0.6:
        h["qualifiedTuition"] = [R2.choice([1500, 2500, 4000, 9000]) for _ in students[:1]]
    if R2.random() < 0.03:                        # high income with large gains: 20% rate, NIIT, AMT
        h["wages"] += money(250000); h["longTermGains"] += money(150000)
        h["qualifiedDividends"] += 20000; h["ordinaryDividends"] += 20000
        h["stateLocalTaxes"] = max(h["stateLocalTaxes"], money(30000))
    if h["filing"] == "mfs":
        h["socialSecurity"] = 0                  # whether the spouses lived apart is not recorded
    return h


hs = [(hard if PROFILE == "hard" else household)(i) for i in range(N)]
json.dump(hs, open(out, "w", encoding="utf-8"))
print(f"wrote {len(hs)} households to {out}")
