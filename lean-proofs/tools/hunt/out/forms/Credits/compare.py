"""Statute vs form, tax year 2025: Forms 8839, 2441, 8863, 8880, 8962, EIC worksheets.
Each pair of functions is written from its own text. Prints every class of difference with an example.
Run: python -I compare.py
"""
import itertools, json, math
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

grid = 0
diffs = defaultdict(list)   # key -> list of (inputs, statute, form)

def rec(key, inp, s, f, tol=0.0):
    if abs(s - f) > tol:
        diffs[key].append((inp, round(s, 2), round(f, 2)))

def r3(x):   # "rounded to at least three places"
    return float(Decimal(str(x)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))

# ---------------------------------------------------------------- Form 8839 / s.23
LIM, PH0, PHW, REF = 17280, 259190, 40000, 5000

def s23_statute(exp, magi, carry_in, limit, mfs_carry_only=False, carry_refundable=True):
    """s.23(a)(1),(a)(4),(b),(c). One credit per taxpayer; (a)(4) caps the refundable part at $5,000 of
    'the credit allowed under paragraph (1)'. carry_refundable=True: the carry from 2024 arose under the
    pre-2025 (c)(1), which added it 'to the credit allowable under subsection (a)' for 2025."""
    ratio = min(1.0, max(0.0, (magi - PH0) / PHW))
    cur = sum(min(e, LIM) for e in exp) * (1 - ratio)          # (b)(1) then (b)(2), without regard to (c)
    if mfs_carry_only:                                           # (f)(1) -> s.21(e)(2): joint return or nothing
        return dict(refund=0.0, nonref=0.0, carry_out=carry_in)
    pool = cur + (carry_in if carry_refundable else 0)
    refund = min(pool, REF)
    nonref_avail = cur + carry_in - refund
    used = min(nonref_avail, limit)
    return dict(refund=refund, nonref=used, carry_out=nonref_avail - used)

def f8839_form(exp, magi, carry_in, limit, mfs_carry_only=False):
    l6 = [min(LIM, e) for e in exp]                              # lines 2-6 (no prior-year claim)
    l9 = min(1.0, r3((magi - PH0) / PHW)) if magi > PH0 else 0.0  # lines 8-9
    l11a = [x - x * l9 for x in l6]                              # lines 10-11a
    l11b = [min(x, 5000) for x in l11a]                          # line 11b, per child
    l13 = sum(l11b)                                              # 11c -> 13
    l14 = max(0.0, sum(l11a) - l13)                              # 12 - 13
    l16 = l14 + carry_in                                         # line 15 added after the refundable part
    l18 = min(l16, limit)                                        # line 17 = credit limit worksheet
    return dict(refund=l13, nonref=l18, carry_out=l16 - l18)     # MFS filer may claim a carryforward

for nkids, e, magi, carry, limit in itertools.product(
        [0, 1, 2, 3], [0, 2000, 5000, 8000, 17280, 25000],
        [50000, 259190, 269190, 279190, 289200, 299190, 320000],
        [0, 3000, 8000, 20000], [0, 1500, 6000, 40000]):
    if nkids == 0 and (e or not carry): continue
    exp = [e] * nkids
    for variant in ("carry refundable (pre-2025 (c)(1))", "carry nonrefundable (current (c)(1))"):
        grid += 1
        s = s23_statute(exp, magi, carry, limit, carry_refundable=variant.startswith("carry refundable"))
        f = f8839_form(exp, magi, carry, limit)
        inp = dict(children=nkids, expenses_each=e, magi=magi, carry_in=carry, s26_limit=limit, reading=variant)
        tol = 0.0005 * LIM * max(nkids, 1) + 0.01                # stated 3-place rounding of line 9
        if abs(s["refund"] - f["refund"]) > tol:
            k = "8839 refundable: " + ("per-child $5,000 (form more)" if f["refund"] > s["refund"]
                                       else "carryforward kept out of the refundable part (statute more)")
            rec(k, inp, s["refund"], f["refund"], tol)
        rec("8839 total credit this year (refundable + nonrefundable)", inp,
            s["refund"] + s["nonref"], f["refund"] + f["nonref"], tol)
    grid += 1
    s = s23_statute(exp, magi, carry, limit, mfs_carry_only=True)
    f = f8839_form([], magi, carry, limit, mfs_carry_only=True)
    if carry:
        rec("8839 carryforward on a married-separate return", dict(carry_in=carry, s26_limit=limit),
            s["nonref"], f["nonref"])

