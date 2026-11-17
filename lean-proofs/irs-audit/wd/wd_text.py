"""pdftotext -layout for every harvested irs-wd / Chief Counsel PDF, 8 processes (nice), skipping texts already made -> wd/text/<folder>__<name>.txt"""
import os, glob, subprocess, concurrent.futures as cf
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); TXT = H + '/wd/text'; os.makedirs(TXT, exist_ok=True)
docs = [f for d in ('irs-wd', 'irs-ccdm', 'irs-utl', 'lanoa', 'irs-lafa', 'irs-aod', 'irs-counsel', 'foia') for f in glob.glob(H + '/cache/www.irs.gov/pub/%s/*.pdf' % d)]
def one(f):
    out = TXT + '/' + f.split('/pub/')[1].replace('/', '__') + '.txt'
    if os.path.exists(out): return 0
    subprocess.run(['nice', '-n', '10', 'pdftotext', '-layout', f, out + '.tmp'], stderr=subprocess.DEVNULL, timeout=300)
    if os.path.exists(out + '.tmp'): os.replace(out + '.tmp', out)
    return 1
with cf.ThreadPoolExecutor(8) as ex: n = sum(ex.map(one, docs))
print('texts made', n, 'of', len(docs), flush=True)
