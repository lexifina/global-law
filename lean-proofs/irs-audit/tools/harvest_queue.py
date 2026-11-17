"""Sequential harvest queue (resumable; one request at a time, >= 1.5 s apart):
 A. Cumulative Bulletins on GovInfo (src/govinfo/cb_packages.tsv): <id>.pdf, else parts <id>-1.pdf, -2, ... until a miss.
 B. Pile of Law (Hugging Face): taxrulings and irs_legal_advice_memos, train + validation.
 D. Written determinations (irs.gov/pub/irs-wd): every week of every year, both numbering schemes, stop after 6 misses."""
import os, sys, json
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/tools'))
os.environ.setdefault('FETCH_TIMEOUT', '600')
import fetch
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
def log(*a): print(*a, flush=True)
stage = sys.argv[1] if len(sys.argv) > 1 else 'ABD'
if 'A' in stage:
    lines = open(H + '/src/govinfo/cb_packages.tsv').read().splitlines()
    lines.sort(key=lambda l: (0 if '1984' <= l[:4] <= '1995' else 1 if l[:4] < '1984' else 2, l[:4]))
    for line in lines:
        p = [x.strip() for x in line.split('\t')]
        if len(p) < 3: continue
        date, title, pkg = p[0], p[1], p[2]
        base = 'https://www.govinfo.gov/content/pkg/%s/pdf/%s' % (pkg, pkg)
        f, code = fetch.get(base + '.pdf')
        k = 0
        if not f:
            while True:
                f2, code = fetch.get(base + '-%d.pdf' % (k + 1))
                if not f2: break
                k += 1
        log('CB', date[:4], pkg, 'whole' if f else 'parts %d' % k, code)
        if code in ('403', '429'): log('STOP CB', code); sys.exit()
    log('A DONE')
if 'B' in stage:
    base = 'https://huggingface.co/datasets/pile-of-law/pile-of-law/resolve/main/data/'
    for n in ('validation.taxrulings.jsonl.xz', 'train.taxrulings.jsonl.xz', 'validation.irs_legal_advice_memos.jsonl.xz', 'train.irs_legal_advice_memos.jsonl.xz'):
        f, code = fetch.get(base + n); log('PILE', n, code)
    log('B DONE')
if 'D' in stage or 'E' in stage:
    # E: prior-year withholding guides and publications with checkable figures, by predictable name
    names = ['p15t', 'p15', 'n1036', 'p17', 'p501', 'p505', 'p596', 'p915', 'p939', 'p590', 'p590a', 'p590b', 'p946']
    for y in range(2025, 1994, -1):
        for nm in names:
            f, code = fetch.get('https://www.irs.gov/pub/irs-prior/%s--%d.pdf' % (nm, y))
            if code in ('403', '429'): log('STOP E', code); sys.exit()
        log('E', y)
    log('E DONE')
if 'D' in stage:
    state_f = H + '/wd/full_state.json'
    st = json.load(open(state_f)) if os.path.exists(state_f) else {}
    def num(scheme, y, w, n): return ('%02d%02d%03d' % (y % 100, w, n)) if scheme == 7 else ('%d%02d%03d' % (y, w, n))
    for y in range(1996, 2027):
        for w in range(1, 54):
            key = '%d-%02d' % (y, w)
            if key in st: continue
            found = []
            for scheme in (7, 9):
                if (scheme == 9 and y < 2010) or (scheme == 7 and y > 2016): continue
                miss = 0; n = 0
                while miss < 6 and n < 400:
                    n += 1
                    f, code = fetch.get('https://www.irs.gov/pub/irs-wd/%s.pdf' % num(scheme, y, w, n))
                    if code in ('403', '429'):
                        log('STOP wd', code, y, w, n); sys.exit()
                    if f: found.append(num(scheme, y, w, n)); miss = 0
                    else: miss += 1
            st[key] = found
            json.dump(st, open(state_f + '.tmp', 'w')); os.replace(state_f + '.tmp', state_f)
            log('WD', key, len(found))
    log('D DONE')
