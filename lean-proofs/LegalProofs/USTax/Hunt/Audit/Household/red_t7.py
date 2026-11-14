"""T7. H6 recomputed from the statute text (26 U.S.C. 1, 2(b), 23, 24, 26, 32, 63; 2025 indexed figures).
Not a translation of the Lean file: each return is worked as a tax return, top to bottom."""
from fractions import Fraction as F

BR = {  # 2025 rate schedules, Rev. Proc. 2024-40 as amended by Pub. L. 119-21
    "single": [(11925, 10), (48475, 12), (103350, 22), (197300, 24), (250525, 32), (626350, 35), (None, 37)],
    "hoh": [(17000, 10), (64850, 12), (103350, 22), (197300, 24), (250500, 32), (626350, 35), (None, 37)],
    "joint": [(23850, 10), (96950, 12), (206700, 22), (394600, 24), (501050, 32), (751600, 35), (None, 37)],
}
STD = {"single": 15750, "hoh": 23625, "joint": 31500}
LIMIT, REFUND, PHASE = 17280, 5000, 259190   # sec. 23(b)(1), (a)(4), (b)(2) for 2025

def tax(status, ti):
    t, lo = F(0), 0
    for hi, r in BR[status]:
        top = ti if hi is None else min(ti, hi)
        if top > lo:
            t += F(top - lo) * r / 100
        if hi is None or ti <= hi:
            break
        lo = hi
    return int(t)  # whole dollars, rounded down

def eic_one_child(earned, agi, joint):
    # sec. 32(b): 34% of earned income up to 12,730; less 15.98% of income over 23,350 (30,470 joint)
    start = 30470 if joint else 23350
    full = F(34, 100) * 12730
    a = F(34, 100) * min(earned, 12730)
    b = max(F(0), full - F(1598, 10000) * max(0, max(agi, earned) - start))
    return int(min(a, b))

