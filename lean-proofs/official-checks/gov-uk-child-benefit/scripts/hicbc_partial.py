#!/usr/bin/env python3
"""Partial-year child benefit (2025-26): GOV.UK calculator (real Ruby class) vs a week-by-week reading of the rates
(S.I. 2006/965 reg. 2 as uprated: the higher weekly rate for the only/eldest child in a week, the lower rate for each
other child; SSCBA 1992 s. 147(1): a week begins on a Monday). A child counts for a week if its claim period
[start, end] contains that week's Monday (the calculator's own date convention; see REPORT)."""
import random, subprocess, os, math
from datetime import date, timedelta
BASE = os.path.expanduser('~/cmp/official/uk-hmrc')
S, E = date(2025, 4, 6), date(2026, 4, 5)
mons = [S + timedelta(days=i) for i in range((E - S).days + 1) if (S + timedelta(days=i)).weekday() == 0]
rnd = random.Random(7)
lines, cases = [], []
for i in range(3000):
    n = rnd.randint(1, 4); p = rnd.randint(1, n)
    periods = []
    for _ in range(p):
        a = S + timedelta(days=rnd.randint(0, 360)); b = a + timedelta(days=rnd.randint(1, 400))
        periods.append((a, b if b <= E and rnd.random() < 0.7 else None))
    ani = rnd.randint(60000, 82000)
    cases.append((n, p, periods, ani))
    lines.append(f"c{i};2025;{n};{ani};0;0;{p};" + "|".join(f"{a},{b or ''}" for a, b in periods))
out = subprocess.run([BASE + '/opt/ruby/bin/ruby', BASE + '/scripts/hicbc_run.rb', BASE + '/src/smart-answers'],
                     input="\n".join(lines) + "\n", capture_output=True, text=True, check=True).stdout.splitlines()
bad_total = bad_charge = other = 0
for (n, p, periods, ani), o in zip(cases, out):
    _, tot, pct, est, _ = o.split(';')
    pence = 0
    for m in mons:
        k = (n - p) + sum(1 for a, b in periods if a <= m <= (b or E))
        if k: pence += 2605 + 1725 * (k - 1)
    if abs(float(tot) * 100 - pence) > 0.5: bad_total += 1
    st_pct = 0 if ani <= 60000 else min(100, (ani - 60000) // 200)
    st = (pence // 100) * st_pct // 100
    if int(est) != st: bad_charge += 1
    if int(est) != pence * st_pct // 10000: other += 1
print(f"partial-year cases {len(cases)}: benefit total differs {bad_total}; charge differs {bad_charge} "
      f"(of which not explained by the issue-02 rounding: {other})")
