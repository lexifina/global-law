"""AFR rulings 1984-1988 in the Cumulative Bulletins (older layout: no 'Applicable Federal Rates (AFR) for <Month>' table
title). Table blocks are found by 'Period for Compounding' in the -layout text; the ruling number is the nearest
'Rev. Rul. 8X-NN' above; the month comes from that ruling's prose in the reading-order text ('for the month of ...').
Appends to afr/afr_cb.json (months already parsed by cb_afr2.py are kept)."""
import re, os, glob, json, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
exec(open(H + '/afr/cb_afr2.py').read().split('out = []')[0])   # MON, PCT, imports
src = open(H + '/afr/cb_afr2.py').read(); nsrc = src[src.index('def norm'): src.index('for f in sorted')]
rep = collections.Counter(); exec(nsrc)
out = json.load(open(H + '/afr/afr_cb.json')); seen = {(r['year'], r['month']) for r in out}; add = 0
TERM = [('short', r's\s*h\s*o\s*r\s*t\s*-?\s*t\s*e\s*r\s*m'), ('mid', r'm\s*i\s*d\s*-?\s*t\s*e\s*r\s*m'), ('long', r'l\s*o\s*n\s*g\s*-?\s*t\s*e\s*r\s*m')]
for f in sorted(glob.glob(H + '/src/govinfo/text/198[4-8]_*.txt')):
    yv = int(os.path.basename(f)[:4]); raw = open(H + '/src/govinfo/raw/' + os.path.basename(f), errors='replace').read() if os.path.exists(H + '/src/govinfo/raw/' + os.path.basename(f)) else ''
    rawj = re.sub(r'-\s*\n\s*', '', raw); rawj = re.sub(r'\s+', ' ', rawj)
    L = norm(open(f, errors='replace').read()).splitlines()
    for i, l in enumerate(L):
        if 'Period for Compounding' not in l: continue
        rows, lab, term, gap = [], [], None, 0
        for l2 in L[i + 1: i + 40]:
            lo = l2.lower(); hit = False
            for t, rx in TERM:
                if re.search(rx, lo): term = t; hit = True
            v = re.findall(PCT, l2)
            if len(v) == 4:
                pm = re.match(r'\s*([1lI][0-9lIO]{2})\s*(?:%|070|o/o)', l2)
                rows.append(v); lab.append((term, int(pm.group(1).replace('l', '1').replace('I', '1').replace('O', '0')) if pm else 100)); gap = 0
            elif not hit and l2.strip() and not re.search(r'Annual|Semi|AFR\s*$', l2):
                gap += 1
                if rows and gap > 1: break
        if len(rows) < 9 or not any(p == 110 for _, p in lab): continue
        above = '\n'.join(L[max(0, i - 120): i])
        rr = re.findall(r'Rev\.\s*Rul\.\s*(8\d)\s*[-–]\s*(\d+)', above)
        if not rr: rep['no_ruling'] += 1; continue
        num = '%s-%s' % rr[-1]
        m = re.search(r'Rev\. Rul\. ' + num + r'\b.{0,1500}?for the month of ([A-Za-z]+),? (19\d\d)', rawj)
        if not m or m.group(1).lower() not in MON: rep['no_month'] += 1; continue
        yr, mo = int(m.group(2)), MON.index(m.group(1).lower()) + 1
        if (yr, mo) in seen: rep['dup'] += 1; continue
        seen.add((yr, mo)); add += 1
        out.append(dict(file=os.path.relpath(f, H), item='Rev. Rul. ' + num, bulletin='C.B. %d' % yv, source='govinfo', published=str(yv), year=yr, month=mo,
                        table1=rows, labels=lab, table2=[], adj_lt=None, lt_exempt=None, lihtc70=None, lihtc30=None, r7520=None, deemed=None, t7702=None))
json.dump(out, open(H + '/afr/afr_cb.json', 'w'), indent=0)
print('added', add, dict(rep), 'total', len(out), dict(collections.Counter(r['year'] for r in out)))