# ---------------------------------------------------------------- Form 2441 / s.21 (2025 text: 35% -> 20%)
def pct21_statute(agi):
    over = max(0, agi - 15000)
    return max(20, 35 - math.ceil(over / 2000)) / 100           # 1 point per $2,000 or fraction thereof

T2441 = [(15000, .35), (17000, .34), (19000, .33), (21000, .32), (23000, .31), (25000, .30), (27000, .29),
         (29000, .28), (31000, .27), (33000, .26), (35000, .25), (37000, .24), (39000, .23), (41000, .22),
         (43000, .21), (float("inf"), .20)]
def pct21_form(agi):
    for hi, d in T2441:
        if agi <= hi: return d

def s21_statute(agi, exp, n, ei, ei_sp, married, benefits, student_months=0, limit=1e9,
                late_exp=0, late_room=0, prior_agi=None):
    cap = (3000 if n == 1 else 6000) - benefits                  # (c)
    earned = min(ei, ei_sp) if married else ei                   # (d)(1); (d)(2) deems income only for 'a spouse'
    if married and student_months:
        earned = min(ei, max(ei_sp, (250 if n == 1 else 500) * student_months))
    base = max(0, min(exp, cap, earned))
    late = min(late_exp, late_room)                              # reg 1.21-1(a)(3): credit in year of payment
    return min((base + late) * pct21_statute(agi), limit)        # (a)(2): AGI 'for the taxable year'

def f2441_form(agi, exp, n, ei, ei_sp, married, benefits, student_months=0, limit=1e9,
               late_exp=0, late_room=0, prior_agi=None):
    l27 = 3000 if n == 1 else 6000
    l3 = min(exp, l27) if not benefits else min(max(0, l27 - benefits), exp)   # lines 27-31
    deemed = (250 if n == 1 else 500) * student_months
    l4 = max(ei, deemed) if (student_months and not married) else ei   # instr.: rules "also apply to you"
    l5 = (max(ei_sp, deemed) if student_months else ei_sp) if married else l4
    l6 = max(0, min(l3, l4, l5))
    l9a = l6 * pct21_form(agi)
    l9b = min(late_exp, late_room) * pct21_form(prior_agi if prior_agi is not None else agi)  # Worksheet A
    return min(l9a + l9b, limit)

for agi in list(range(0, 50001, 250)) + [15001, 16999, 17001, 43001]:
    for exp, n, ei, ei_sp, married, ben in itertools.product([1000, 3000, 7000], [1, 2], [0, 2500, 40000],
                                                               [0, 2500, 40000], [False, True], [0, 2000, 5000]):
        grid += 1
        a = (agi, exp, n, ei, ei_sp, married, ben)
        rec("2441 basic credit", dict(zip("agi exp n ei ei_sp married benefits".split(), a)),
            s21_statute(*a), f2441_form(*a))
for agi, n, months in itertools.product([12000, 30000, 60000], [1, 2], [5, 9, 12]):
    grid += 1
    a = (agi, 6000, n, 0, 0, False, 0, months)
    rec("2441 unmarried full-time student with no earnings: deemed $250/$500 a month",
        dict(agi=agi, n=n, student_months=months, married=False, earned=0), s21_statute(*a), f2441_form(*a))
for agi, prior in itertools.product([14000, 30000, 60000], [14000, 30000, 60000]):
    grid += 1
    kw = dict(late_exp=2000, late_room=2000, prior_agi=prior)
    a = (agi, 0, 2, 40000, 40000, False, 0)
    rec("2441 Worksheet A: 2024 expenses paid in 2025 use the 2024 percentage",
        dict(agi_2025=agi, agi_2024=prior, late_expenses=2000), s21_statute(*a, **kw), f2441_form(*a, **kw))

# ---------------------------------------------------------------- Form 8863 / s.25A
def s25A_statute(aotc_exp, llc_exp, magi, joint, kiddie=False):
    a = sum(min(e, 2000) + 0.25 * max(0, min(e, 4000) - 2000) for e in aotc_exp)
    l = 0.20 * min(llc_exp, 10000)
    red = min(1.0, max(0.0, (magi - (160000 if joint else 80000)) / (20000 if joint else 10000)))
    a, l = a * (1 - red), l * (1 - red)
    ref = 0 if kiddie else 0.40 * a
    return ref, a - ref + l

def f8863_form(aotc_exp, llc_exp, magi, joint, kiddie=False):
    l1 = 0
    for e in aotc_exp:
        l27 = min(e, 4000); l28 = max(0, l27 - 2000); l1 += l27 if l28 == 0 else 2000 + 0.25 * l28
    l2, l5 = (180000, 20000) if joint else (90000, 10000)
    l4 = l2 - magi
    if l4 <= 0: return 0.0, 0.0
    l6 = 1.0 if l4 >= l5 else r3(l4 / l5)
    l7 = l1 * l6
    l8 = 0 if kiddie else 0.40 * l7
    l12 = 0.20 * min(llc_exp, 10000)
    return l8, (l7 - l8) + l12 * l6

