"""Exact extremes of 10000*(printed EIC Table) - §32 credit (1/10000 dollar), per column, whole-dollar amounts
0..80,000 (earned income = AGI). Usage: python3 -I eic_extremes.py EICTableData.lean"""
import re, sys
s = open(sys.argv[1]).read()
rows = [(int(a), int(b), list(map(int, v.split(', ')))) for a, b, v in re.findall(r'\((\d+), (\d+), \[([-\d, ]+)\]\)', s)]
splits = [tuple(map(int, t)) for t in re.findall(r'\((\d+), (\d+), (\d+), (\d+)\)', s.split('def splits')[1])]
P = {0: (765, 765, 8490, 10620, 17730), 1: (3400, 1598, 12730, 23350, 30470), 2: (4000, 2106, 17880, 23350, 30470),
     3: (4500, 2106, 17880, 23350, 30470)}
def f(c, x):
    cp, pp, eia, ts, tj = P[c % 4]; thr = tj if c >= 4 else ts
    return max(0, min(cp * min(x, eia), cp * eia - pp * max(0, max(x, x) - thr)))
def table(c, x):
    for lo, hi, vs in rows:
        if lo <= x < hi:
            v = vs[c]
            if v == -1:
                (_, _, co, sv), = [t for t in splits if t[0] == c and t[1] == lo]
                return sv if x < co else 0
            return v
    return 0
for c in range(8):
    d = [(10000 * table(c, x) - f(c, x), x) for x in range(0, 80001)]
    print(c, 'over', max(d), 'under', min(d))
