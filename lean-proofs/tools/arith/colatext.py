"""Print every Title 26 subdivision of the given sections that mentions a cost-of-living adjustment,
with its whole enclosing subdivision (so the base amount, base year and rounding rule are visible)."""
import json, re, sys, os
P = json.load(open(os.path.expanduser('~/Documents/tax-formalization-data/out/t26.json'), encoding='utf-8'))['provisions']
sys.stdout.reconfigure(encoding='utf-8')
byid = {p['id']: p for p in P}
for sec in sys.argv[1:]:
    pre = '/us/usc/t26/s' + sec
    hits = [p for p in P if (p['id'] == pre or p['id'].startswith(pre + '/')) and re.search(r'cost-of-living|1\(f\)\(3\)|rounded|multiple of', p.get('text') or '')]
    roots = []
    for p in hits:
        parts = p['id'].split('/')
        r = '/'.join(parts[:max(6, len(parts) - 1)]) if len(parts) > 6 else p['id']
        if not any(r == x or r.startswith(x + '/') for x in roots): roots = [x for x in roots if not x.startswith(r + '/')] + [r]
    print(f'===== §{sec}')
    for r in roots:
        for p in P:
            if p['id'] == r or p['id'].startswith(r + '/'):
                d = p['id'].count('/') - 5
                print('  ' * d + p['id'][len(pre):] + ' ' + (p.get('heading') or '') + ' ' + (p.get('text') or '') + ('' if p.get('status') == 'in-force' else f"  [{p.get('status')}]"))
