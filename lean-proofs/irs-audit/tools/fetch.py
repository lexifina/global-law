"""Polite, resumable fetcher. Usage: fetch.py URL [URL ...] or fetch.py -f list.txt
Sequential, >= SLEEP s between requests, generic UA, skips files already cached, logs every request.
Cache path: ~/irs-audit/cache/<host>/<path>. A 404 is recorded in cache/_status.tsv and not retried."""
import sys, os, time, urllib.request, urllib.error, urllib.parse
UA = 'Mozilla/5.0 (compatible; tax-guidance-audit/1.0; research use)'
SLEEP = float(os.environ.get('SLEEP', '1.5'))
C = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/cache')
ST = os.path.join(C, '_status.tsv')
done = {}
if os.path.exists(ST):
    for l in open(ST):
        p = l.rstrip('\n').split('\t')
        if len(p) >= 2: done[p[0]] = p[1]
def path(u):
    p = urllib.parse.urlparse(u); q = p.path.lstrip('/') or 'index.html'
    if p.path.endswith('/'): q += 'index.html'
    if p.query: q += '__' + p.query.replace('/', '_').replace('&', '_')
    f = os.path.join(C, p.netloc, q)
    if os.path.isfile(f): return f
    if '.' not in os.path.basename(q): f = os.path.join(f, 'index.html')
    return f
def get(u):
    f = path(u)
    if os.path.exists(f): return f, 'cached'
    if done.get(u, '').startswith('4'): return None, done[u]
    req = urllib.request.Request(u, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=int(os.environ.get("FETCH_TIMEOUT", "60"))) as r:
            data = r.read(); code = str(r.status)
        if u.lower().endswith('.pdf') and not data[:5].startswith(b'%PDF'):
            raise urllib.error.HTTPError(u, 415, 'not a PDF', None, None)
        os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f + '.part', 'wb').write(data); os.replace(f + '.part', f)
    except urllib.error.HTTPError as e:
        code = str(e.code); f = None
    except Exception as e:
        code = 'ERR ' + type(e).__name__; f = None
    with open(ST, 'a') as s: s.write(f'{u}\t{code}\t{time.strftime("%Y-%m-%dT%H:%M:%S")}\n')
    done[u] = code
    time.sleep(SLEEP)
    return f, code
if __name__ == '__main__':
    urls = sys.argv[1:]
    if urls and urls[0] == '-f': urls = [l.strip() for l in open(urls[1]) if l.strip() and not l.startswith('#')]
    stop429 = 0
    for u in urls:
        f, code = get(u)
        print(code, u, f or '', flush=True)
        if code in ('429', '403'):
            stop429 += 1
            if stop429 >= 3: print('STOP: repeated 403/429, backing off', flush=True); break
