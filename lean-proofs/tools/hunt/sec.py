"""Print the text of a Title 26 section (or a subdivision of it) from the OLRC release point.

    python -I tools/hunt/sec.py 224            whole section
    python -I tools/hunt/sec.py 408 d 9        §408(d)(9) only
    python -I tools/hunt/sec.py --grep "last-month"   sections whose text matches (regex), with counts
"""
import json, re, sys, os
DATA = os.path.expanduser('~/Documents/tax-formalization-data/out/t26.json')
P = json.load(open(DATA, encoding='utf-8'))['provisions']
sys.stdout.reconfigure(encoding='utf-8')
if sys.argv[1] == '--grep':
    rx = re.compile(sys.argv[2], re.I); hits = {}
    for p in P:
        if rx.search(p.get('text') or '') or rx.search(p.get('heading') or ''):
            m = re.match(r'/us/usc/t26/s([^/]+)', p['id'])
            if m: hits[m.group(1)] = hits.get(m.group(1), 0) + 1
    for k, v in sorted(hits.items(), key=lambda kv: -kv[1])[:60]: print(f'§{k}: {v}')
    sys.exit()
pid = '/us/usc/t26/s' + sys.argv[1] + ''.join('/' + a for a in sys.argv[2:])
for p in P:
    if p['id'] == pid or p['id'].startswith(pid + '/'):
        depth = p['id'].count('/') - 4
        num = p.get('num') or ''
        print('  ' * depth + (f'({num}) ' if depth else f'§{num} ') + (p.get('heading') or '') + ' ' + (p.get('text') or '') + ('' if p.get('status') == 'in-force' else f"  [{p.get('status')}]"))
