"""Parse Pub. 15-T (2025, 2026): annual Percentage Method tables (Worksheet 1A, STANDARD and Step 2 checkbox) and the
Wage Bracket Method tables for Forms W-4 from 2020 or later (section 2). Check them against §1(j) and each other.

    python3 -I tools/arith/p15t.py            -> out/p15t.json and a report
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from spec import PUB_BR
from derived import TAXCOL

D = os.path.expanduser('~/docs/irs')
MONEY = r'\$\s?([\d,]+(?:\.\d\d)?)'

def cents(s): s = s.replace(',', ''); return int(round(float(s) * 100))
def dollars(s): return int(s.replace(',', '').split('.')[0])

STATUS = {'Married Filing Jointly': 'mfj', 'Single or Married Filing Separately': 'single', 'Head of Household': 'hoh'}

def annual_tables(year):
    """{('std'|'chk', status): [(A dollars, C cents, D percent)]}"""
    t = open(f'{D}/p15t--{year}.txt', encoding='utf-8').read().split('\n')
    start = next(i for i, l in enumerate(t) if f'{year} Percentage Method Tables for Automated Payroll Systems and Withholding' in l)
    out, st = {}, None
    for l in t[start:start + 80]:
        s = l.strip()
        for k, v in STATUS.items():
            if s.startswith(k) or (s.startswith(k.split()[0]) and k in s):
                st = v
        vals = re.findall(r'\$\s?[\d,]+(?:\.\d\d)?|\d+%', l)
        if st and len(vals) >= 8:
            # left: A B C D E   right: A B C D E  (top rows lack B)
            def row(v):
                A = dollars(v[0][1:]); C = cents(v[-3][1:]) if v[-3].startswith('$') else None
                D_ = int(v[-2][:-1]); return (A, C, D_)
            pct = [i for i, v in enumerate(vals) if v.endswith('%')]
            left, right = vals[:pct[0] + 2], vals[pct[0] + 2:]
            out.setdefault(('std', st), []).append(row(left))
            out.setdefault(('chk', st), []).append(row(right))
        if st == 'hoh' and len(out.get(('std', 'hoh'), [])) == 8:
            break
    return out

def wage_brackets(year):
    """{(freq, status, 'std'|'chk'): [(lo, hi, amount)]} from section 2 (Forms W-4 from 2020 or later)."""
    t = open(f'{D}/p15t--{year}.txt', encoding='utf-8').read().split('\n')
    s0 = next(i for i, l in enumerate(t) if 'Wage Bracket Method Tables for Manual Payroll Systems with Forms W-4 From 2020'.lower() in l.lower())
    s1 = next(i for i, l in enumerate(t) if i > s0 + 10 and 'Wage Bracket Method Tables for Manual Payroll Systems With Forms W-4 From 2019'.lower() in l.lower())
    out, freq = {}, None
    cols = [('mfj', 'std'), ('mfj', 'chk'), ('hoh', 'std'), ('hoh', 'chk'), ('single', 'std'), ('single', 'chk')]
    for l in t[s0:s1]:
        m = re.search(r'(WEEKLY|BIWEEKLY|SEMIMONTHLY|MONTHLY|DAILY) Payroll Period', l)
        if m: freq = m.group(1).lower()
        vals = re.findall(MONEY, l)
        if freq and len(vals) == 8:
            lo, hi = dollars(vals[0]), dollars(vals[1])
            for (st, kind), v in zip(cols, vals[2:]):
                out.setdefault(f'{freq}|{st}|{kind}', []).append((lo, hi, dollars(v)))
    return out

PERIODS = {'weekly': 52, 'biweekly': 26, 'semimonthly': 24, 'monthly': 12, 'daily': 260}

def eval_rows(rows, w):
    """annual table value in cents at annual wage w (dollars, may be fractional via Fraction)"""
    best = None
    for A, C, Dp in rows:
        if A <= w: best = (A, C, Dp)
    A, C, Dp = best
    return C + Dp * (w - A)        # percent of dollars = cents

if __name__ == '__main__':
    from fractions import Fraction as F
    rep = {}
    for year in (2025, 2026):
        at = annual_tables(year); wb = wage_brackets(year)
        ty = year
        rep[year] = dict(annual={f'{k[0]}|{k[1]}': v for k, v in at.items()}, wage={k: v for k, v in wb.items()})
        print(year, 'annual tables', {k: len(v) for k, v in at.items()})
        print(year, 'wage bracket tables', {k: len(v) for k, v in wb.items()})
        # structural: STANDARD table = §1(j) table shifted by z
        for st in ('mfj', 'single', 'hoh'):
            rows = at[('std', st)]; z = rows[1][0]
            tops = PUB_BR[ty][st]; col = [0] + TAXCOL[ty][st]
            want = [(0, 0, 0)] + [(z + a, c, r) for a, c, r in zip([0] + tops, col, [10, 12, 22, 24, 32, 35, 37])]
            print(' std', st, 'zero bracket', z, 'shift ok' if rows == want else f'DIFF {rows} vs {want}')
            ch = at[('chk', st)]; zc = ch[1][0]
            wantc = [(0, 0, 0)] + [(zc + (a // 2 if a % 2 == 0 else F(a, 2)), F(c, 2), r) for a, c, r in zip([0] + tops, col, [10, 12, 22, 24, 32, 35, 37])]
            diffs = [(x, y) for x, y in zip(ch, wantc) if x[0] != y[0] or abs(x[1] - y[1]) > F(1, 2) or x[2] != y[2]]
            print(' chk', st, 'zero bracket', zc, 'half ok' if not diffs else f'DIFF {diffs}')
        # wage bracket vs percentage method
        worst = {}
        for key, rows in wb.items():
            freq, st, kind = key.split('|'); n = PERIODS[freq]
            ann = at[(kind, st)]
            # Worksheet 2 has no line 1g: the STANDARD wage-bracket columns build in Worksheet 1A line 1g
            adj = 0 if kind == 'chk' else (12900 if st == 'mfj' else 8600)
            pm = lambda w: F(eval_rows(ann, max(0, w * n - adj)), n)
            for lo, hi, amt in rows:
                plo = pm(lo); phi = pm(hi)   # cents per period
                pmid = pm(F(lo + hi, 2))
                mid_ok = abs(amt * 100 - pmid) <= 50
                dev = max(amt * 100 - plo, phi - amt * 100)
                w = worst.setdefault(key, [0, 0, 0])
                w[0] = max(w[0], dev); w[1] += (0 if mid_ok else 1); w[2] += 1
        for k, (dev, bad, n) in sorted(worst.items()):
            print(f'  {k:28} rows {n:4} max |wage bracket - percentage| <= ${float(dev)/100:.2f}  midpoint-rule misses {bad}')
    json.dump({str(y): {'annual': v['annual'], 'wage': v['wage']} for y, v in rep.items()}, open(os.path.join(HERE, 'out', 'p15t.json'), 'w'),
              default=lambda o: float(o))
