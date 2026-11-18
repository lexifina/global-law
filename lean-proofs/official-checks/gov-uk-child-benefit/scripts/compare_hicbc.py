#!/usr/bin/env python3
"""GOV.UK Child Benefit tax calculator (alphagov/smart-answers, the real Ruby class via scripts/hicbc_run.rb)
vs ITEPA 2003 s. 681C (exact arithmetic) vs the Lean UK model (uktax, 2025-26, whole-pound incomes).

Outputs results/hicbc_rows.jsonl, results/hicbc_summary.txt."""
import json, math, os, subprocess, random
from fractions import Fraction as F
from collections import Counter, defaultdict
from datetime import date, timedelta

BASE = os.path.expanduser('~/cmp/official/uk-hmrc')
RUBY = BASE + '/opt/ruby/bin/ruby'
SA = BASE + '/src/smart-answers'
UKTAX = os.path.expanduser('~/cmp/uk/lean/.lake/build/bin/uktax')
OUT = BASE + '/results'

RATES = {  # config/smart_answers/rates/child_benefit_rates.yml (checked against the statute below for 2025)
    '2023': (date(2023, 4, 6), date(2024, 4, 5), F('24.00'), F('15.90'), 50000, 60000),
    '2024': (date(2024, 4, 6), date(2025, 4, 5), F('25.60'), F('16.95'), 60000, 80000),
    '2025': (date(2025, 4, 6), date(2026, 4, 5), F('26.05'), F('17.25'), 60000, 80000),
    '2026': (date(2026, 4, 6), date(2027, 4, 5), F('27.05'), F('17.90'), 60000, 80000),
}


def mondays(a, b):
    d = a + timedelta(days=(7 - a.weekday()) % 7)
    n = 0
    while d <= b:
        n += 1
        d += timedelta(days=7)
    return n


def statute(year, n, ani):
    """s. 681C: charge = appropriate % of the total CB; (3)(a) total and charge rounded down to £1;
    (2)(b) % = (ANI - L) / X, (3)(b) rounded down to a whole number; (2)(a) at most 100 %."""
    s, e, eld, add, lo, hi = RATES[year]
    x = F(hi - lo, 100)          # £200 from 2024-25 (L £60,000); £100 before (L £50,000)
    wk = mondays(s, e)
    total = wk * (eld + add * (n - 1))
    total_r = math.floor(total)
    ani = F(ani)
    if ani <= lo:
        pct = 0
    else:
        pct = min(100, math.floor((ani - lo) / x))
    charge = math.floor(F(total_r) * pct / 100)
    return dict(total=total, pct=pct, charge=charge)


def run_ruby(lines):
    out = subprocess.run([RUBY, BASE + '/scripts/hicbc_run.rb', SA], input='\n'.join(lines) + '\n',
                         capture_output=True, text=True, check=True).stdout.splitlines()
    assert len(out) == len(lines)
    res = {}
    for o in out:
        i, b, p, t, a = o.split(';')
        res[i] = dict(total=F(b), pct=int(p), charge=int(t), ani=F(a))
    return res


def run_lean(rows):
    hs = []
    for r in rows:
        hs.append(json.dumps({"id": r['id'], "year": 2025, "adults": [{"age": 40, "wages": r['ani'], "selfEmployment": 0,
                              "pension": 0}], "married": False, "children": [{"age": 5}] * r['n'], "interest": 0,
                              "dividends": 0, "capitalGains": 0, "rentalIncome": 0, "charitable": 0,
                              "pensionContributions": 0}))
    out = subprocess.run([UKTAX], input='\n'.join(hs) + '\n', capture_output=True, text=True, check=True).stdout
    res = {}
    for o in out.splitlines():
        j = json.loads(o)
        res[j['id']] = dict(cb=F(str(j['detail']['childBenefit'])), hicbc=F(str(j['detail']['hicbc'])))
    return res


