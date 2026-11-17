"""Exact extremes of (Tax Table - §1(j) schedule) per filing status, from the parsed rows (for writing the Lean
statements; the Lean file proves them). Usage: python3 -I table_extremes.py TaxTableData.lean"""
import re, sys
rows = [tuple(map(int, m)) for m in re.findall(r'\((\d+), (\d+), (\d+), (\d+), (\d+), (\d+)\)', open(sys.argv[1]).read())]
S = {'single': (11925, 48475, 103350, 197300, 250525, 626350, 119250, 557850, 1765100, 4019900, 5723100, 18876975),
     'mfj': (23850, 96950, 206700, 394600, 501050, 751600, 238500, 1115700, 3530200, 8039800, 11446200, 20215450),
     'mfs': (11925, 48475, 103350, 197300, 250525, 375800, 119250, 557850, 1765100, 4019900, 5723100, 10107725),
     'hoh': (17000, 64850, 103350, 197300, 250500, 626350, 170000, 744200, 1591200, 3846000, 5548400, 18703150)}
def cents(s, x):
    e1,e2,e3,e4,e5,e6,b1,b2,b3,b4,b5,b6 = s
    if x <= 0: return 0
    if x <= e1: return 10*x
    if x <= e2: return b1 + 12*(x-e1)
    if x <= e3: return b2 + 22*(x-e2)
    return b3 + 24*(x-e3)
rd = lambda n, d: (2*n + d) // (2*d)
for k, name in enumerate(['single', 'mfj', 'mfs', 'hoh']):
    s = S[name]
    over = max((100*r[2+k] - cents(s, r[0]), r[0]) for r in rows)
    under = max((cents(s, r[1]-1) - 100*r[2+k], r[1]-1) for r in rows)
    overR = max((r[2+k] - rd(cents(s, r[0]), 100), r[0]) for r in rows)
    underR = max((rd(cents(s, r[1]-1), 100) - r[2+k], r[1]-1) for r in rows)
    print(name, 'over cents', over, 'under cents', under, 'over $', overR, 'under $', underR)
