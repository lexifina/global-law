"""Fetch the committee reports each law's LEGISLATIVE HISTORY note lists (govinfo CRPT htm), for laws that are the
first rewriting law of a Supreme Court or court of appeals citation within ten years. About 1 request/second, cached."""
import collections, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import lawtext as LT
O = os.path.expanduser('~/Documents/us-caselaw-lean-work/uses/overrides')
cnt = collections.Counter()
for l in open(f'{O}/cand_rows.tsv', encoding='utf-8'):
    f = l.split('\t')
    if f[3] in ('S', 'A') and int(f[10]) <= 120: cnt[f[8]] += 1 + 20 * (f[3] == 'S')
log = open(f'{O}/cache/crpt.log', 'a', encoding='utf-8', newline='\n')
def get(url, fn):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (statute research; low rate)'})
    t0 = time.time()
    try:
        data = urllib.request.urlopen(req, timeout=180).read()
        if b'Page Not Found | GovInfo' in data[:5000]:
            log.write(f'{url}\tnotfound\n'); ok = False
        else:
            open(fn, 'wb').write(data); log.write(f'{url}\t200\t{len(data)}\n'); ok = True
    except urllib.error.HTTPError as e:
        log.write(f'{url}\t{e.code}\n'); ok = False
        if e.code in (403, 429): log.flush(); time.sleep(60)
    except Exception as e:
        log.write(f'{url}\terr {e}\n'); ok = False
    log.flush(); time.sleep(max(0, 1.2 - (time.time() - t0)))
    return ok
for lab, _ in cnt.most_common():
    t = LT.text(lab)
    if not t: continue
    for h, c, n in LT.reports(t)[:4]:
        base = f'CRPT-{c}{h}rpt{n}'
        fn = f'{O}/cache/crpt/{base}.htm'
        if os.path.exists(fn) or os.path.exists(fn + '.missing') or os.path.exists(f'{O}/cache/crpt/{base}-pt1.htm'): continue
        if get(f'https://www.govinfo.gov/content/pkg/{base}/html/{base}.htm', fn): continue
        if not get(f'https://www.govinfo.gov/content/pkg/{base}/html/{base}-pt1.htm', f'{O}/cache/crpt/{base}-pt1.htm'):
            open(fn + '.missing', 'w').close()
print('done')
