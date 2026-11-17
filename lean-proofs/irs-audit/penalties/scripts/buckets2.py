#!/usr/bin/env python3
"""Provisional buckets for every flagged row/opinion (before hand verification)."""
import json, collections, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties'); D2 = H + '/data2'
F = json.load(open(D2 + '/flags.json')); T = json.load(open(D2 + '/tags.json'))
RATE = {'6662(a)': .20, '6662(h)': .40, '6663': .75, '6651(a)(1)': .25, '6651(a)(2)': .25, '6651(f)': .75}
def bucket(f):
    d = f['deficiency']; p = f['pen']; lab = f['label']
    if 'amount is 40%' in lab: return 'B1 6662 amount at exactly 40% (valuation rate under a generic label?)'
    if f['check'] == 'c1': return 'B9 (c)(1) check'
    if 'overlap' in lab:
        tot = sum(v / RATE[k] for k, v in p.items() if k in ('6662(a)', '6662(h)', '6663'))
        r = tot / d if d else 99
    else:
        k = {'acc': None, '6651a1': '6651(a)(1)', '6651a2': '6651(a)(2)', '6651f': '6651(f)'}[f['check']]
        if k is None: k = '6663' if '6663' in lab else '6662(h)' if '6662(h)' in lab else '6662(a)'
        v = p.get(k, 0) + (p.get('6651(a)(3)', 0) if k == '6651(a)(2)' else 0)
        cap = RATE[k] * d; r = v / cap if cap else 99
        if v - cap <= max(5, 0.005 * cap): return 'B2 excess within $5 or 0.5% (rounding level)'
    if d < 10 or r >= 2: return 'B3 gross excess (2x the cap or more)'
    late = (T.get(f['id']) or {}).get('late')
    if f['check'] == '6651a1' and late: return 'B4 6651(a)(1) over 25%, late return in the opinion (6665(b)(1) candidate)'
    if f['check'] == '6651a1': return 'B5 6651(a)(1) over 25%, no late return found in text'
    return 'B6 other excess, Rule 155' if f['decision'] == 'Rule 155' else 'B7 other excess, decided otherwise'
for f in F: f['bucket'] = bucket(f)
json.dump(F, open(D2 + '/flags.json', 'w'), indent=0)
print(collections.Counter(f['bucket'] for f in F).most_common())
ob = collections.defaultdict(set)
for f in F: ob[f['id']].add(f['bucket'][:2])
print('opinions by bucket set (min):', collections.Counter(min(v) for v in ob.values()).most_common())
