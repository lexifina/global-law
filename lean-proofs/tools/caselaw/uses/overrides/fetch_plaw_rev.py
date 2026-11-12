"""Fetch each public law's text from govinfo (PLAW htm), 104th Congress on, about 1 request/second, cached."""
import collections, os, re, subprocess, sys, time, urllib.request
W = os.path.expanduser('~/Documents/us-caselaw-lean-work'); O = f'{W}/uses/overrides'
first = collections.Counter(l.split('\t')[8] for l in open(f'{O}/cand_rows.tsv', encoding='utf-8'))
alll = {l.split('\t')[3] for l in open(f'{W}/usc/versions.tsv', encoding='utf-8') if l.split('\t')[2] == 'law'}
order = [k for k, _ in first.most_common()][::-1]
log = open(f'{O}/cache/plaw.log', 'a', encoding='utf-8', newline='\n')
for lab in order:
    m = re.fullmatch(r'Pub\. L\. (\d+)-(\d+)', lab)
    if not m or int(m.group(1)) < 104: continue
    c, n = m.groups(); fn = f'{O}/cache/plaw/PLAW-{c}publ{n}.htm'
    if os.path.exists(fn) or os.path.exists(fn + '.missing'): continue
    url = f'https://www.govinfo.gov/content/pkg/PLAW-{c}publ{n}/html/PLAW-{c}publ{n}.htm'
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (statute research; low rate)'})
        data = urllib.request.urlopen(req, timeout=120).read()
        open(fn, 'wb').write(data); log.write(f'{lab}\t200\t{len(data)}\n')
    except urllib.error.HTTPError as e:
        log.write(f'{lab}\t{e.code}\n')
        if e.code == 404: open(fn + '.missing', 'w').close()
        if e.code in (403, 429): log.flush(); time.sleep(60)
    except Exception as e:
        log.write(f'{lab}\terr {e}\n')
    log.flush()
    time.sleep(max(0, 1.2 - (time.time() - t0)))
print('done')
