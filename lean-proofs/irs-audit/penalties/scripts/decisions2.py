#!/usr/bin/env python3
"""Final amounts: for each target opinion (parsed with penalties and decided under Rule 155, or flagged), read the
docket's public entries, find the decision entries and try to download them. Stipulated decisions and computations are
private in DAWSON (403 'Unauthorized to access private document'): recorded as such, not counted as errors.
Paper-era decisions without an attached file are recorded too. Resumable (per-docket JSON in cache/docket/)."""
import json, os, sys, time, threading, urllib.request, urllib.error, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__)); import dawson
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties')
C = H + '/cache'; os.makedirs(C + '/docket', exist_ok=True); os.makedirs(C + '/dec', exist_ok=True)
G = dawson.G


def get(url):
    """200 -> bytes; 403 private -> 'PRIVATE'; 404 -> None. Private 403s are released as code 'private' (not errors)."""
    for a in range(5):
        G.acquire(); code = None; data = None; body = ''
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': dawson.UA}), timeout=120) as r:
                data = r.read(); code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
            try: body = e.read()[:300].decode('utf-8', 'ignore')
            except Exception: body = ''
            if code == 403 and 'private document' in body: code = 'private'
            elif code == 403 and 'sealed' in body: code = 'sealed'
        except Exception as e:
            code = 'ERR:' + type(e).__name__
        finally:
            G.release(200 if code in ('private', 'sealed') else code)
        with dawson.LOGL:
            dawson.LOG.write('%s\t%s\t%s\n' % (url.split('?X-Amz')[0], code, time.strftime('%Y-%m-%dT%H:%M:%S'))); dawson.LOG.flush()
        if code == 200: return data
        if code == 'private': return 'PRIVATE'
        if code == 'sealed': return 'SEALED'
        if code in (400, 404): return None
        time.sleep(10 * (a + 1))
    return None


DEC_CODES = {'DEC', 'SDEC', 'OAD', 'ODD', 'ODJ', 'ODL', 'ODS', 'ORAP'}


def one(docket):
    fn = '%s/docket/%s.json' % (C, docket)
    if os.path.exists(fn):
        return json.load(open(fn))
    d = get('%s/cases/%s/docket-entries' % (dawson.B, docket))
    if d is None or d == 'PRIVATE':
        res = dict(docket=docket, status='no docket record' if d is None else 'docket private', decisions=[])
        json.dump(res, open(fn, 'w')); return res
    E = json.loads(d)['docketEntries']
    decs = [e for e in E if e.get('eventCode') in DEC_CODES or ('ecision' in (e.get('documentType') or '') and 'Proposed' not in (e.get('documentType') or '') and 'Motion' not in (e.get('documentType') or ''))]
    out = []
    for e in decs:
        r = dict(eventCode=e.get('eventCode'), documentType=e.get('documentType'), title=(e.get('documentTitle') or '')[:160],
                 filingDate=(e.get('filingDate') or '')[:10], attached=e.get('isFileAttached'), docketEntryId=e.get('docketEntryId'))
        if not e.get('isFileAttached'):
            r['result'] = 'no file attached (paper-era entry)'
        else:
            pf = '%s/dec/%s.pdf' % (C, e['docketEntryId'])
            if os.path.exists(pf):
                r['result'] = 'fetched'
            else:
                u = get('%s/%s/%s/public-document-download-url' % (dawson.B, docket, e['docketEntryId']))
                if u == 'PRIVATE':
                    r['result'] = 'private (403)'
                elif u == 'SEALED':
                    r['result'] = 'sealed (403)'
                elif u is None:
                    r['result'] = 'no url'
                else:
                    pdf = get(json.loads(u)['url'])
                    if pdf and pdf != 'PRIVATE':
                        open(pf, 'wb').write(pdf); r['result'] = 'fetched'
                    else:
                        r['result'] = 'download failed'
        out.append(r)
    res = dict(docket=docket, status='ok', n_entries=len(E), decisions=out)
    json.dump(res, open(fn, 'w')); return res


if __name__ == '__main__':
    P = json.load(open(H + '/data2/parsed.json'))
    F = json.load(open(H + '/data2/flags.json'))
    flagged = {f['id'] for f in F}
    targets = []
    for o in P:
        if o['status'] != 'parsed':
            continue
        if o['decision'] == 'Rule 155' or o['id'] in flagged:
            targets.append(o['docket'])
    targets = list(dict.fromkeys(targets))
    print('dockets', len(targets), flush=True)
    done = [0]; L = threading.Lock(); t0 = time.time()
    def w(dk):
        r = one(dk)
        with L:
            done[0] += 1
            if done[0] % 100 == 0:
                print(time.strftime('%H:%M:%S'), done[0], 'conc', G.n, dict(G.total), flush=True)
        return r
    with ThreadPoolExecutor(8) as ex:
        R = list(ex.map(w, targets))
    c = collections.Counter(); c2 = collections.Counter()
    for r in R:
        c[r['status']] += 1
        for d in r['decisions']:
            c2[(d['eventCode'], d['result'])] += 1
    print(dict(c)); print(c2.most_common(30))
    json.dump(R, open(H + '/data2/decisions_index.json', 'w'))
    print('DONE', time.strftime('%H:%M:%S'), flush=True)
