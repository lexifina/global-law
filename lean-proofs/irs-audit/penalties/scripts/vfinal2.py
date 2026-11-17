#!/usr/bin/env python3
"""vfinal2.py <mode> <n> <seed>: mode=all|flag|increased. Shows notice figures, parsed final figures and decision text."""
import json, re, sys, random, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties'); D2 = H + '/data2'
FIN = json.load(open(D2 + '/final.json')); P = {o['id']: o for o in json.load(open(D2 + '/parsed.json'))}
mode, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
fl = {}
for l in open(D2 + '/classified_final.tsv'):
    rid, y, k, v = l.rstrip('\n').split('\t')
    if v.startswith('FLAG'): fl.setdefault(rid.split('#')[0], []).append((y, v[6:40]))
ids = [i for i, v in FIN.items() if v.get('final')]
if mode == 'flag': ids = [i for i in ids if i in fl]
if mode == 'increased':
    ids = [i for i in ids if any(r.get('pen') and str(r['year']) in FIN[i]['final'] and any(FIN[i]['final'][str(r['year'])].get(k, -1) > v + 1 for k, v in r['pen'].items() if k in ('6662(a)', '6663', '6651(a)(1)')) for r in P[i]['recs'])]
random.seed(seed)
for i in random.sample(ids, min(n, len(ids))):
    v = FIN[i]; o = P[i]
    t = re.sub(r'\s+', ' ', open(D2 + '/dec/%s.txt' % v['decision_entry'], errors='ignore').read())
    m = re.search(r'ORDERED AND DECIDED|DECIDED|ORDERED', t); s = m.start() if m else 0
    print('##', v.get('cite'), v['docket'], v['decision_event'], v['decision_date'], 'flags', fl.get(i, ''))
    print('  notice', [(r['year'], r.get('deficiency'), r.get('pen')) for r in o['recs'] if r.get('pen')][:4])
    print('  final ', v['final'])
    print('  text  ', t[s:s + 520])
