"""Collection 11 harvest on irs.gov /pub/ (sequential, polite, resumable): Chief Counsel notices (irs-ccdm),
generic legal advice memoranda (irs-utl; lanoa from 2022), field attorney advice (irs-lafa, weekly numbering), actions on
decisions (irs-aod). File naming from the Pile of Law url fields (wd/pile_inventory.json); each year/week tries the
naming variants seen there and stops after a run of misses. Then runs the full irs-wd enumeration (harvest_queue.py D)."""
import os, sys, json, subprocess
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/tools'))
import fetch
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); S = H + '/wd/c11_state.json'
st = json.load(open(S)) if os.path.exists(S) else {}
def save(): json.dump(st, open(S + '.tmp', 'w'), indent=0); os.replace(S + '.tmp', S)
def log(*a): print(*a, flush=True)
def run(key, url_fn, nmax=200, misses=4):
    if key in st: return
    found = []; miss = 0; n = 0
    while miss < misses and n < nmax:
        n += 1
        hit = None
        for u in url_fn(n):
            f, code = fetch.get(u)
            if code in ('403', '429'): log('STOP', code, u); save(); sys.exit()
            if f: hit = u; break
        if hit: found.append(hit.rsplit('/', 1)[1]); miss = 0
        else: miss += 1
    st[key] = found; save(); log(key, len(found))
B = 'https://www.irs.gov/pub/'
for y in range(1998, 2027):
    run('ccdm-%d' % y, lambda n: [B + 'irs-ccdm/cc-%d-%03d.pdf' % (y, n), B + 'irs-ccdm/CC-%d-%03d.pdf' % (y, n), B + 'irs-ccdm/cc_%d_%03d.pdf' % (y, n)])
for y in range(1998, 2027):
    run('utl-%d' % y, lambda n: [B + 'irs-utl/am%d%03d.pdf' % (y, n), B + 'irs-utl/am%d-%03d.pdf' % (y, n), B + 'irs-utl/AM%d-%03d.pdf' % (y, n),
                                  B + 'irs-lafa/am%d%03d.pdf' % (y, n), B + 'lanoa/am-%d-%03d.pdf' % (y, n)])
for y in range(1995, 2027):
    run('aod-%d' % y, lambda n: [B + 'irs-aod/aod-%d-%02d.pdf' % (y, n), B + 'irs-aod/aod%d%02d.pdf' % (y, n), B + 'irs-aod/AOD-%d-%02d.pdf' % (y, n)], misses=3)
for y in range(1999, 2027):
    for w in range(1, 54):
        run('lafa-%d-%02d' % (y, w), lambda n: [B + 'irs-lafa/%d%02d%02df.pdf' % (y, w, n), B + 'irs-lafa/%d%02d%02dF.pdf' % (y, w, n), B + 'irs-lafa/%02d%02d%02df.pdf' % (y % 100, w, n)], misses=3)
log('C11 DONE')
subprocess.run([sys.executable, H + '/tools/harvest_queue.py', 'D'])
