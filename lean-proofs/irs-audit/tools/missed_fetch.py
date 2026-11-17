"""Further sources on irs.gov (beyond the 12 collections) that need HTML pages for their links (pages allowed by robots.txt; /pub/ files allowed).
One sequential stream (1 request at a time; 0.5 s apart) next to irs_harvest.py's 8, so irs.gov sees at most 9.
Stages: T actuarial tables page + /pub/irs-tege files + Pubs 1457-1459; P current Pubs 15, 15-T, 15-A, 15-B and
Notice 1036; S SOI rate/share and historical tables (/pub/irs-soi files linked from the pages); A MeF ATS pages and their
/pub/ PDFs; L changes-to-current-forms-publications (all listing pages and each item page). Resumable via cfetch cache."""
import os, sys, re, time, html, urllib.parse
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/tools'))
import cfetch
cfetch.host('www.irs.gov', 1)
B = 'https://www.irs.gov'
def log(*a): print(*a, flush=True)
def get(u, head=False):
    f, code = cfetch.get(u, head_first=head); time.sleep(0.5); return f, code
def links(f, base):
    t = open(f, errors='replace').read()
    return [urllib.parse.urljoin(base, html.unescape(h)) for h in re.findall(r'href="([^"#]+)"', t)]
def files_from(page, pat):
    f, code = get(page); log('PAGE', code, page)
    if not f: return []
    out = sorted({u.split('?')[0] for u in links(f, page) if re.search(pat, u, re.I) and 'irs.gov/pub/' in u})
    for u in out:
        g, c = get(u, head=True); log(' FILE', c, u)
    return out
st = sys.argv[1] if len(sys.argv) > 1 else 'TPSAL'
if 'T' in st:
    files_from(B + '/retirement-plans/actuarial-tables', r'\.(xlsx?|pdf|zip)$')
    for n in ('p1457', 'p1458', 'p1459'): log('PUB', get(B + '/pub/irs-pdf/%s.pdf' % n, True)[1], n)
if 'P' in st:
    for n in ('p15', 'p15t', 'p15a', 'p15b', 'n1036', 'p17', 'p501', 'p505', 'p596', 'p915', 'p939', 'p590a', 'p590b', 'p946', 'p1542'):
        log('PUB', get(B + '/pub/irs-pdf/%s.pdf' % n, True)[1], n)
if 'S' in st:
    for p in ('/statistics/soi-tax-stats-individual-income-tax-rates-and-tax-shares', '/statistics/soi-tax-stats-historical-data-tables',
              '/statistics/soi-tax-stats-individual-statistical-tables-by-tax-rate-and-income-percentile'):
        files_from(B + p, r'\.(xlsx?|csv|pdf)$')
if 'A' in st:
    p0 = B + '/e-file-providers/tax-year-2025-form-1040-series-and-extensions-modernized-e-file-mef-assurance-testing-system-ats-information'
    files_from(p0, r'\.(pdf|zip|xml|xlsx?)$')
    f, _ = get(B + '/e-file-providers/modernized-e-file-mef-assurance-testing-system-ats')
    if f:
        for u in sorted({u.split('?')[0] for u in links(f, B) if 'assurance-testing' in u or '-ats' in u}):
            if u.startswith(B + '/e-file-providers/') and u != p0: files_from(u, r'\.(pdf|zip|xml|xlsx?)$')
if 'L' in st:
    items = set()
    for n in range(0, 40):
        u = B + '/forms-pubs/changes-to-current-forms-publications' + ('?page=%d' % n if n else '')
        f, code = get(u); log('LIST', n, code)
        if not f: break
        new = {x.split('?')[0] for x in links(f, B) if re.match(re.escape(B) + r'/forms-pubs/[a-z0-9-]+$', x.split('?')[0]) and x.split('?')[0] != B + '/forms-pubs/changes-to-current-forms-publications'}
        if not new - items and n > 0: break
        items |= new
    log('L items', len(items))
    for u in sorted(items): get(u)
    open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/changes_items.txt'), 'w').write('\n'.join(sorted(items)))
log('FURTHER SOURCES FETCH DONE', dict(cfetch.host('www.irs.gov').n))
