"""Checks on harvested written determinations (irs-wd) and Chief Counsel documents (irs-ccdm, irs-utl, lanoa, irs-lafa, irs-aod):
text layer or scanned; kind; year; amounts stated for indexed or fixed statutory items compared with the statute and the
revenue procedures (indexing/published.json); citations to sections already repealed when the document was issued."""
import os, re, glob, json, subprocess, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); U = os.path.expanduser(os.environ.get('USC_HISTORY', '~/united-states-law'))
pub = json.load(open(H + '/indexing/published.json'))
have = {os.path.basename(f)[:-3] for f in glob.glob(U + '/title-26/*.md')}
dele = {}
def deleted(s):
    if s not in dele:
        dele[s] = subprocess.run(['git', '-C', U, 'log', '-1', '--diff-filter=D', '--format=%ad', '--date=short', '--', 'title-26/%s.md' % s], capture_output=True, text=True).stdout.strip()
    return dele[s]
TXT = H + '/wd/text'; os.makedirs(TXT, exist_ok=True)
docs = sorted(glob.glob(H + '/cache/www.irs.gov/pub/irs-wd/*.pdf')) + sorted(glob.glob(H + '/cache/www.irs.gov/pub/irs-ccdm/*.pdf')) + \
       sorted(glob.glob(H + '/cache/www.irs.gov/pub/irs-utl/*.pdf')) + sorted(glob.glob(H + '/cache/www.irs.gov/pub/lanoa/*.pdf')) + \
       sorted(glob.glob(H + '/cache/www.irs.gov/pub/irs-lafa/*.pdf')) + sorted(glob.glob(H + '/cache/www.irs.gov/pub/irs-aod/*.pdf'))
ITEMS = {'gift_excl': r'(?:2503\(b\)|annual exclusion)', 'basic_excl': r'basic exclusion amount', 'feie': r'911\(b\)\(2\)\(D\)|foreign earned income exclusion', 's6601j': r'6601\(j\)'}
FIXED = [(r'section 121\(b\)\(1\)|§ ?121\(b\)\(1\)', {250000}), (r'section 121\(b\)\(2\)|§ ?121\(b\)\(2\)', {500000})]
res = collections.Counter(); amount_checks = []; cite_after = []; per = {}
for f in docs:
    d = f.split('/pub/')[1]; base = os.path.basename(f)[:-4]
    out = TXT + '/' + d.replace('/', '__') + '.txt'
    if not os.path.exists(out):
        open(out, 'w').write(subprocess.run(['nice', '-n', '10', 'pdftotext', '-layout', f, '-'], capture_output=True, text=True, errors='replace').stdout)
    t = open(out, errors='replace').read()
    words = len(t.split())
    if words < 50: res['scanned'] += 1; per[d] = 'scanned'; continue
    res['text'] += 1
    m = re.search(r'Release Date:\s*(\d{1,2})/(\d{1,2})/(\d{4})', t)
    if m: year = int(m.group(3)); date = '%s-%02d-%02d' % (m.group(3), int(m.group(1)), int(m.group(2)))
    else:
        dig = re.sub(r'\D', '', base)
        year = int(dig[:4]) if len(dig) >= 8 and dig[:2] in ('19', '20') else (2000 + int(dig[:2]) if dig[:2] < '50' else 1900 + int(dig[:2])) if len(dig) >= 6 else None
        date = '%d-12-31' % year if year else None
    head = t[:4000]
    kind = 'TAM' if re.search(r'(?i)technical advice memorandum', head) else 'FSA' if re.search(r'(?i)field service advice', head) else \
           'CCA' if re.search(r'(?i)office of chief counsel', head) and not re.search(r'Dear ', head) else 'PLR' if re.search(r'Dear |This letter responds|This is in reply|This is in response', t[:8000]) else 'other'
    res['kind_' + d.split('/')[0] + '_' + kind] += 1
    per[d] = dict(kind=kind, year=year, words=words)
    flat = ' '.join(t.split())
    for k, rx in ITEMS.items():
        for mm in re.finditer('(?:' + rx + ')' + r'[^.$]{0,160}?\$([\d,]{4,})[^.]{0,80}?\b(19\d\d|20\d\d)\b', flat):
            amt = int(mm.group(1).replace(',', '')); yy = mm.group(2)
            if yy in pub and k in pub[yy]:
                want = pub[yy][k]['v'][0]
                amount_checks.append((d, k, yy, amt, want, amt == want, flat[mm.start(): mm.end()][:200]))
    for rx, ok in FIXED:
        for mm in re.finditer('(?:' + rx + ')' + r'[^.$]{0,120}?\$([\d,]{6,})', flat):
            amt = int(mm.group(1).replace(',', ''))
            amount_checks.append((d, rx[:24], '', amt, sorted(ok), amt in ok, flat[mm.start(): mm.end()][:200]))
    if date:
        for mm in re.finditer(r'(?:§§? ?|\b[Ss]ection )(\d{1,4}[A-Z]{0,2})(?=\(|\s|,|\.(?!\d))', flat):
            s = mm.group(1)
            if s in have: continue
            pre = flat[max(0, mm.start() - 50): mm.start()]; post = flat[mm.end(): mm.end() + 50]
            if re.search(r'(?i)former|repeal|U\.S\.C|1939|1954', pre + post) or re.match(r'\s+of\s+(?!the (Internal Revenue )?Code)', post): continue
            dd = deleted(s)
            if dd and dd < date: cite_after.append((d, date, s, dd, flat[max(0, mm.start() - 100): mm.end() + 80]))
res['amount_checks'] = len(amount_checks); res['amount_mismatch'] = sum(1 for a in amount_checks if not a[5]); res['cites_after_repeal'] = len(cite_after)
json.dump(dict(summary=res, amounts=amount_checks, cites_after_repeal=cite_after, docs=per), open(H + '/wd/checks.json', 'w'), indent=1)
print(dict(res))
for a in amount_checks:
    if not a[5]: print('AMT', a)
