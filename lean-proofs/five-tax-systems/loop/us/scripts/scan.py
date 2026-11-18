"""Novel search, part 1: effective marginal rates by archetype (TY2025 model).

For each archetype and income x (0 .. 700k, $250 grid) the household's burden is netTax (+ employee FICA when the
income is wages). Reports, per archetype: the $1,000-step marginal rate peaks, every band where it exceeds 60%, and
every point where it exceeds 100% (net income falls). Output ../runs/scan_mtr.json.
"""
import json, sys
from model import H, run, kid, fica

S = lambda **kw: H(filing="single", **kw)
J = lambda **kw: H(filing="mfj", **kw)
HH = lambda **kw: H(filing="hoh", **kw)
O = lambda a: {"age": a, "blind": False}

A = {
    "single_wages": (lambda x: S(wages=x), True),
    "hoh1_wages": (lambda x: HH(wages=x, dependents=[kid(6)]), True),
    "hoh2_wages": (lambda x: HH(wages=x, dependents=[kid(4), kid(9)]), True),
    "hoh3_wages": (lambda x: HH(wages=x, dependents=[kid(3), kid(7), kid(12)]), True),
    "mfj0_wages": (lambda x: J(wages=x, wagesSpouse=x // 2), True),
    "mfj2_wages_1earner": (lambda x: J(wages=x, dependents=[kid(4), kid(9)]), True),
    "mfj2_wages_care": (lambda x: J(wages=x, wagesSpouse=x // 2, dependents=[kid(2), kid(5)], childCareExpenses=8000), True),
    "hoh2_care_college": (lambda x: HH(wages=x, dependents=[kid(9), kid(19, student=True)], childCareExpenses=3000,
                                       qualifiedTuition=[4000]), True),
    "single67_ss20_ira": (lambda x: S(head=O(67), socialSecurity=20000, iraDistributions=x), False),
    "single67_ss40_ira": (lambda x: S(head=O(67), socialSecurity=40000, iraDistributions=x), False),
    "mfj67_ss40_ira": (lambda x: J(head=O(67), spouse=O(67), socialSecurity=40000, iraDistributions=x), False),
    "mfj67_ss60_ltcg": (lambda x: J(head=O(67), spouse=O(67), socialSecurity=60000, pensions=30000,
                                    longTermGains=x), False),
    "single_tips30": (lambda x: S(wages=x, qualifiedTips=min(x * 3 // 10, 25000)), True),
    "single66_tips30": (lambda x: S(head=O(66), wages=x, qualifiedTips=min(x * 3 // 10, 25000)), True),
    "mfj2_overtime10": (lambda x: J(wages=x, dependents=[kid(5), kid(8)], qualifiedOvertime=min(x // 10, 25000)), True),
    "single_carloan8k": (lambda x: S(wages=x, carLoanInterest=8000), True),
    "mfj_salt60_mort20": (lambda x: J(wages=x, wagesSpouse=x // 2, stateLocalTaxes=60000, mortgageInterest=20000), True),
    "single_salt40": (lambda x: S(wages=x, stateLocalTaxes=40000, mortgageInterest=15000), True),
    "single60_marketplace": (lambda x: S(head=O(60), wages=x, marketplacePremium=13000, benchmarkPremium=13000), True),
    "mfj64_marketplace": (lambda x: J(head=O(64), spouse=O(64), wages=x, marketplacePremium=30000,
                                      benchmarkPremium=30000), True),
    "mfj_saver4k": (lambda x: J(wages=x, wagesSpouse=x // 2, iraContributions=4000, retirementContributions=4000), True),
    "single_se": (lambda x: S(seIncome=x), False),
    "mfj_se_sstb": (lambda x: J(seIncome=x, facts={"qbiSstb": True}), False),
    "mfj_se_nonsstb_nowages": (lambda x: J(seIncome=x), False),
    "hoh1_wages_interest": (lambda x: HH(wages=25000, dependents=[kid(6)], taxableInterest=x), False),
    "mfj2_senior_tips": (lambda x: J(head=O(66), spouse=O(40), wages=x, qualifiedTips=min(x // 5, 25000),
                                     dependents=[kid(10), kid(14)]), True),
    "single_ltcg_on_40k": (lambda x: S(wages=40000, longTermGains=x), False),
    "single66_ltcg_on_40k": (lambda x: S(head=O(66), pensions=40000, longTermGains=x), False),
}

STEP, TOP, D = 250, 700000, 1000


def main(names=None):
    out = {}
    names = names or list(A)
    for n in names:
        f, wages = A[n]
        xs = list(range(0, TOP + 1, STEP))
        cases = [f(x) for x in xs] + [f(x + D) for x in xs]
        rs = run(cases)
        m = len(xs)
        burden = lambda x, r: r["netTax"] + (fica(x) if wages else 0)
        rates = []
        for i, x in enumerate(xs):
            b0, b1 = burden(x, rs[i]), burden(x + D, rs[m + i])
            rates.append((round((b1 - b0) / D, 4), x))
        hi = [x for r, x in rates if r > 0.6]
        over = [(r, x) for r, x in rates if r > 1.0]
        bands = []
        for x in hi:
            if bands and x - bands[-1][1] <= STEP:
                bands[-1][1] = x
            else:
                bands.append([x, x])
        top = sorted(rates, reverse=True)[:5]
        out[n] = dict(top=top, bands_over_60=bands[:40], over_100=over[:40])
        print(f"{n:24} top={top[:3]} bands>60%={bands[:6]} >100%={len(over)}")
    json.dump(out, open("../runs/scan_mtr.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
