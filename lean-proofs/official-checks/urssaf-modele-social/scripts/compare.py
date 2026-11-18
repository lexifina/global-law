"""Compares (1) the Lean adapter with the engine ('neutral' variant), line by line, and (2) the engine with the
statute reference law.py on every case. Writes out/diffs.json and prints a summary."""
import json, sys, collections
from decimal import Decimal as D
sys.path.insert(0, 'scripts'); from law import law
ours = {r['g']: r for r in map(json.loads, open('out/ours.jsonl'))}
eng = [json.loads(l) for l in open('out/engine.jsonl')]
diffs = collections.defaultdict(list); n = collections.Counter()
def note(kind, line, c, a, b, tol):
    n[(kind, line)] += 1
    if abs(D(str(a)) - D(str(b))) > tol: diffs[(kind, line)].append({'g': c['g'], 'per': c['per'], 'cadre': c['cadre'], 'variant': c['variant'], 'date': c.get('date'), 'a': float(a), 'b': float(b), 'diff': float(D(str(b)) - D(str(a)))})
for c in eng:
    E = {k: D(str(v)) for k, v in c.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    # (2) engine vs statute
    L = law(c['g'], c['per'], c['cadre'], sante=D(0) if c['variant'] == 'neutral' else D(40) * (12 if c['per'] == 'an' else 1),
            prev_cadres=c['variant'] != 'neutral')
    for k in ['vplaf', 'vdeplaf', 'rc', 'ceg', 'cet', 'apec', 'prevCadres', 'baseAbattue', 'csgBase', 'csgDed', 'csgNd', 'crds', 'salarie', 'net', 'netImposable']:
        note('law-vs-engine', k, c, L[k], E[k], D('0.000001'))
    # (1) adapter vs engine, annual integer cases, neutral variant only (the adapter has no health/prévoyance cover)
    if c['per'] == 'an' and c['variant'] == 'neutral' and c['g'] in ours:
        o = ours[c['g']]; cent = D('0.01'); tol = D('0.006')
        pairs = {'vplaf': o['vplaf'], 'vdeplaf': o['vdeplaf'], 'rc': o['t1'] + o['t2'], 'ceg': o['ceg1'] + o['ceg2'], 'cet': o['cet'],
                 'baseAbattue': o['csgBase'], 'csgDed': o['csgDed'], 'csgNd': o['csgNd'], 'crds': o['crds']}
        for k, v in pairs.items(): note('adapter-vs-engine', k, c, D(v) * cent, E[k], tol * (2 if k in ('rc', 'ceg') else 1))
        note('adapter-vs-engine', 'apec', c, D(0), E['apec'], tol)
        sc = o['vplaf'] + o['vdeplaf'] + o['t1'] + o['t2'] + o['ceg1'] + o['ceg2'] + o['cet']
        exact_tax = (D(c['g']) * 100 - sc - o['csgDed']) * cent
        note('adapter-vs-engine', 'netImposable(exact cents, APEC added back)', c, exact_tax, E['netImposable'] + E['apec'], D('0.03'))
        note('adapter-vs-engine', 'taxableSalary(adapter euros) vs netImposable', c, D(o['taxable']), E['netImposable'] + E['apec'], D('1.5'))
        note('adapter-vs-engine', 'ssc+csgcrds(adapter euros) vs salarie-apec', c, D(o['ssc'] + o['csgCrds']), E['salarie'] - E['apec'], D('1.5'))
summary = {f'{k[0]} | {k[1]}': {'cases': n[k], 'differ': len(diffs.get(k, []))} for k in sorted(n)}
json.dump({'summary': summary, 'diffs': {f'{k[0]} | {k[1]}': v for k, v in diffs.items()}}, open('out/diffs.json', 'w'), indent=1)
for k, v in summary.items():
    if v['differ']: 
        d = diffs[tuple(k.split(' | '))]; print(k, v, 'e.g.', d[0], d[-1] if len(d) > 1 else '')
print('lines compared:', sum(n.values()), 'differing:', sum(len(v) for v in diffs.values()))
