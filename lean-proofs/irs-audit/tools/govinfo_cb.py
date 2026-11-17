"""Collection 12: the 92 Cumulative Bulletins from GovInfo, 8 packages at a time (cfetch limiter on www.govinfo.gov).
Each package: <id>.pdf, else parts <id>-1.pdf, -2, ... until a miss (GovInfo serves HTML 200 for a missing part -> 415).
Resumable (cache + _status.tsv). Then pdftotext via cb_text.py."""
import os, sys, concurrent.futures as cf
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/tools'))
import cfetch
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
cfetch.host('www.govinfo.gov', 8)
def one(line):
    p = [x.strip() for x in line.split('\t')]
    date, pkg = p[0], p[2]
    base = 'https://www.govinfo.gov/content/pkg/%s/pdf/%s' % (pkg, pkg)
    f, code = cfetch.get(base + '.pdf', head_first=False, timeout=1800)
    k = 0
    if not f:
        while True:
            f2, code = cfetch.get(base + '-%d.pdf' % (k + 1), head_first=False, timeout=1800)
            if not f2: break
            k += 1
    print('CB', date[:4], pkg, 'whole' if f else 'parts %d' % k, code, flush=True)
    return date[:4], bool(f) or k > 0
lines = [l for l in open(H + '/src/govinfo/cb_packages.tsv').read().splitlines() if l.count('\t') >= 2]
lines.sort(key=lambda l: (0 if '1984' <= l[:4] <= '1995' else 1 if l[:4] < '1984' else 2, l[:4]))
with cf.ThreadPoolExecutor(8) as ex:
    res = list(ex.map(one, lines))
print('A DONE', sum(1 for _, ok in res if ok), 'of', len(res), flush=True)