def one_return(status, wages, child, adopt_taken, refund_cap=REFUND):
    """Returns (net tax, refundable adoption, nonrefundable adoption used, carryforward, tax left after sec. 24)."""
    agi = wages
    t = tax(status, max(0, agi - STD[status]))
    left = t
    # sec. 24: 2,200 a child; nonrefundable against tax, the rest refundable up to 1,700 and 15% of earned income over 2,500
    ctc = 2200 if child else 0
    ctc_used = min(ctc, left); left -= ctc_used
    actc = min(ctc - ctc_used, 1700, max(0, (wages - 2500) * 15 // 100)) if child else 0
    eic = eic_one_child(wages, agi, status == "joint") if child else 0   # childless: wages too high at these facts
    # sec. 23: (b)(2) phaseout nil below 259,190; (a)(4) refundable; rest against tax after the other credits ((c)(1))
    assert agi <= PHASE
    ref = min(refund_cap, adopt_taken)
    non = min(adopt_taken - ref, left); left -= non
    carry = adopt_taken - ref - non
    return t - ctc_used - actc - eic - ref - non, ref, non, carry, left

def six_years(rets, later_room, disc=F(0)):
    """rets: year-one results per return; later_room: tax left after other credits in each later year (same facts)."""
    y1 = sum(r[0] for r in rets)
    used_by_year = [0] * 5
    for r, room in zip(rets, later_room):
        c = r[3]
        for i in range(5):               # sec. 23(c)(2): five years after the year the credit arose
            u = min(c, room); c -= u; used_by_year[i] += u
    expired = sum(r[3] for r in rets) - sum(used_by_year)
    pv = sum(F(u) / (1 + disc) ** (i + 1) for i, u in enumerate(used_by_year))
    return y1, used_by_year, expired, pv

A, B, EXP = 38000, 34000, 20000

def unmarried(pct_a, a_claims=True, refund_caps=(REFUND, REFUND)):
    lim = min(EXP, LIMIT)
    share_a = lim * pct_a // 100             # Notice 97-9: one limit, divided
    share_b = lim * (100 - pct_a) // 100
    sa, sb = ("hoh", "single") if a_claims else ("single", "hoh")
    ra = one_return(sa, A, a_claims, share_a, refund_caps[0])
    rb = one_return(sb, B, not a_claims, share_b, refund_caps[1])
    room = [one_return(sa, A, a_claims, 0)[4], one_return(sb, B, not a_claims, 0)[4]]
    base_later = one_return(sa, A, a_claims, 0)[0] + one_return(sb, B, not a_claims, 0)[0]
    return [ra, rb], room, base_later

def married():
    r = one_return("joint", A + B, True, min(EXP, LIMIT))
    z = one_return("joint", A + B, True, 0)
    return [r], [z[4]], z[0]

def show(name, rets, room, later):
    y1, used, expired, _ = six_years(rets, room)
    pv4 = six_years(rets, room, F(4, 100))[3]
    nominal = y1 + 5 * later - sum(used)
    credit_y1 = sum(r[1] + r[2] for r in rets)
    print(f"{name:46s} year1 net {y1:7d}  refundable {sum(r[1] for r in rets):5d}  nonref {sum(r[2] for r in rets):5d}"
          f"  carry used {used} expired {expired:5d}  six-year net {nominal:7d}  sec.23 total {credit_y1 + sum(used):5d}"
          f"  PV(4%) of sec.23 {float(credit_y1 + pv4):9.0f}")
    return y1, nominal, credit_y1 + sum(used), credit_y1 + pv4

print("A claims the child and keeps the home (the default's other choices)")
d = show("default: A pays 100%", *unmarried(100))
p = show("PLAN: 50/50", *unmarried(50))
b = show("B pays 100%", *unmarried(0))
s29 = show("A pays 29%", *unmarried(29))
print(f"  plan vs default, year 1: {d[0] - p[0]}   (claimed 6951)")
print(f"  plan vs B pays all, year 1: {b[0] - p[0]};  six years: {b[1] - p[1]} (negative = plan worse)")
print(f"  29/71 vs B pays all, six years nominal: {b[1] - s29[1]}; PV of credit at 4%: {float(s29[3] - b[3]):.0f}")
print("B claims the child and keeps the home")
d2 = show("A pays 100%", *unmarried(100, a_claims=False))
p2 = show("50/50", *unmarried(50, a_claims=False))
s71 = show("A pays 71%", *unmarried(71, a_claims=False))
print(f"  50/50 vs A pays all: year 1 {d2[0] - p2[0]}; six years {d2[1] - p2[1]}")
print(f"  71/29 vs A pays all: year 1 {d2[0] - s71[0]}; six years {d2[1] - s71[1]}; PV of credit at 4%: {float(s71[3] - d2[3]):.0f}")
print("married, joint return")
m = show("joint", *married())
print("closed gap: the $5,000 divided like the limit (sec. 23(i) extended to (a)(4))")
c = show("50/50, 2,500 each", *unmarried(50, refund_caps=(2500, 2500)))
print(f"  plan vs default, year 1: {d[0] - c[0]}  (the part that is not (a)(4))")
print("earlier law: no (a)(4)")
o0 = show("A pays 100%", *unmarried(100, refund_caps=(0, 0)))
o5 = show("50/50", *unmarried(50, refund_caps=(0, 0)))
print(f"  50/50 vs default, year 1: {o0[0] - o5[0]}")
print("2026 indexed amounts (limit 17,670, refundable 5,120 per secondary reports of Rev. Proc. 2025-32), 2025 brackets")
LIMIT = 17670
d6 = unmarried(100, refund_caps=(5120, 5120)); p6 = unmarried(50, refund_caps=(5120, 5120)); b6 = unmarried(0, refund_caps=(5120, 5120))
t = lambda x: sum(r[0] for r in x[0])
print(f"  plan vs default year 1: {t(d6) - t(p6)}; plan vs B pays all year 1: {t(b6) - t(p6)}")
