"""Historical interest-rate tables printed in every quarterly section 6621 revenue ruling: (1) each period's rate against
the statute (short-term rate verified in q6621 + the statutory add-on), (2) the same period across rulings, (3) the
Rev. Proc. 95-17 factor table cited for each rate (one table per rate and year length)."""
import re, os, glob, json, collections
G = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/irs-guidance'); H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
MON = {m: i + 1 for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])}
q = json.load(open(H + '/q6621/q.json'))
fst = {}
for r in q:
    if 'fst' in r and 'quarter' in r: fst[tuple(r['quarter'])] = float(r['fst'])
KIND = [('NONCORPORATE', 'noncorp'), ('LARGE CORPORATE', 'large'), ('EXCEEDING', 'over10k'), ('CORPORATE OVERPAYMENTS AND UNDERPAYMENTS', 'corp')]
ADD = {'noncorp': [3.0], 'corp': [2.0, 3.0], 'large': [5.0], 'over10k': [0.5]}
rowre = re.compile(r'^(\w{3})\w*\.? (\d+), (\d{4})\s*[–-]\s*(\w{3})\w*\.? (\d+), (\d{4})\s*\|(.*)$')
seen = collections.defaultdict(dict); mapping = collections.defaultdict(collections.Counter); stat = []; nrows = 0
for f in sorted(glob.glob(G + '/rev-rul/*/*.md')):
    t = open(f, encoding='utf-8').read()
    if 'TABLE OF INTEREST RATES' not in t: continue
    item = re.search(r'^item: "([^"]+)"', t, re.M).group(1)
    kind = None
    for line in t.splitlines():
        if line.startswith('TABLE OF INTEREST RATES'):
            kind = next((k for h, k in KIND if h in line.upper()), None)
            if 'PERIODS BEFORE' in line.upper() or '1987' in line and '1998' in line: kind = None
            continue
        m = rowre.match(line.strip())
        if not m or not kind: continue
        mo = MON.get(m.group(1).lower()); y = int(m.group(3))
        if not mo: continue
        cells = [c.strip() for c in m.group(7).split('|')]
        groups = []
        k = 0
        while k + 2 < len(cells) + 1 and k < len(cells):
            if cells[k].endswith('%'):
                groups.append((float(cells[k][:-1]), cells[k + 1] if k + 1 < len(cells) else '', cells[k + 2] if k + 2 < len(cells) else '')); k += 3
            else: k += 1
        if len(groups) != len(ADD[kind]): continue
        nrows += 1
        for gi, (rate, tab, pg) in enumerate(groups):
            key = (kind, gi, y, mo)
            leap = (y % 4 == 0)
            mapping[(rate, leap)][(tab, pg)] += 1
            seen[key][item] = (rate, tab, pg)
            if (y, mo) in fst and mo in (1, 4, 7, 10):
                want = fst[(y, mo)] + ADD[kind][gi]
                if abs(want - rate) > 1e-9: stat.append((item, kind, gi, y, mo, rate, want))
incons = []
for key, d in seen.items():
    vals = collections.Counter(v[0] for v in d.values())
    if len(vals) > 1:
        maj = vals.most_common(1)[0][0]
        incons.append((key, {i: v[0] for i, v in d.items() if v[0] != maj}, maj))
mapbad = []
for (rate, leap), c in mapping.items():
    if len(c) > 1:
        maj = c.most_common(1)[0][0]
        mapbad.append((rate, leap, maj, {k: v for k, v in c.items() if k != maj}))
print('rows', nrows, 'periods', len(seen), 'statute mismatches', len(stat), 'cross-ruling inconsistencies', len(incons), 'table-ref inconsistencies', len(mapbad))
for s in stat[:10]: print('STAT', s)
for s in incons[:15]: print('INC', s)
for s in mapbad[:15]: print('MAP', s)
json.dump(dict(rows=nrows, periods=len(seen), stat=stat, incons=[(list(k), v, m) for k, v, m in incons], mapbad=[(r, l, list(m), {'%s/%s' % k: v for k, v in o.items()}) for r, l, m, o in mapbad]), open(H + '/q6621/history_tables.json', 'w'), indent=1)