for exps, llc, magi, joint, kid in itertools.product(
        [[], [1500], [4000], [4000, 2600], [9000, 4000, 4000]], [0, 3000, 12000],
        list(range(70000, 190001, 1250)) + [80001, 89999, 160001, 179999], [False, True], [False, True]):
    grid += 1
    s, f = s25A_statute(exps, llc, magi, joint, kid), f8863_form(exps, llc, magi, joint, kid)
    tol = 0.0005 * (2500 * max(len(exps), 1) + 2000) + 0.01
    rec("8863", dict(aotc=exps, llc=llc, magi=magi, joint=joint, kiddie=kid), sum(s), sum(f), tol)
    rec("8863 refundable part", dict(aotc=exps, magi=magi, joint=joint, kiddie=kid), s[0], f[0], tol)

# ---------------------------------------------------------------- Form 8880 / s.25B
J = (47500, 51000, 79000)            # s.25B(b)(1) amounts as indexed for 2025
def s25B_statute(agi, status, contrib, dist, inherited_ira_dist=0):
    k = {"joint": 1.0, "hoh": 0.75}.get(status, 0.5)
    a, b, c = (x * k for x in J)
    p = .5 if agi <= a else .2 if agi <= b else .1 if agi <= c else 0
    return p * sum(min(2000, max(0, x - dist - inherited_ira_dist)) for x in contrib)   # (d)(2): any IRA

ROWS = [(23750, .5, .5, .5), (25500, .5, .5, .2), (35625, .5, .5, .1), (38250, .5, .2, .1), (39500, .5, .1, .1),
        (47500, .5, .1, 0), (51000, .2, .1, 0), (59250, .1, .1, 0), (79000, .1, 0, 0), (float("inf"), 0, 0, 0)]
def f8880_form(agi, status, contrib, dist, inherited_ira_dist=0):
    col = {"joint": 1, "hoh": 2}.get(status, 3)
    for row in ROWS:
        if agi <= row[0]:
            l9 = row[col]; break
    return l9 * sum(min(2000, max(0, x - dist)) for x in contrib)   # line 4 leaves out inherited-IRA payouts

for agi, st, contrib, dist, inh in itertools.product(
        list(range(15000, 85001, 250)) + [23751, 25501, 35626, 38251, 39501, 47501, 51001, 59251, 79001],
        ["joint", "hoh", "single", "mfs"], [[500], [2000], [3000, 1000]], [0, 800], [0, 2500]):
    if st != "joint" and len(contrib) > 1: continue
    grid += 1
    key = "8880" if not inh else "8880 line 4: inherited-IRA distributions left out of the testing-period reduction"
    rec(key, dict(agi=agi, status=st, contributions=contrib, other_dist=dist, inherited_ira_dist=inh),
        s25B_statute(agi, st, contrib, dist, inh), f8880_form(agi, st, contrib, dist, inh))

# ---------------------------------------------------------------- Form 8962 / s.36B (2025: (b)(3)(A)(iii) table)
def fpl(n): return 15060 + 5380 * (n - 1)       # 2024 guidelines, 48 States and DC
TIERS = [(150, 200, 0.0, 2.0), (200, 250, 2.0, 4.0), (250, 300, 4.0, 6.0), (300, 400, 6.0, 8.5)]
def s36B_statute(agi, n, slcsp, prem, housing_deduction=0):
    hi = agi                                         # (d)(2)(B): AGI + amounts *excluded* under s.911 (+ ...)
    pct_fpl = 100 * hi / fpl(n)
    if pct_fpl < 100: return 0.0
    ap = 0.0 if pct_fpl <= 150 else 8.5
    for lo, up, a, b in TIERS:
        if lo <= pct_fpl < up: ap = a + (b - a) * (pct_fpl - lo) / (up - lo)   # linear sliding scale
    return 12 * min(prem, max(0, slcsp - ap / 100 * hi / 12))

