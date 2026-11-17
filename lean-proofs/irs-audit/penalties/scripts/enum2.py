#!/usr/bin/env python3
"""Enumerate every DAWSON opinion matching the penalty keywords, per year (and per type / half-year if a query hits 5,000)."""
import json, os, sys, urllib.parse, collections, re
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__)); import dawson
D = dawson.D; S = D + '/search2'; os.makedirs(S, exist_ok=True)
KWS = ['6662', '6663', '6651', '6654', '6662(h)', '6651(f)', '6751(b)', '"accuracy-related penalty"', '"addition to tax"', '"additions to tax"', '"fraud penalty"']
TYPES = ['MOP', 'SOP', 'TCOP', 'OST']
def q(kw, start, end, types):
    fn = '%s/%s__%s_%s__%s.json' % (S, re.sub(r'[^0-9a-z]+', '_', kw.lower()).strip('_'), start.replace('/', ''), end.replace('/', ''), '-'.join(types))
    if os.path.exists(fn): return json.load(open(fn))
    url = dawson.B + '/opinion-search?' + urllib.parse.urlencode({'keyword': kw, 'opinionTypes': ','.join(types), 'dateRange': 'customDates', 'startDate': start, 'endDate': end})
    d = dawson.get(url)
    if d is None: raise RuntimeError('fail ' + url)
    r = json.loads(d)['results']; json.dump(r, open(fn, 'w')); return r
import time
TODAY = time.strftime('%m/%d/%Y')
def endd(md, y):
    e = '%s/%d' % (md, y)
    return TODAY if (y, md) > (int(TODAY[-4:]), TODAY[:5]) else e
def year(kw, y):
    r = q(kw, '01/01/%d' % y, endd('12/31', y), TYPES)
    if len(r) < 5000: return r
    out = []
    for t in TYPES:
        for a, b in (('01/01', '06/30'), ('07/01', '12/31')):
            rr = q(kw, '%s/%d' % (a, y), endd(b, y), [t])
            if len(rr) >= 5000: print('STILL CAPPED', kw, y, t, a, flush=True)
            out += rr
    return out
if __name__ == '__main__':
    jobs = [(k, y) for k in KWS for y in range(1980, 2027)]
    hits = collections.defaultdict(set); rec = {}
    with ThreadPoolExecutor(8) as ex:
        for (k, y), r in zip(jobs, ex.map(lambda j: year(*j), jobs)):
            for x in r:
                rec[x['docketEntryId']] = x; hits[x['docketEntryId']].add(k)
    for i, x in rec.items(): x['keywords'] = sorted(hits[i])
    json.dump(list(rec.values()), open(D + '/inventory_entries.json', 'w'))
    print('entries', len(rec), dict(dawson.G.total), flush=True)
