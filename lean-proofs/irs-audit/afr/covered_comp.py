"""Covered compensation tables (annual revenue rulings under §401(l)(5)(E)): Table I of year Y against Table I of
year Y-1 and the two taxable wage bases the rulings state. For a birth year whose Social Security retirement age
year s is at least Y: CC_Y - CC_{Y-1} = (s - (Y-1)) x (W_Y - W_{Y-1}) / 35 (Reg. 1.401(l)-1(c)(7)(i): future wage bases
assumed equal to the current one); for s <= Y-1 the amount is frozen."""
import re, glob, os, json
G = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/irs-guidance')
T = {}
for f in sorted(glob.glob(G + '/rev-rul/*/*.md')):
    t = open(f, encoding='utf-8').read()
    if 'COVERED COMPENSATION TABLE' not in t.upper() or 'taxable wage base' not in t: continue
    m = re.search(r'covered compensation for the (\d{4}) (?:plan )?year, the taxable wage base is \$([\d,]+)', t)
    if not m: continue
    Y = int(m.group(1)); W = int(m.group(2).replace(',', ''))
    body = t.split('ROUNDED')[0]
    rows = {}
    for b, s, v in re.findall(r'^(\d{4})\s*\|\s*(\d{4})\s*\|\s*\$?\s*([\d,]+)\s*$', body, re.M):
        rows[int(b)] = (int(s), int(v.replace(',', '')))
    if rows: T[Y] = dict(W=W, rows=rows, item=re.search(r'^item: "([^"]+)"', t, re.M).group(1))
res = []; n = bad = 0
for Y in sorted(T):
    if Y - 1 not in T: continue
    a, b = T[Y - 1], T[Y]
    for by, (s, v) in b['rows'].items():
        if by not in a['rows']: continue
        v0 = a['rows'][by][1]
        exp = (s - (Y - 1)) * (b['W'] - a['W']) / 35 if s >= Y else 0
        n += 1
        if abs((v - v0) - exp) > 12.0001 or v % 12:
            bad += 1; res.append((Y, b['item'], by, s, v0, v, round(exp, 2)))
print('years', sorted(T), 'pairs checked', n, 'off by more than $1:', bad)
for r in res[:30]: print(r)
json.dump(dict(years={y: dict(W=T[y]['W'], item=T[y]['item'], n=len(T[y]['rows'])) for y in T}, checked=n, bad=res), open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/afr/covered_comp.json'), 'w'), indent=1)
