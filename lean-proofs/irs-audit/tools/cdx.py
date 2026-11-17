"""Wayback CDX inventory (extra index only; files themselves come from irs.gov). Sequential, >= 6 s apart, stop at 503/429.
Usage: cdx.py PREFIX TAG  (e.g. irs.gov/pub/irs-wd/ wd). Pages saved to wd/cdx/<TAG>-<N>.txt; resumable."""
import sys, os, time, requests
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); D = H + '/wd/cdx'
UA = 'Mozilla/5.0 (compatible; tax-guidance-audit/1.0; research use)'
pre, tag = sys.argv[1], sys.argv[2]
B = 'https://web.archive.org/cdx/search/cdx?url=%s&matchType=prefix&fl=original&collapse=urlkey&filter=statuscode:200' % pre
s = requests.Session(); s.headers['User-Agent'] = UA
np = D + '/%s-numpages' % tag
if not os.path.exists(np):
    r = s.get('https://web.archive.org/cdx/search/cdx?url=%s&matchType=prefix&showNumPages=true' % pre, timeout=120); print('numpages', r.status_code, r.text.strip()[:50], flush=True)
    if r.status_code != 200: sys.exit('STOP ' + str(r.status_code))
    open(np, 'w').write(r.text.strip()); time.sleep(45)
N = int(open(np).read())
for n in range(N):
    f = D + '/%s-%03d.txt' % (tag, n)
    if os.path.exists(f): continue
    for att in range(3):
        try:
            r = s.get(B + '&page=%d' % n, timeout=180); code = r.status_code
        except Exception as e:
            code = 'ERR ' + type(e).__name__; r = None
        if code == 200: break
        print('page', n, code, flush=True)
        if code in (503, 429, 403): sys.exit('STOP %s' % code)
        time.sleep(30)
    if code != 200: sys.exit('STOP after errors')
    open(f + '.part', 'w').write(r.text); os.replace(f + '.part', f)
    print(tag, 'page', n, '/', N, len(r.text.splitlines()), flush=True)
    time.sleep(45)
print('CDX DONE', tag, flush=True)
