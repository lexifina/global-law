"""Parse the monthly applicable-federal-rate revenue rulings (IRB 1996-2026) into afr.json."""
import re, os, json, glob, sys
G = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/irs-guidance')
MONTHS = ['january','february','march','april','may','june','july','august','september','october','november','december']
P = r'(\d{0,2}\.\d{1,3})\s*%'
SEP = r'[\s|]*'
TUP = re.compile(P + SEP + P + SEP + P + SEP + P)
def front(t):
    m = re.search(r'^item: "([^"]+)"', t, re.M); b = re.search(r'^bulletin: "([^"]+)"', t, re.M)
    s = re.search(r'^source: "([^"]+)"', t, re.M); p = re.search(r'^published: "([^"]+)"', t, re.M)
    return m.group(1), b.group(1), s.group(1), p.group(1)
NUM = r'(\d{0,2}\.\d{1,3}|\d{1,2}(?=\s*%))(?:\s*%)?'
STOPS = re.compile(r'TABLE|Appropriate|REV\. RUL|Rate Under|Deemed Rate|Section 42|Average of', re.I)
def first_after(t, phrase, pat=NUM, span=600, label=None):
    i = t.lower().find(phrase.lower())
    if i < 0: return None
    seg = t[i+len(phrase): i+len(phrase)+span]
    st = STOPS.search(seg)
    if st: seg = seg[:st.start()]
    m = re.search(pat, seg)
    if m: return m.group(1)
    if label:
        j = t.lower().find(label.lower())
        if j > 0:
            ms = re.findall(pat, t[max(0, j-30):j])
            if ms: return ms[-1]
    return None
out = []; fails = []
for f in sorted(glob.glob(G + '/rev-rul/*/*.md')):
    t = open(f, encoding='utf-8').read()
    if not re.search(r'prescribed rates for federal income tax purposes', t, re.I): continue
    item, bull, src, pub = front(t)
    m = re.search(r'prescribed rates for federal income tax purposes for\s+(\w+)\s*,?\s*(\d{4})', t, re.I)
    if not m or m.group(1).lower() not in MONTHS:
        fails.append((f, 'month')); continue
    mon = MONTHS.index(m.group(1).lower()) + 1; yr = int(m.group(2))
    body = t
    # cut at the cross-reference section ("Section 42.--" lines) to avoid stray matches
    cut = re.search(r'\n(Section|§)\s*42\.?\s*[—–-]', body)
    if cut: body = body[:cut.start()]
    adj = re.search(r'Adjusted AFR for', body)
    tA = body[:adj.start()] if adj else body
    tB = body[adj.start():] if adj else ''
    t1 = [tuple(x) for x in TUP.findall(tA)]
    t2 = [tuple(x) for x in TUP.findall(tB)][:3]
    rec = dict(file=os.path.relpath(f, G), item=item, bulletin=bull, source=src, published=pub, year=yr, month=mon,
               table1=t1, table2=t2,
               adj_lt=first_after(tB, 'Adjusted federal long-term rate for the current month'),
               lt_exempt=first_after(tB, 'prior two months', label='Long-term tax-exempt rate'),
               lihtc70=first_after(tB, '70% present value low-income housing credit'),
               lihtc30=first_after(tB, '30% present value low-income housing credit'),
               r7520=first_after(tB, 'reversionary interest', NUM),
               deemed=first_after(tB, 'less than 3 taxable years', NUM),
               t7702=None)
    m7 = re.search(r'60-month period ending ([A-Za-z]+ \d+, \d{4}), is (\d+\.\d+)%, rounded to (\d+)%', body)
    if m7: rec['t7702'] = [m7.group(1), m7.group(2), m7.group(3)]
    out.append(rec)
json.dump(out, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/afr/afr.json'), 'w'), indent=0)
from collections import Counter
print(len(out), 'rulings;', 'fails', len(fails), fails[:5])
print('table1 tuple counts', Counter(len(r['table1']) for r in out))
print('table2 counts', Counter(len(r['table2']) for r in out))
for k in ('adj_lt','lt_exempt','lihtc70','lihtc30','r7520','deemed','t7702'):
    print(k, sum(1 for r in out if r[k]))
ym = Counter((r['year'], r['month']) for r in out)
dups = [k for k,v in ym.items() if v>1]; print('dup months', dups)
allm = {(y,m) for y in range(1996,2027) for m in range(1,13)}
print('missing months', sorted(allm - set(ym))[:40], len(allm-set(ym)))
