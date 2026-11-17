"""Harvest the Internal Revenue Manual (irs.gov/irm): every part page, then every section page it lists. Resumable."""
import re, os, sys, json
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/tools'))
import fetch
base = 'https://www.irs.gov'
f, _ = fetch.get(base + '/irm')
parts = sorted(set(re.findall(r'href="(?:https://www\.irs\.gov)?(/irm/part\d+)"', open(f, errors='replace').read())))
secs = []
for p in parts:
    f, code = fetch.get(base + p)
    if not f: print('part fail', p, code, flush=True); continue
    s = sorted(set(re.findall(r'href="(?:https://www\.irs\.gov)?(/irm/part\d+/irm_[0-9a-z_-]+)"', open(f, errors='replace').read())))
    print(p, len(s), flush=True); secs += s
pri = {'20': 0, '21': 1, '5': 2, '4': 3, '25': 4, '8': 5, '3': 6}
secs.sort(key=lambda x: (pri.get(x.split('/')[2][4:], 9), x))
json.dump(secs, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/irm/sections.json'), 'w'))
print('sections', len(secs), flush=True)
n = 0
for s in secs:
    f, code = fetch.get(base + s); n += 1
    if n % 50 == 0: print(n, code, s, flush=True)
    if code in ('403', '429'): print('STOP', code, s, flush=True); break
print('DONE', n, flush=True)
