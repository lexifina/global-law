"""Hypothesis check: are the brochure's Table 4 thresholds computed without rounding (exact arithmetic)?"""
from fractions import Fraction as F
import json, sys
P = {2024: dict(b=(11497, 29315, 83823, 180294), half=1791, t1=4224, L=1069, comp=1785, widow=1993),
     2025: dict(b=(11600, 29579, 84577, 181917), half=1807, t1=4262, L=1079, comp=1801, widow=2011)}
def tax(p, r, n):
    b = p["b"]; x = F(r) / n; t = F(0)
    sl = [(b[0], b[1], 11), (b[1], b[2], 30), (b[2], b[3], 41), (b[3], None, 45)]
    for lo, hi, rate in sl:
        top = x if hi is None else min(x, hi)
        if top > lo: t += (top - lo) * rate / 100
    return t * n
def first(p, n, ref, cap, compl, rounded):
    def f(r):
        full, rf = tax(p, r, F(n)), tax(p, r, F(ref))
        if rounded:
            full, rf = round(full + F(1, 10**9)), round(rf + F(1, 10**9))
        capped = max(full, rf - cap)
        c = min(compl, capped - full) if capped > full else 0
        return capped - c > full
    lo, hi = 0, 400000
    while lo < hi:
        m = (lo + hi) // 2
        if f(m): hi = m
        else: lo = m + 1
    return lo
rows = json.load(open(sys.argv[1]))
for ed, year in (("2025", 2024), ("2026", 2025)):
    p = P[year]
    for x in rows[ed]:
        if x["table"] != 4: continue
        row, n = x["row"], F(x["parts"]).limit_denominator(4)
        ref = 2 if row.startswith("M") else 1
        inv = row.endswith("inv") or row == "Inv_single"
        extra = n - ref - (F(1, 2) if inv else 0)
        if row == "L": cap, compl = p["L"], 0
        elif row.startswith("T"): cap, compl = p["t1"] + (extra - 1) * 2 * p["half"], 0
        else: cap, compl = extra * 2 * p["half"], 0
        if row.startswith("V"): compl += p["widow"]
        if inv: cap += p["half"]; compl += p["comp"]
        ex, rd = first(p, n, ref, cap, compl, False), first(p, n, ref, cap, compl, True)
        print(ed, row, float(n), "printed", x["printed"], "exact", ex, "rounded", rd, "| lean_B", x["lean_B"], "ok_exact" if ex == x["printed"] else "")