def table2(p):
    if p <= 150: return 0.0
    if p >= 400: return 0.085
    if p <= 300: return round(0.0004 * (p - 150), 4)
    return ((6000 + 25 * (p - 300) + 5) // 10) / 10000   # .06025 -> 0.0603, as printed
def f8962_form(agi, n, slcsp, prem, housing_deduction=0):
    l3 = agi + housing_deduction                     # Worksheet 1-1 line 3: Form 2555 lines 45 *and 50*
    l4 = fpl(n)
    l5 = 401 if l3 > 4 * l4 else int(100 * l3 / l4)  # Worksheet 2: drop the decimals
    if l5 < 100: return 0.0
    l8a = round(l3 * table2(l5))
    return min(12 * prem, max(0, 12 * slcsp - l8a))  # line 11

big36 = 0
for n, mult, slcsp, prem, hd in itertools.product(
        [1, 2, 4, 6], [x / 1000 for x in range(1000, 4500, 7)], [450, 900, 1800], [400, 2500], [0, 12000]):
    grid += 1
    agi = round(mult * fpl(n))
    s, f = s36B_statute(agi, n, slcsp, prem, hd), f8962_form(agi, n, slcsp, prem, hd)
    if hd:
        rec("8962 Worksheet 1-1 line 3: s.911 housing deduction (Form 2555 line 50) added to modified AGI",
            dict(agi=agi, family=n, slcsp_month=slcsp, housing_deduction=hd), s, f, 60)
    else:
        rec("8962 line 5 / Table 2: whole-percent truncation of the poverty-line percentage",
            dict(agi=agi, family=n, pct_fpl=round(100 * agi / fpl(n), 2), slcsp_month=slcsp), s, f, 5)
        big36 = max(big36, f - s)

# ---------------------------------------------------------------- EIC worksheets / s.32
EIC = {0: (.0765, 8490, .0765, 10620, 17730), 1: (.34, 12730, .1598, 23350, 30470),
       2: (.40, 17880, .2106, 23350, 30470), 3: (.45, 17880, .2106, 23350, 30470)}
def s32_formula(x_ei, x_agi, kids, joint):
    c, eamt, p, ps, pj = EIC[kids]
    start = pj if joint else ps
    return max(0.0, min(c * min(x_ei, eamt), c * eamt - p * max(0, max(x_agi, x_ei) - start)))
def mid(x): return (x // 50) * 50 + 25                # s.32(f): $50 brackets, credit at the bracket midpoint
def s32_statute(ei, agi, kids, joint, sep_agreement_only=False):
    if ei <= 0: return 0
    c, eamt, p, ps, pj = EIC[kids]; start = pj if joint else ps
    t = lambda x: round(max(0.0, min(c * min(mid(x), eamt), c * eamt - p * max(0, mid(x) - start))))
    return min(t(ei), t(max(agi, ei)))                # (a)(2)(B) uses AGI or, if greater, earned income
def eic_form(ei, agi, kids, joint, sep_agreement_only=False):
    if sep_agreement_only: return 0                   # form: must be "legally separated according to your state law"
    if ei <= 0: return 0
    c, eamt, p, ps, pj = EIC[kids]; start = pj if joint else ps
    t = lambda x: round(max(0.0, min(c * min(mid(x), eamt), c * eamt - p * max(0, mid(x) - start))))
    l2 = t(ei)                                        # Worksheet A line 2
    if agi == ei or agi < start: return l2            # lines 4-5
    return min(l2, t(agi))                            # line 6

for kids, joint, ei, dagi in itertools.product([0, 1, 2, 3], [False, True], range(1, 70000, 487),
                                                [-3000, 0, 30, 2500, 15000]):
    grid += 1
    agi = max(0, ei + dagi)
    rec("EIC worksheet vs s.32 table", dict(kids=kids, joint=joint, earned=ei, agi=agi),
        s32_statute(ei, agi, kids, joint), eic_form(ei, agi, kids, joint))
    rec("EIC table vs exact s.32(a) formula (statutory $50 brackets, s.32(f))",
        dict(kids=kids, joint=joint, earned=ei, agi=agi), s32_formula(ei, agi, kids, joint),
        s32_statute(ei, agi, kids, joint), 0.2106 * 25 + 0.45 * 25 + 1)
for kids, ei in itertools.product([1, 2, 3], [9000, 18000, 30000]):
    grid += 1
    rec("EIC married-separate filer with a written separation agreement or support decree but not 'legally separated'",
        dict(kids=kids, earned=ei, agi=ei), s32_statute(ei, ei, kids, False, True), eic_form(ei, ei, kids, False, True))

out = {"grid_points": grid, "classes": {}}
for k, v in diffs.items():
    gap = [f - s for _, s, f in v]
    out["classes"][k] = dict(count=len(v), form_minus_statute_min=round(min(gap), 2),
                             form_minus_statute_max=round(max(gap), 2),
                             example=max(v, key=lambda t: abs(t[2] - t[1])))
out["max_8962_truncation_gain"] = round(big36, 2)
print(json.dumps(out, indent=1, default=str))
