"""AFR rulings in the Cumulative Bulletins 1984-1995 (scanned volumes with an OCR text layer, pdftotext -layout).
Anchors on the table headers, not the prose (the prose runs in 3 interleaved columns). OCR number artifacts are
normalised only in the forms '9. 11%' / '6, 25%' (a digit, '.' or ',', one space, two digits, '%'); every such repair is
counted. Output: afr/afr_cb.json in the afr.json layout (table1 rows, table2, adj_lt, lt_exempt, lihtc70, lihtc30)."""
import re, os, glob, json, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
MON = ['january','february','march','april','may','june','july','august','september','october','november','december']
PCT = r'(\d{1,2}\.\d{2})\s*%'
out = []; seen = set(); rep = collections.Counter()
def norm(s):
    s, n = re.subn(r"(\d\.\s?\d{2}) ?(?:070|o/o|'7o|c/c|ci)(?=\s)", r'%', s); rep['pct_sign_repaired'] += n
    s, n = re.subn(r'(?<=\s)(\d{1,2}) (\d{2})%', r'.%', s); rep['point_repaired'] += n
    s2, n = re.subn(r'(\d)\s?[.,]\s(\d{2})\s*%', r'\1.\2%', s); rep['repaired'] += n
    s2, n = re.subn(r'(\d),(\d{2})\s*%', r'\1.\2%', s2); rep['repaired'] += n
    return s2
for f in sorted(glob.glob(H + '/src/govinfo/text/[12][90][09]*_*.txt')):
    yv = int(os.path.basename(f)[:4])
    if not 1996 <= yv <= 2008: continue
    t = open(f, errors='replace').read()
    for m in re.finditer(r'Applicable\s+Federal\s+Rates\s*\(AFR\)\s+for\s+([A-Za-z]+)\s*,?\s+(\d{4})', t):
        mon = m.group(1).lower()
        if mon not in MON: rep['bad_month'] += 1; continue
        yr, mo = int(m.group(2)), MON.index(mon) + 1
        if (yr, mo) in seen: rep['dup'] += 1; continue
        body = norm(t[m.end(): m.end() + 9000])
        nxt = re.search(r'Applicable\s+Federal\s+Rates\s*\(AFR\)\s+for', body)
        if nxt: body = body[:nxt.start()]
        adj = re.search(r'Adjusted\s+A[FP]R\s+(?:for\s+)?[A-Z]', body)
        tA = body[:adj.start()] if adj else body; tB = body[adj.start():] if adj else ''
        rows = lambda s: [r for r in (re.findall(PCT, l) for l in s.splitlines()) if len(r) == 4]
        lab = []; term = None
        for l in tA.splitlines():
            lo = l.lower()
            if re.search(r's\s*h\s*o\s*r\s*t\s*-?\s*t\s*e\s*r\s*m', lo): term = 'short'
            elif re.search(r'm\s*i\s*d\s*-?\s*t\s*e\s*r\s*m', lo): term = 'mid'
            elif re.search(r'l\s*o\s*n\s*g\s*-?\s*t\s*e\s*r\s*m', lo): term = 'long'
            v = re.findall(PCT, l)
            if len(v) == 4:
                pm = re.match(r'\s*([1lI][0-9lIO]{2})\s*(?:%|070|o/o)', l); lab.append((term, int(pm.group(1).replace('l', '1').replace('I', '1').replace('O', '0')) if pm else 100))
        t1 = rows(tA); t2 = rows(tB.split('TABLE')[0] if tB else '')[:3]
        def after(s, phrase):
            i = re.search(phrase, s, re.I | re.S)
            if not i: return None
            rest = s[i.end():]; nl = rest.find(chr(10)); line = rest[:nl if nl >= 0 else 400]
            if not re.search(r'\d', line):   # value on the next line (wrapped label)
                nl2 = rest.find(chr(10), nl + 1); line = rest[nl: nl2 if nl2 > 0 else nl + 400]
            mm = re.search(r'(\d{1,2}\.\d{2})\s*(?:%|ci|c/c|c;|\Z|$)', line.strip()); return mm.group(1) if mm else None
        rr = re.findall(r'REV\.\s*RUL\.\s*(\d{2})\s*[-–]\s*(\d+)', t[max(0, m.start() - 400): m.start()])
        item = 'Rev. Rul. %s-%s' % rr[-1] if rr else 'CB %d (%s %d)' % (yv, mon.capitalize(), yr)
        out.append(dict(file=os.path.relpath(f, H), item=item, bulletin='C.B. %d' % yv, source='govinfo', published=str(yv), year=yr, month=mo,
                        table1=t1, labels=lab, table2=t2, adj_lt=after(tB, r'Adjusted\s+federal\s+long-term\s+rate\s+for\s+the\s+current\s+month'),
                        lt_exempt=after(tB, r'prior\s+two\s+months\)'), lihtc70=after(tB, r'70%\s+present\s+value\s+low-income\s+housing\s+credit'),
                        lihtc30=after(tB, r'30%\s+present\s+value\s+low-income\s+housing\s+credit'), r7520=None, deemed=None, t7702=None))
        seen.add((yr, mo))
json.dump(out, open(H + '/afr/afr_cb_late.json', 'w'), indent=0)
print(len(out), 'rulings', dict(rep), 'table1 rows', collections.Counter(len(r['table1']) for r in out), 'table2', collections.Counter(len(r['table2']) for r in out))
print('months by year', dict(collections.Counter(r['year'] for r in out)))
print('missing fields', {k: sum(1 for r in out if r[k] is None) for k in ('adj_lt', 'lt_exempt', 'lihtc70', 'lihtc30')})
