"""26 CFR 20.2031-7A: Table S single-life remainder factors (80CNSMT, 1989-1999; 90CM, 1999-2009) recomputed from the
life tables printed in the same section: R = (1 + i/2) * sum_t v^(t+1) (l_{x+t} - l_{x+t+1}) / l_x (the IRS convention,
which reproduces the Table S examples of 20.2031-7(d)), five decimals."""
import re, os, json
from fractions import Fraction as F
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
L = open(H + '/src/cfr/title-26-part-0020/sec-2031-0007a.md', encoding='utf-8').read().splitlines()
tabs = {'80CNSMT': {}, '90CM': {}}; life = {'80CNSMT': {}, '90CM': {}}
cur = None; mode = None; rates = None
for line in L:
    if line.startswith('Table S') and '80CNSMT' in line: cur, mode, rates = '80CNSMT', 'S', None; continue
    if line.startswith('Table S') and '90CM' in line: cur, mode, rates = '90CM', 'S', None; continue
    if line.startswith('Table 80CNSMT'): cur, mode = '80CNSMT', 'L'; continue
    if line.startswith('Table 90CM'): cur, mode = '90CM', 'L'; continue
    if line.startswith('Table ') : mode = None; continue
    c = [x.strip() for x in line.split('|')]
    if mode == 'S':
        if c[0].lower().startswith('age') and len(c) > 2:
            rates = [x.rstrip('%') for x in c[1:]]; continue
        if all(x.endswith('%') for x in c) and len(c) > 2:
            rates = [x.rstrip('%') for x in c]; continue
        if rates and c[0].isdigit() and len(c) == len(rates) + 1:
            for r, v in zip(rates, c[1:]):
                try: tabs[cur][(int(round(float(r) * 10)), int(c[0]))] = v
                except ValueError: pass
    elif mode == 'L':
        for k in range(0, len(c) - 1, 2):
            if c[k].isdigit(): life[cur][int(c[k])] = float(c[k + 1].replace(',', ''))
res = {}
for name in tabs:
    lx = life[name]; top = max(lx)
    bad = []; n = 0
    for (r, x), v in sorted(tabs[name].items()):
        if x not in lx: continue
        i = r / 1000; vv = 1 / (1 + i)
        R = (1 + i / 2) * sum(vv ** (t + 1) * (lx[x + t] - lx.get(x + t + 1, 0)) for t in range(0, top - x + 1)) / lx[x]
        n += 1
        if abs(R - float(v)) > 0.0000051: bad.append((r / 10, x, v, round(R, 6)))
    res[name] = dict(factors=n, life_rows=len(lx), off=bad)
    print(name, 'life rows', len(lx), 'factors', n, 'off', len(bad), bad[:12])
json.dump(res, open(H + '/cfr/table_s_hist.json', 'w'), indent=1)