def main():
    rows = []
    # 1. 2025-26, whole-pound ANI 59,000-81,000, 1-4 children: Ruby vs statute vs Lean
    for n in (1, 2, 3, 4):
        for ani in range(59000, 81001):
            rows.append(dict(id=f'y2025-n{n}-{ani}', year='2025', n=n, ani=ani, inc=str(ani), ded='0', oth='0'))
    # 2. pence probes around every £200 step, all four years in the calculator's current range
    for year in ('2023', '2024', '2025', '2026'):
        lo, hi = RATES[year][4], RATES[year][5]
        step = (hi - lo) // 100
        for k in range(0, 101):
            for d in ('-0.01', '0', '0.01', '0.99'):
                v = F(lo + k * step) + F(d)
                rows.append(dict(id=f'p{year}-{k}{d}', year=year, n=2, ani=v, inc=str(float(v)) if v.denominator != 1 else str(v.numerator), ded='0', oth='0'))
    # 3. deductions (pension relief at source / Gift Aid grossed up x 1.25; other deductions), 2025-26
    rnd = random.Random(20261118)
    for i in range(20000):
        inc = rnd.randint(60000, 95000)
        ded = rnd.choice([0, rnd.randint(0, 12000), rnd.randint(0, 1200000) / 100])
        oth = rnd.choice([0, 0, rnd.randint(0, 5000)])
        ani = F(inc) - F(str(ded)) * F(5, 4) - F(oth)
        rows.append(dict(id=f'd{i}', year='2025', n=rnd.randint(1, 4), ani=ani, inc=str(inc), ded=str(ded), oth=str(oth)))
    lines = [f"{r['id']};{r['year']};{r['n']};{r['inc']};{r['ded']};{r['oth']}" for r in rows]
    rb = run_ruby(lines)
    lean = run_lean([r for r in rows if r['id'].startswith('y2025')])

    summ = defaultdict(Counter)
    maxd = defaultdict(int)
    examples = defaultdict(list)
    out = []
    for r in rows:
        g = rb[r['id']]
        s = statute(r['year'], r['n'], r['ani'])
        grp = r['id'][0] if not r['id'].startswith('y') else 'y2025'
        if g['ani'] != F(r['ani']) and abs(g['ani'] - F(r['ani'])) > F(1, 10 ** 6):
            summ[grp]['ani-mismatch'] += 1
        cause = []
        if g['total'] != s['total']:
            cause.append('benefit total')
        if g['pct'] != s['pct']:
            cause.append('percentage (float floor)')
        if g['charge'] != s['charge'] and g['pct'] == s['pct']:
            cause.append('total not rounded down before the %')
        if r['id'] in lean:
            L = lean[r['id']]
            if L['hicbc'] != s['charge'] or L['cb'] != s['total']:
                summ[grp]['LEAN != statute replica'] += 1
                examples['lean'].append((r['id'], float(L['hicbc']), s['charge'], float(L['cb']), float(s['total'])))
        d = g['charge'] - s['charge']
        key = 'equal' if d == 0 and not cause else ' + '.join(cause) or 'other'
        summ[grp][key] += 1
        maxd[(grp, key)] = max(maxd[(grp, key)], abs(d))
        if d != 0 and len(examples[key]) < 12:
            examples[key].append((r['id'], float(r['ani']), r['n'], g['pct'], s['pct'], g['charge'], s['charge']))
        out.append(dict(id=r['id'], year=r['year'], n=r['n'], ani=float(r['ani']), gov_pct=g['pct'], stat_pct=s['pct'],
                        gov_charge=g['charge'], stat_charge=s['charge'], total=float(s['total']), cls=key))
    with open(OUT + '/hicbc_rows.jsonl', 'w') as f:
        for o in out:
            f.write(json.dumps(o) + '\n')
    with open(OUT + '/hicbc_summary.txt', 'w') as f:
        f.write(f'rows: {len(rows)} (Lean-checked: {len(lean)})\n')
        for g_ in sorted(summ):
            f.write(f'{g_}: ' + ', '.join(f'{k}={v}' for k, v in sorted(summ[g_].items())) + '\n')
        f.write('max |charge difference| (£):\n')
        for k_, v in sorted(maxd.items()):
            f.write(f'  {k_}: {v}\n')
        f.write('examples (id, ANI, children, GOV.UK %, statute %, GOV.UK £, statute £):\n')
        for k_, v in examples.items():
            f.write(f'  {k_}:\n')
            for e in v[:12]:
                f.write(f'    {e}\n')
    print(open(OUT + '/hicbc_summary.txt').read())


if __name__ == '__main__':
    main()
