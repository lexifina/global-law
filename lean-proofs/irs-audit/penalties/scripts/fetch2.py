#!/usr/bin/env python3
"""Fetch every inventoried opinion PDF (one docket entry per opinion), adaptive 4->8 concurrency, resumable.
Order: 2020-2026, 2010-2019, older."""
import json, os, sys, time, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__)); import dawson
D = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties')
inv = json.load(open(D + '/data2/inventory.json'))
def band(y): return 0 if y >= 2020 else 1 if y >= 2010 else 2
todo = []
for o in sorted(inv, key=lambda o: (band(o['year']), -o['year'])):
    e = [x for x in o['entries'] if x['docketEntryId'] == o['pick']][0]
    fn = '%s/cache/pdf/%s.pdf' % (D, e['docketEntryId'])
    if not os.path.exists(fn) and not os.path.exists(fn + '.fail'): todo.append((o, e, fn))
print('todo', len(todo), flush=True)
done = [0]; ok = [0]; t0 = time.time(); L = threading.Lock()
def one(a):
    o, e, fn = a
    u = dawson.get('%s/%s/%s/public-document-download-url' % (dawson.B, e['docketNumber'], e['docketEntryId']))
    pdf = dawson.get(json.loads(u)['url']) if u else None
    if pdf:
        open(fn + '.tmp', 'wb').write(pdf); os.replace(fn + '.tmp', fn)
    else:
        open(fn + '.fail', 'w').write('nourl' if not u else 'nopdf')
    with L:
        done[0] += 1; ok[0] += bool(pdf)
        if done[0] % 100 == 0 or done[0] == len(todo):
            el = time.time() - t0; rate = done[0] / el
            print('%s done %d/%d ok %d rate %.2f/s conc %d eta %.0f min last_year %d codes %s' % (time.strftime('%H:%M:%S'), done[0], len(todo), ok[0], rate, dawson.G.n, (len(todo) - done[0]) / rate / 60, o['year'], dict(dawson.G.total)), flush=True)
with ThreadPoolExecutor(8) as ex:
    list(ex.map(one, todo))
print('DONE', time.strftime('%H:%M:%S'), flush=True)
