"""Classify the novel-search hits (runs/novel_n1.json, runs/novel_n2.json) by cause, by switching single features off."""
import json, collections, copy
import de
from de import run, burden

# N1: big drops (> 5 €) and where they are
n1 = json.load(open('runs/novel_n1.json'))
big = collections.Counter(); small = collections.Counter(); kinds = collections.Counter()
for r in n1:
    for w, d in r['drops']:
        if d < -5: big[(r['kind'], w)] += 1
        else: small[r['kind']] += 1
print('N1 drops > 5 € by (kind, wage):', big.most_common(10))
print('N1 drops <= 5 € by kind:', dict(small))
mx = collections.Counter()
for r in n1:
    for w, d in r['drops']:
        if d >= -5: mx[round(d)] += 1
print('N1 small-drop sizes (rounded €):', sorted(mx.items()))
wr = sorted(((r['worst100'][0], r['kind'], r['prof'], r['worst100'][1]) for r in n1 if not (6550 <= r['worst100'][1] <= 6700)), reverse=True)[:8]
print('N1 worst 100-€ windows away from the Minijob limit:', wr)

# N2: joint worse than separate by > 2 €
n2 = [x for x in json.load(open('runs/novel_n2.json')) if x['joint_minus_sep'] > 2]
def gap(h, kist, *extra):
    fl = ([f'--kist={kist}'] if kist else []) + list(extra)
    j = run([h], *fl)[0]; s = run([h], *fl, '--separate')[0]
    return burden(j) - burden(s)
cause = collections.Counter(); ex = {}
for x in n2[:3000]:
    h, k = x['h'], x['kist']
    g0 = x['joint_minus_sep']
    if gap(h, k, '--no-32d6') <= 2: c = '32d6 all-or-nothing for spouses (Satz 3)'
    elif gap(dict(h, children=[]), k) <= 2: c = 'children (per-parent Guenstigerpruefung)'
    elif gap(dict(h, charitable=0), k) <= 2: c = '§ 10b cap'
    elif gap(dict(h, adults=[dict(a, age=min(a['age'], 60)) for a in h['adults']]), k) <= 2: c = 'age-related (§ 24a / SV)'
    else: c = 'other'
    cause[c] += 1; ex.setdefault(c, []).append((g0, x))
print('N2 cause of joint > separate (first 3000 of', len(n2), '):', dict(cause))
for c, l in ex.items():
    l.sort(key=lambda t: -t[0]); g0, x = l[0]
    print(' ', c, 'max', g0, 'kist', x['kist'], json.dumps({k: v for k, v in x['h'].items() if k not in ('id', 'year')}))
