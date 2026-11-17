#!/usr/bin/env python3
"""Polite sequential fetcher for Tax Court (DAWSON) opinions. One request at a time, >=2 s between API calls,
back off on 403/429/503. Generic UA. Logs every request to cache/_status.tsv."""
import json, os, random, sys, time, urllib.request, urllib.parse, urllib.error, collections
UA = 'Mozilla/5.0 (compatible; research-audit/1.0)'
B = 'https://public-api.dawson.ustaxcourt.gov/public-api'
D = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties/cache')
os.makedirs(D + '/search', exist_ok=True); os.makedirs(D + '/pdf', exist_ok=True)
LOG = open(D + '/_status.tsv', 'a')
last = [0.0]
def get(url, binary=False, spacing=2.0):
    for attempt in range(6):
        wait = spacing - (time.time() - last[0])
        if wait > 0: time.sleep(wait)
        last[0] = time.time()
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read(); code = r.status
        except urllib.error.HTTPError as e:
            code = e.code; data = None
        except Exception as e:
            code = 'ERR:' + type(e).__name__; data = None
        LOG.write('%s\t%s\t%s\n' % (url.split('?X-Amz')[0], code, time.strftime('%Y-%m-%dT%H:%M:%S'))); LOG.flush()
        if code == 200: return data
        if code in (403, 429, 503) or str(code).startswith('ERR') or code == 500:
            time.sleep(30 * (attempt + 1)); continue
        return None
    return None
def search(kw):
    fn = '%s/search/%s.json' % (D, kw.replace(' ', '_').replace('(', '').replace(')', ''))
    if os.path.exists(fn): return json.load(open(fn))
    data = get(B + '/opinion-search?' + urllib.parse.urlencode({'keyword': kw, 'opinionTypes': 'MOP,SOP,TCOP'}))
    res = json.loads(data)['results']; json.dump(res, open(fn, 'w')); return res
if __name__ == '__main__':
    kws = ['6662', '6651', '6663', '6654', '6662(h)', '6751(b)']
    pools = {k: search(k) for k in kws}
    for k, v in pools.items(): print(k, len(v), flush=True)
    # stratified sample: per keyword, per filing year
    random.seed(20261117)
    quota = {'6662': 18, '6651': 6, '6663': 5, '6654': 3, '6662(h)': 3, '6751(b)': 0}
    chosen = collections.OrderedDict()
    for k in kws:
        by = collections.defaultdict(list)
        for r in pools[k]:
            by[r['filingDate'][:4]].append(r)
        for y in sorted(by):
            rs = sorted(by[y], key=lambda r: r['docketEntryId']); random.shuffle(rs)
            for r in rs[:quota[k]]:
                chosen.setdefault(r['docketEntryId'], dict(r, sampled_by=k))
    json.dump(list(chosen.values()), open(D + '/sample.json', 'w'), indent=0)
    print('sample', len(chosen), flush=True)
    for i, r in enumerate(chosen.values()):
        fn = '%s/pdf/%s.pdf' % (D, r['docketEntryId'])
        if os.path.exists(fn): continue
        u = get('%s/%s/%s/public-document-download-url' % (B, r['docketNumber'], r['docketEntryId']))
        if not u: print('nourl', r['docketNumber'], flush=True); continue
        pdf = get(json.loads(u)['url'], spacing=1.0)
        if pdf: open(fn, 'wb').write(pdf)
        if i % 25 == 0: print(i, time.strftime('%H:%M:%S'), flush=True)
    print('done', flush=True)
