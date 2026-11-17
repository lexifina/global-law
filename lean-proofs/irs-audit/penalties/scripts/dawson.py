"""Shared concurrent DAWSON client: generic UA, adaptive concurrency (4 -> 8), error-window backoff, request log."""
import json, os, threading, time, urllib.request, urllib.parse, urllib.error, collections
UA = 'Mozilla/5.0 (compatible; research-audit/1.0)'
B = 'https://public-api.dawson.ustaxcourt.gov/public-api'
D = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties/cache')
LOGL = threading.Lock()
LOG = open(D + '/_status.tsv', 'a')
class Gate:
    """Concurrency gate. Window = 60 s. >1% errors (min 2) in a window -> halve + pause 60 s.
    Clean 120 s at current level -> +2 (max 8). >=20 403s within a window twice -> stop."""
    def __init__(s, start=4, top=8):
        s.n = start; s.top = top; s.active = 0; s.cv = threading.Condition(); s.win = collections.deque()
        s.paused_until = 0; s.last_change = time.time(); s.stop = False; s.f403_windows = 0; s.total = collections.Counter()
    def acquire(s):
        with s.cv:
            while (s.active >= s.n or time.time() < s.paused_until) and not s.stop:
                s.cv.wait(1)
            if s.stop: raise SystemExit('stopped: persistent 403')
            s.active += 1
    def release(s, code):
        with s.cv:
            s.active -= 1; now = time.time(); s.win.append((now, code)); s.total[code] += 1
            while s.win and s.win[0][0] < now - 60: s.win.popleft()
            errs = sum(1 for _, c in s.win if c != 200 and c != 404)
            n403 = sum(1 for _, c in s.win if c == 403)
            if n403 >= 20:
                s.f403_windows += 1; s.win.clear()
                if s.f403_windows >= 2: s.stop = True
            if errs >= 2 and errs > 0.01 * len(s.win):
                s.n = max(1, s.n // 2); s.paused_until = now + 60; s.win.clear(); s.last_change = now
                print('BACKOFF -> conc %d (errs %d)' % (s.n, errs), flush=True)
            elif now - s.last_change > 120 and s.n < s.top and len(s.win) >= 20:
                s.n = min(s.top, s.n + 2); s.last_change = now
                print('UP -> conc %d' % s.n, flush=True)
            s.cv.notify_all()
G = Gate()
def get(url, tries=5):
    for a in range(tries):
        G.acquire()
        code = None; data = None
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read(); code = r.status
        except urllib.error.HTTPError as e: code = e.code
        except Exception as e: code = 'ERR:' + type(e).__name__
        finally:
            G.release(code)
        with LOGL:
            LOG.write('%s\t%s\t%s\n' % (url.split('?X-Amz')[0], code, time.strftime('%Y-%m-%dT%H:%M:%S'))); LOG.flush()
        if code == 200: return data
        if code in (400, 404): return None
        time.sleep(10 * (a + 1))
    return None
