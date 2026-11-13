"""Fetch law texts (govinfo PLAW htm) and committee reports not already in the overrides cache, at most 1 request/second.
Cached under caselaw-lean-2/statutes/cache/{plaw,crpt}.

    python s2_fetch.py laws        # every law in blockchanges.tsv without cached text
    python s2_fetch.py reports F   # reports listed by the laws named one per line in file F
"""
import os, re, sys, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
import common as C
log = open(f'{C.S}/cache/fetch.log', 'a', encoding='utf-8', newline='\n')
def get(url, fn):
    if os.path.exists(fn) or os.path.exists(fn + '.missing'): return os.path.exists(fn)
    t0 = time.time(); ok = False
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (statute research; low rate)'})
        data = urllib.request.urlopen(req, timeout=180).read()
        if b'Page Not Found | GovInfo' in data[:5000]:
            log.write(f'{url}\tnotfound\n')
        else:
            open(fn, 'wb').write(data); log.write(f'{url}\t200\t{len(data)}\n'); ok = True
    except urllib.error.HTTPError as e:
        log.write(f'{url}\t{e.code}\n')
        if e.code == 404: open(fn + '.missing', 'w').close()
        if e.code in (403, 429): log.flush(); time.sleep(60)
    except Exception as e:
        log.write(f'{url}\terr {e}\n')
    log.flush(); time.sleep(max(0, 1.05 - (time.time() - t0)))
    return ok
if sys.argv[1] == 'laws':
    laws = sorted({l.split('\t')[0] for l in open(f'{C.S}/blockchanges.tsv', encoding='utf-8')})
    for lab in laws:
        m = re.fullmatch(r'Pub\. L\. (\d+)-(\d+)', lab)
        if not m or int(m.group(1)) < 104 or C.plaw_file(lab): continue
        c, n = m.groups()
        get(f'https://www.govinfo.gov/content/pkg/PLAW-{c}publ{n}/html/PLAW-{c}publ{n}.htm', f'{C.S}/cache/plaw/PLAW-{c}publ{n}.htm')
else:
    for lab in [l.strip() for l in open(sys.argv[2], encoding='utf-8') if l.strip()]:
        raw = C.raw_law(lab)
        if not raw: continue
        for h, c, n in C.reports(raw)[:4]:
            base = f'CRPT-{c}{h}rpt{n}'
            if C.report_file(base): continue
            if get(f'https://www.govinfo.gov/content/pkg/{base}/html/{base}.htm', f'{C.S}/cache/crpt/{base}.htm'): continue
            if os.path.exists(f'{C.S}/cache/crpt/{base}.htm.missing'): os.remove(f'{C.S}/cache/crpt/{base}.htm.missing')
            if not get(f'https://www.govinfo.gov/content/pkg/{base}/html/{base}-pt1.htm', f'{C.S}/cache/crpt/{base}-pt1.htm'):
                open(f'{C.S}/cache/crpt/{base}.htm.missing', 'w').close()
print('done')
