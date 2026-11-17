"""irs.gov /pub/ harvest, concurrent (one process holds the irs.gov limiter: 16-way, HEAD then GET on 200, adaptive backoff).
Stages (argv[1], default 'WCE'):
 W  written determinations /pub/irs-wd: every week 1996-2026, both numbering schemes (YYWWNNN and YYYYWWNNN) for every
    year, stop a week/scheme after 12 consecutive misses (n <= 600); plus any irs-wd names in the CDX inventory.
    State: wd/full_state.json  {"YYYY-WW-s": [names]}.
 C  collection 11: irs-ccdm, irs-utl/lanoa, irs-aod, irs-lafa naming variants (state wd/c11_state.json, same keys as
    c11_harvest.py), plus CDX names for those folders and irs-counsel.
 E  prior-year withholding guides and publications: irs-prior/<name>--YYYY.pdf 1995-2025.
Resumable: cached files and recorded 4xx are skipped; finished keys are skipped."""
import os, sys, json, glob, threading, concurrent.futures as cf
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/tools'))
import cfetch
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); B = 'https://www.irs.gov/pub/'
cfetch.host('www.irs.gov', int(os.environ.get('IRS_CONC', '8')))  # measured: 16-way HEAD gives ~3% 403s, 8-way none (21 req/s)
lock = threading.Lock()
unsure = []
def log(*a): print(*a, flush=True)
def load(f): return json.load(open(f)) if os.path.exists(f) else {}
def saver(st, f):
    def save():
        with lock:
            json.dump(st, open(f + '.tmp', 'w')); os.replace(f + '.tmp', f)
    return save
def probe(key, st, save, url_fn, nmax, misses):
    if key in st: return
    found = []; miss = 0; n = 0
    while miss < misses and n < nmax:
        n += 1; hit = None
        for u in url_fn(n):
            f, code = cfetch.get(u)
            if f: hit = u; break
            if code not in cfetch.PERM:
                with lock: unsure.append((key, u))
        if hit: found.append(hit.rsplit('/', 1)[1]); miss = 0
        else: miss += 1
    with lock: st[key] = found
    save(); log(key, len(found))
def recheck(st, save):
    global unsure
    todo, unsure = unsure, []
    for key, u in todo:
        f, code = cfetch.get(u)
        log('recheck', u, code)
        if f:
            with lock: st.setdefault(key, []).append(u.rsplit('/', 1)[1])
    save()
def pool(tasks, n=int(os.environ.get('IRS_CONC', '8'))):
    with cf.ThreadPoolExecutor(n) as ex:
        for fu in [ex.submit(t) for t in tasks]:
            try: fu.result()
            except cfetch.Stop: log('STOPPED (host stop)'); os._exit(2)
def cdx_names(tag):
    out = set()
    for f in glob.glob(H + '/wd/cdx/%s-[0-9]*.txt' % tag):
        for l in open(f):
            u = l.strip()
            if '/pub/' in u: out.add('https://www.irs.gov/pub/' + u.split('/pub/', 1)[1].split('?')[0])
    return sorted(out)
stage = sys.argv[1] if len(sys.argv) > 1 else 'WCE'
if 'W' in stage:
    S = H + '/wd/full_state.json'; st = load(S); save = saver(st, S)
    def num(sch, y, w, n): return ('%02d%02d%03d' % (y % 100, w, n)) if sch == 7 else ('%d%02d%03d' % (y, w, n))
    tasks = []
    for y in range(2026, 1995, -1):
        for w in range(1, 54):
            for sch in (9, 7):
                tasks.append(lambda y=y, w=w, sch=sch: probe('%d-%02d-%d' % (y, w, sch), st, save,
                             lambda n: [B + 'irs-wd/%s.pdf' % num(sch, y, w, n)], 600, 12))
    pool(tasks); recheck(st, save)
    ex = cdx_names('wd'); log('W cdx extra names', len(ex))
    pool([lambda u=u: cfetch.get(u) for u in ex])
    log('W DONE')
if 'C' in stage:
    S = H + '/wd/c11_state.json'; st = load(S); save = saver(st, S)
    T = []
    for y in range(1998, 2027):
        T.append(lambda y=y: probe('ccdm-%d' % y, st, save, lambda n: [B + 'irs-ccdm/cc-%d-%03d.pdf' % (y, n), B + 'irs-ccdm/CC-%d-%03d.pdf' % (y, n), B + 'irs-ccdm/cc_%d_%03d.pdf' % (y, n)], 200, 6))
        T.append(lambda y=y: probe('utl-%d' % y, st, save, lambda n: [B + 'irs-utl/am%d%03d.pdf' % (y, n), B + 'irs-utl/am%d-%03d.pdf' % (y, n), B + 'irs-utl/AM%d-%03d.pdf' % (y, n),
                                  B + 'irs-lafa/am%d%03d.pdf' % (y, n), B + 'lanoa/am-%d-%03d.pdf' % (y, n)], 200, 6))
    for y in range(1995, 2027):
        T.append(lambda y=y: probe('aod-%d' % y, st, save, lambda n: [B + 'irs-aod/aod-%d-%02d.pdf' % (y, n), B + 'irs-aod/aod%d%02d.pdf' % (y, n), B + 'irs-aod/AOD-%d-%02d.pdf' % (y, n)], 99, 5))
    for y in range(2026, 1998, -1):
        for w in range(1, 54):
            T.append(lambda y=y, w=w: probe('lafa-%d-%02d' % (y, w), st, save, lambda n: [B + 'irs-lafa/%d%02d%02df.pdf' % (y, w, n), B + 'irs-lafa/%d%02d%02dF.pdf' % (y, w, n), B + 'irs-lafa/%02d%02d%02df.pdf' % (y % 100, w, n)], 99, 4))
    pool(T); recheck(st, save)
    ex = [u for t in ('ccdm', 'lafa', 'utl', 'aod', 'lanoa', 'counsel') for u in cdx_names(t)]; log('C cdx extra names', len(ex))
    pool([lambda u=u: cfetch.get(u) for u in ex])
    log('C DONE')
if 'E' in stage:
    names = ['p15t', 'p15', 'n1036', 'p17', 'p501', 'p505', 'p596', 'p915', 'p939', 'p590', 'p590a', 'p590b', 'p946', 'p15a', 'p15b']
    pool([lambda u=u: cfetch.get(u) for u in [B + 'irs-prior/%s--%d.pdf' % (nm, y) for y in range(2025, 1994, -1) for nm in names]])
    log('E DONE')
log('ALL DONE', dict(cfetch.host('www.irs.gov').n))
