#!/usr/bin/env python3
"""vflag2.py <bucket-prefix> <n> <seed> [width]: sample flagged opinions of a bucket, show row + text around the amount."""
import json, re, sys, random, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties'); D2 = H + '/data2'
F = json.load(open(D2 + '/flags.json'))
b, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); w = int(sys.argv[4]) if len(sys.argv) > 4 else 260
by = {}
for f in F:
    if f['bucket'].startswith(b): by.setdefault(f['id'], []).append(f)
ids = sorted(by); random.seed(seed); pick = random.sample(ids, min(n, len(ids)))
for i in pick:
    fs = by[i]; f = fs[0]
    t = re.sub(r'\s+', ' ', open(D2 + '/lay/%s.txt' % i, errors='ignore').read())
    v = max(f['pen'].values()); s = '{:,.0f}'.format(int(v)) if v >= 1000 else str(int(v))
    m = re.search(re.escape(s).replace(',', r',\s?'), t); st = m.start() if m else 0
    print('##', f['cite'], f['docket'], f['decision'], '|', '; '.join('%s def %s %s [%s]' % (x['year'], x['deficiency'], x['pen'], x['label'][6:40]) for x in fs[:3]))
    print('   ', t[max(0, st - w):st + 120])
