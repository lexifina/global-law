"""Monthly AFR revenue rulings printed in the Cumulative Bulletins 1984-1995 -> afr/afr_cb.json (same layout as afr.json)."""
import re, os, glob, json, sys
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
sys.argv = ['x']; exec(open(H + '/afr/parse_afr.py').read().split('out = []; fails = []')[0])   # reuse P, SEP, TUP, NUM, first_after
MONTHS = ['january','february','march','april','may','june','july','august','september','october','november','december']
out = []; seen = set()
for f in sorted(glob.glob(H + '/src/govinfo/text/19[89]*_*.txt')):
    yv = int(os.path.basename(f)[:4])
    if not 1984 <= yv <= 1995: continue
    t = open(f, errors='replace').read()
    starts = [m for m in re.finditer(r'prescribed rates for federal income tax purposes for\s+(\w+)\s*,?\s*(\d{4})', t, re.I)]
    for i, m in enumerate(starts):
        if m.group(1).lower() not in MONTHS: continue
        yr, mo = int(m.group(2)), MONTHS.index(m.group(1).lower()) + 1
        if (yr, mo) in seen: continue
        body = t[m.start(): starts[i + 1].start() if i + 1 < len(starts) else m.start() + 15000][:15000]
        adj = re.search(r'Adjusted AFR for', body)
        tA = body[:adj.start()] if adj else body; tB = body[adj.start():] if adj else ''
        t1 = [tuple(x) for x in TUP.findall(tA)]; t2 = [tuple(x) for x in TUP.findall(tB)][:3]
        rr = re.search(r'Rev\. ?Rul\. (\d{2})[-–](\d+)', t[max(0, m.start() - 3000): m.start()][::-1][::-1])
        item = 'CB %d (%s %d)' % (yv, m.group(1).capitalize(), yr)
        out.append(dict(file=os.path.relpath(f, H), item=item, bulletin='C.B. %d' % yv, source='govinfo', published=str(yv), year=yr, month=mo,
                        table1=t1, table2=t2,
                        adj_lt=first_after(tB, 'Adjusted federal long-term rate for the current month'),
                        lt_exempt=first_after(tB, 'prior two months', label='Long-term tax-exempt rate'),
                        lihtc70=first_after(tB, '70% present value low-income housing credit'),
                        lihtc30=first_after(tB, '30% present value low-income housing credit'),
                        r7520=first_after(tB, 'reversionary interest', NUM), deemed=first_after(tB, 'less than 3 taxable years', NUM), t7702=None))
        seen.add((yr, mo))
json.dump(out, open(H + '/afr/afr_cb.json', 'w'), indent=0)
from collections import Counter
print(len(out), 'rulings', Counter(len(r['table1']) for r in out), sorted({r['year'] for r in out}))
