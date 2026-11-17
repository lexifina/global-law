"""Concurrent, resumable fetcher. Same cache and status file as fetch.py (cache/<host>/<path>, cache/_status.tsv;
a 4xx is recorded and not retried). Per-host adaptive limiter: if 403/429/503 exceed ~1% of responses in any 60 s window
(and at least 2), concurrency halves and the host pauses 60 s; if 403s trigger two backoffs in a row the host stops.
Generic honest UA, no proxies. HEAD first on irs.gov (GET only on 200). Robots: never request /downloads/ or
/written-determinations paths."""
import os, time, threading, collections, urllib.parse, requests
import fetch  # path() and UA
UA = fetch.UA
C = fetch.C; ST = fetch.ST
_slock = threading.Lock()
done = dict(fetch.done)
BARRED = ('/downloads/', '/written-determinations', '/applicable-federal-rates', '/actions-on-decisions', '/information-letters', '/chief-counsel-notices', '/draft-tax-forms', '/forms-instructions-and-publications', '/prior-year-forms-and-instructions', '/internal-revenue-bulletins', '/instructions-and-publications-xml-source-files', 'search')
class Stop(Exception): pass
class Host:
    def __init__(s, name, limit):
        s.name, s.limit, s.active = name, limit, 0
        s.cv = threading.Condition(); s.win = collections.deque(); s.paused = 0; s.stopped = False; s.last403 = False
        s.n = collections.Counter()
    def acquire(s):
        with s.cv:
            while True:
                if s.stopped: raise Stop(s.name)
                if s.active < s.limit and time.time() >= s.paused: s.active += 1; return
                s.cv.wait(1)
    def release(s, code):
        with s.cv:
            s.active -= 1; now = time.time(); s.n[code[:3]] += 1
            s.win.append((now, code))
            while s.win and s.win[0][0] < now - 60: s.win.popleft()
            bad = [c for _, c in s.win if c in ('403', '429', '503')]
            if len(bad) >= 2 and len(bad) > 0.01 * len(s.win):
                has403 = '403' in bad
                if has403 and s.last403:
                    s.stopped = True; print('STOP host', s.name, 'persistent 403', flush=True)
                else:
                    s.limit = max(1, s.limit // 2); s.paused = now + 60; s.last403 = has403
                    print('BACKOFF', s.name, 'bad', collections.Counter(bad), 'of', len(s.win), '-> limit', s.limit, flush=True)
                s.win.clear()
            elif len(s.win) >= 50 and not bad:
                s.last403 = False
            s.cv.notify_all()
HOSTS = {}
def host(name, limit=None):
    if name not in HOSTS: HOSTS[name] = Host(name, limit or 4)
    elif limit: HOSTS[name].limit = limit
    return HOSTS[name]
_tl = threading.local()
def sess():
    if not hasattr(_tl, 's'):
        _tl.s = requests.Session(); _tl.s.headers['User-Agent'] = UA
        a = requests.adapters.HTTPAdapter(pool_connections=4, pool_maxsize=4); _tl.s.mount('https://', a)
    return _tl.s
def record(u, code):
    with _slock:
        done[u] = code
        with open(ST, 'a') as f: f.write(f'{u}\t{code}\t{time.strftime("%Y-%m-%dT%H:%M:%S")}\n')
def get(u, head_first=True, timeout=60):
    """Return (local_path or None, code). Cached files and recorded 4xx are not requested again."""
    p = urllib.parse.urlparse(u)
    if any(b in p.path for b in BARRED): return None, 'barred'
    f = fetch.path(u)
    if os.path.exists(f): return f, 'cached'
    c0 = done.get(u, '')
    if c0 in PERM: return None, c0
    for att in range(3):
        f2, code = _get(u, f, head_first, timeout)
        if f2 or code in PERM or code == 'barred': return f2, code
        time.sleep(15 * (att + 1))
    return None, code
PERM = ('404', '410', '415')
def _get(u, f, head_first, timeout):
    p = urllib.parse.urlparse(u)
    h = host(p.netloc)
    h.acquire(); code = 'ERR'
    try:
        s = sess()
        if head_first:
            r = s.head(u, timeout=30, allow_redirects=True); code = str(r.status_code)
            if r.status_code != 200: record(u, code); return None, code
        r = s.get(u, timeout=timeout, stream=True); code = str(r.status_code)
        if r.status_code != 200: r.close(); record(u, code); return None, code
        os.makedirs(os.path.dirname(f), exist_ok=True)
        tmp = f + '.part.%d' % threading.get_ident(); first = b''
        with open(tmp, 'wb') as o:
            for ch in r.iter_content(1 << 16):
                if not first: first = ch[:5]
                o.write(ch)
        if u.lower().endswith('.pdf') and not first.startswith(b'%PDF'):
            os.remove(tmp); code = '415'; record(u, code); return None, code
        os.replace(tmp, f); record(u, code); return f, code
    except Stop: raise
    except Exception as e:
        code = 'ERR ' + type(e).__name__; record(u, code); return None, code
    finally:
        h.release(code)
