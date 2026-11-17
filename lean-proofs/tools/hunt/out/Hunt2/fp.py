"""PTC (sec. 36B) <-> self-employed health insurance deduction (sec. 162(l), sec. 280C(g)) fixed points.

Written from the statute text and the published tables, not from the Lean file.
  sec. 36B(b)(2): credit = min(enrollment premium Q, SLCSP Bm - applicable% x HI)      (annual, 12 equal months)
  sec. 36B(c)(1)(A): applicable taxpayer iff 100% <= HI/P <= 400%; (E) drops the 400% cap for 2021-2025
  sec. 36B(b)(3)(A)(iii) 2025 table; Rev. Proc. 2025-25 sec. 3.01 2026 table; Treas. Reg. 1.36B-3(g) linear scale
  sec. 36B(f)(2)(B) 2025 limitation, Rev. Proc. 2024-40 sec. 3.07; removed for 2026 (Pub. L. 119-21 sec. 71305)
  sec. 162(l)(1),(2)(A) deduction = premiums, capped at earned income L; sec. 280C(g): no deduction for the
  portion equal to the credit.   => consistent pair: d = min(L, Q - C(I0 - d))   (I0 = HI before the deduction)
Poverty line: 2025 coverage uses the 2024 HHS guideline (15,060 + 5,380/person, Form 8962 instr. 2025 Table 1-1);
2026 coverage uses the 2025 guideline (15,650 + 5,500/person; HHS, 90 FR 5917).
Two schedules: 'exact' (Pub. 974: dollars and cents, no rounding) and 'form' (Form 8962 line 5 truncated to a whole
percent, applicable figure to 4 decimals, line 8a rounded to whole dollars).
"""
import math, json, sys
import numpy as np

T2025 = [(0, 150, 0.0, 0.0), (150, 200, 0.0, 2.0), (200, 250, 2.0, 4.0), (250, 300, 4.0, 6.0),
         (300, 400, 6.0, 8.5), (400, 10**9, 8.5, 8.5)]
T2026 = [(0, 133, 2.10, 2.10), (133, 150, 3.14, 4.19), (150, 200, 4.19, 6.60), (200, 250, 6.60, 8.44),
         (250, 300, 8.44, 9.96), (300, 400.0000001, 9.96, 9.96)]
LIM2025 = [(200, 375, 750), (300, 975, 1950), (400, 1625, 3250)]  # HI% < bound -> (single, other)

def pov(year, n):
    return (15060 + 5380 * (n - 1)) if year == 2025 else (15650 + 5500 * (n - 1))

def app_pct(year, pct):
    """applicable percentage (as a fraction) at household income pct (percent of poverty line)."""
    for lo, hi, a0, a1 in (T2025 if year == 2025 else T2026):
        if lo <= pct < hi:
            return (a0 + (a1 - a0) * (pct - lo) / (hi - lo)) / 100.0
    return (8.5 if year == 2025 else 9.96) / 100.0

def credit(year, h, P, Q, Bm, mode='exact', aptc=0.0):
    pct = 100.0 * h / P
    if mode == 'form':
        pct = math.floor(pct)
    floor_ok = pct >= 100 or (aptc > 0)            # Treas. Reg. 1.36B-2(b)(6): APTC paid -> treated as applicable
    cap_ok = (year == 2025) or pct <= 400
    if not (floor_ok and cap_ok):
        return 0.0
    a = app_pct(year, max(pct, 0))
    if mode == 'form':
        a = round(a, 4)
        contrib = round(h * a)
    else:
        contrib = h * a
    return min(Q, max(0.0, Bm - contrib))

def limitation(year, h, P, single):
    if year != 2025:
        return math.inf
    pct = 100.0 * h / P
    for b, s, o in LIM2025:
        if pct < b:
            return s if single else o
    return math.inf

def g(year, d, I0, P, Q, Bm, L, mode='exact', aptc=0.0, single=True):
    """deduction implied by the statute when the taxpayer first claims d."""
    h = I0 - d
    C = credit(year, h, P, Q, Bm, mode, aptc)
    cap = Q - C
    if aptc > 0:                                   # Rev. Proc. 2014-41 sec. 5.03(2)(B)
        cap = min(cap, Q - aptc + min(max(aptc - C, 0), limitation(year, h, P, single)))
    return max(0.0, min(L, cap)), C

def solutions(year, I0, P, Q, Bm, L, mode='exact', aptc=0.0, single=True, tol=1.0):
    """all clusters of whole-dollar d with |d - g(d)| <= tol; returns list of (d, credit)."""
    top = int(min(Q, L))
    out, cur = [], None
    for d in range(0, top + 1):
        gd, C = g(year, d, I0, P, Q, Bm, L, mode, aptc, single)
        if abs(d - gd) <= tol:
            if cur is None or d != cur[-1][0] + 1:
                cur = []
                out.append(cur)
            cur.append((d, C))
    return [c[len(c) // 2] for c in out]

def iterative(year, I0, P, Q, Bm, L, mode='exact', aptc=0.0, single=True, maxit=60):
    """Rev. Proc. 2014-41 sec. 5.01 / Pub. 974 iterative method. Returns (status, d, C)."""
    d1 = min(Q, L)                                                   # Step 1
    d3, C2 = g(year, d1, I0, P, Q, Bm, L, mode, aptc, single)        # Steps 2-3
    if C2 == 0 and aptc == 0:
        return ('ineligible-at-step1', d1, 0.0)                      # Pub. 974 Step 2 "Cannot take the PTC ... stop"
    for _ in range(maxit):
        d5, C4 = g(year, d3, I0, P, Q, Bm, L, mode, aptc, single)    # Steps 4-5
        if abs(d5 - d3) < 1 and abs(C4 - C2) < 1:                    # Step 6
            return ('converged', d5, C4)
        d3, C2 = d5, C4
    return ('no-convergence', d3, C2)

def simplified(year, I0, P, Q, Bm, L, mode='exact', aptc=0.0, single=True):
    """Rev. Proc. 2014-41 sec. 5.02 alternative / Pub. 974 simplified: claim Step 4 credit with Step 3 deduction."""
    d0 = min(Q, L)
    C2 = credit(year, I0 - d0, P, Q, Bm, mode, aptc)
    if C2 == 0 and aptc == 0:
        return ('ineligible-at-step1', d0, 0.0)
    d3 = g(year, d0, I0, P, Q, Bm, L, mode, aptc, single)[0]
    C4 = credit(year, I0 - d3, P, Q, Bm, mode, aptc)
    return ('ok', d3, C4)

if __name__ == '__main__':
    print(credit(2026, 62600, 15650, 13000, 13000), credit(2026, 62601, 15650, 13000, 13000))
