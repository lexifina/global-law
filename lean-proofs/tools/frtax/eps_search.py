"""Find returns where M's rounding margin (my_arr: floor(x + 0.5 + 0.00005)) and exact half-up rounding differ:
an amount whose exact fraction is in [0.49995, 0.5). Target: the effective rate of art. 197 C for a single
salaried person with flat-levy services income (5TB): tax(tot) * rni / tot."""
from fractions import Fraction as F
import sys
P = {2024: (11497, 29315, 83823, 180294, 504, 14426), 2025: (11600, 29579, 84577, 181917, 509, 14555)}
def rnd(x):  # half up
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)
def scale(year, r):
    b1, b2, b3, b4 = P[year][:4]
    t = F(0)
    for lo, hi, rate in ((b1, b2, 11), (b2, b3, 30), (b3, b4, 41), (b4, None, 45)):
        top = r if hi is None else min(r, hi)
        if top > lo:
            t += F(rate, 100) * (top - lo)
    return rnd(t)
found = []
for year in (2024, 2025):
    mn, mx = P[year][4], P[year][5]
    for s in range(20000, 120000, 7):
        allow = min(s, max(mn, min(mx, rnd(F(s, 10)))))
        rni = s - allow
        for v in range(2000, 60000, 13):
            vl = v - min(v, max(305, rnd(F(v, 2))))
            tot = rni + vl
            T = scale(year, tot)
            x = F(T * rni, tot)
            frac = x - (x.numerator // x.denominator)
            if F(49995, 100000) <= frac < F(1, 2):
                found.append((year, s, v, rni, tot, T, float(frac)))
                if len(found) >= 12:
                    break
        if len(found) >= 12 * (1 + (year == 2025)):
            break
for f in found:
    print(*f)
