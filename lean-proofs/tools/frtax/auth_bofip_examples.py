"""Recompute the worked examples of BOI-IR-PAS-20-20-20-20250507 (§140, examples 1-3) under the income-2024
parameters, to see which décote (single or couple) and which rounding of the quarter-part cap the DGFiP used.
Usage: python3 -I harness/auth_bofip_examples.py"""
from fractions import Fraction as F
B = [(0, 11497, 0), (11497, 29315, F(11, 100)), (29315, 83823, F(30, 100)), (83823, 180294, F(41, 100)), (180294, 10**9, F(45, 100))]
HALF = 1791; DEC = {"single": 889, "couple": 1470}; DR = F(4525, 10000)
def arr(x): return int(x + F(1, 2)) if x >= 0 else -int(-x + F(1, 2))
def scale(r):  # tax for one part, exact
    return sum((min(r, hi) - lo) * t for lo, hi, t in B if r > lo)
def tax(R, parts, base_parts, sep_cap):
    t = scale(F(R) / parts) * parts
    t0 = scale(F(R) / base_parts) * base_parts
    cap = 2 * HALF * (F(parts) - base_parts)
    if t0 - t > cap:
        return arr(t0) - arr(cap) if sep_cap else arr(t0 - cap)
    return arr(t)
def decote(t, kind):
    d = arr(DEC[kind] - DR * t)
    return t - max(0, min(d, t))
print("household ex1 (2 parts, 129 600):", tax(129600, 2, 2, True), "BOFiP 25 211")
print("household ex2 (3 parts, 139 600):", tax(139600, 3, 2, True), "BOFiP 24 629")
print("household ex3 (2.5 parts, 114 800):", tax(114800, F(5, 2), 2, True), "/", tax(114800, F(5, 2), 2, False), "BOFiP 18 980")
t1 = tax(21600, 1, 1, True); print("ex1 lower earner 1 part, 21 600: brut", t1, "single décote ->", decote(t1, "single"), "couple décote ->", decote(t1, "couple"), "BOFiP 725")
t2 = tax(26600, F(3, 2), 1, True); print("ex2 lower earner 1.5 parts, 26 600: brut", t2, "single ->", decote(t2, "single"), "couple ->", decote(t2, "couple"), "BOFiP 606")
print("ex3 lower earner 1.25 parts, 52 000: cap rounded apart", tax(52000, F(5, 4), 1, True), "| cap rounded with the tax", tax(52000, F(5, 4), 1, False), "BOFiP 7 869")
