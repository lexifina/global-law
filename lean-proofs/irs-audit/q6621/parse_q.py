"""Parse the quarterly section 6621 interest-rate revenue rulings: the declared federal short-term rate, the
established rates, and the Appendix daily-compound interest factor tables."""
import re, os, json, glob
G = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/irs-guidance')
MON = ['january','february','march','april','may','june','july','august','september','october','november','december']
NUMP = r'(\d+(?:\.\d+)?)'
out = []
for f in sorted(glob.glob(G + '/rev-rul/*/*.md')):
    raw = open(f, encoding='utf-8').read()
    if 'calendar quarter beginning' not in raw or '6621' not in raw: continue
    item = re.search(r'^item: "([^"]+)"', raw, re.M).group(1)
    bull = re.search(r'^bulletin: "([^"]+)"', raw, re.M).group(1)
    t = re.sub(r'(\w)[-–]\s*\n\s*(\w)', r'\1\2', raw)
    t = ' '.join(t.split())
    t = t.replace('under- payment', 'underpayment').replace('over- payment', 'overpayment')
    r = dict(file=os.path.relpath(f, G), item=item, bulletin=bull)
    m = re.search(r'daily compounding,? determined during the month of (\w+),? (\d{4}),? is ' + NUMP + r' percent', t, re.I)
    if m and m.group(1).lower() in MON:
        r['fst_month'] = [int(m.group(2)), MON.index(m.group(1).lower()) + 1]; r['fst'] = m.group(3)
        seg = t[m.end(): m.end() + 1500]
        q = re.search(r'calendar quarter beginning (\w+) 1, (\d{4})', seg)
        if q: r['quarter'] = [int(q.group(2)), MON.index(q.group(1).lower()) + 1]
        a = re.search(r'overpayment rate of ' + NUMP + r' percent(?: \(' + NUMP + r' percent in the case of a corporation\))? and an underpayment rate of ' + NUMP + ' percent', seg)
        if a: r['over'], r['over_corp'], r['under'] = a.group(1), a.group(2), a.group(3)
        b = re.search(r'exceeding \$10,000[^.]*?is ' + NUMP + r' percent', seg)
        if b: r['over_10k'] = b.group(1)
        c = re.search(r'large corporate underpayments[^.]*?is ' + NUMP + r' percent', seg)
        if c: r['large_corp'] = c.group(1)
    # appendix factor tables: walk the lines; "365 Day Year" / "366 Day Year" set the year, "<r>% Compound Rate" the rate
    tabs = []; yd = None; cur = None
    for line in raw.split('\n'):
        my = re.match(r'\s*(36[56]) Day Year', line)
        if my: yd = int(my.group(1)); continue
        mr = re.match(r'\s*(\d+(?:\.\d+)?)% Compound Rate', line)
        if mr and yd:
            cur = dict(year_days=yd, rate=mr.group(1), rows=[]); tabs.append(cur); continue
        if cur is not None:
            for d, v in re.findall(r'(\d{1,3})\s*\|\s*(\d\.\d{9})', line): cur['rows'].append([int(d), v])
    tabs = [t for t in tabs if t['rows']]
    r['tables'] = tabs
    out.append(r)
json.dump(out, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/q6621/q.json'), 'w'))
from collections import Counter
print(len(out), 'rulings; with fst', sum('fst' in r for r in out), 'with rates', sum('under' in r for r in out),
      'quarter', sum('quarter' in r for r in out), '10k', sum('over_10k' in r for r in out), 'large', sum('large_corp' in r for r in out))
print('tables', sum(len(r['tables']) for r in out), 'rows', sum(len(t['rows']) for r in out for t in r['tables']))
print('years without fst', sorted(Counter(r['file'][8:12] for r in out if 'fst' not in r).items()))
