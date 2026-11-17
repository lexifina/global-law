"""26 CFR annual editions 1997-2016 (GovInfo bulk XML, src/cfr_annual/<year>/): every printed Table S (single-life
remainder factors, Life Tables 80CNSMT / 90CM / 2000CM) recomputed from the life table printed in the same edition:
R = (1 + i/2) * sum_t v^(t+1) (l_{x+t} - l_{x+t+1}) / l_x, five decimals (the convention that reproduces the
Reg. 20.2031-7(d) examples; cfr/table_s_hist.py). -> cfr/annual_table_s.json"""
import os, re, glob, json, collections
import xml.etree.ElementTree as ET
from decimal import Decimal as D, getcontext, ROUND_HALF_UP
getcontext().prec = 40
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
def txt(e): return ''.join(e.itertext()).strip()
def basis(title):
    for b in ('2000CM', '90CM', '80CNSMT'):
        if b in title.replace(' ', ''): return b
res = collections.Counter(); off = []; perys = collections.Counter()
for yd in sorted(glob.glob(H + '/src/cfr_annual/*')):
    y = os.path.basename(yd); life = {}; stabs = []
    for f in sorted(glob.glob(yd + '/*.xml')):
        if 'Table S' not in open(f, errors='replace').read(): continue
        title = ''
        for ev, e in ET.iterparse(f, events=('end',)):
            if e.tag == 'TTITLE': title = txt(e); continue
            if e.tag != 'GPOTABLE': continue
            tt = e.find('TTITLE'); t = txt(tt) if tt is not None else title
            if tt is not None: title = t
            heads = [txt(c) for c in e.iter('CHED')]
            rows = [[txt(x) for x in r.findall('ENT')] for r in e.iter('ROW')]
            b = basis(title)
            if b and re.match(r'(Life )?Table\s*(80CNSMT|90CM|2000CM)', ' '.join(title.split())) and heads and heads[0].lower().startswith('age'):
                cand = {}
                for r in rows:
                    for k in range(0, len(r) - 1, 2):
                        a, l = r[k].replace(',', ''), r[k + 1].replace(',', '')
                        if a.isdigit() and re.fullmatch(r'[\d.]+', l): cand[int(a)] = D(l)
                ks = sorted(cand)
                if len(ks) >= 100 and all(cand[ks[j]] >= cand[ks[j + 1]] for j in range(len(ks) - 1)) and b not in life: life[b] = cand
                elif cand: res['life_rejected_' + b] += 1
            elif b and 'Table S' in title and heads and heads[0].lower().startswith('age'):
                rates = [D(h.rstrip('%').strip()) / 100 for h in heads[1:] if re.fullmatch(r'[\d.]+ ?%?', h.strip())]
                stabs.append((b, title[:60], rates, rows))
            e.clear()
    for b, title, rates, rows in stabs:
        lx = life.get(b)
        if not lx or len(lx) < 100: res['no_life_' + b] += 1; continue
        mx = max(lx)
        for r in rows:
            if not r or not r[0].isdigit(): continue
            x = int(r[0])
            if x not in lx: continue
            if len(r) - 1 != len(rates): res['row_width_mismatch'] += 1; continue
            for i, v in zip(rates, r[1:]):
                if i is None or not re.fullmatch(r'\.?\d*\.\d+', v): continue
                s = D(0); vv = D(1); disc = 1 / (1 + i)
                for t in range(0, mx - x + 1):
                    vv *= disc; s += vv * (lx.get(x + t, D(0)) - lx.get(x + t + 1, D(0)))
                R = (s / lx[x] * (1 + i / 2)).quantize(D('0.00001'), rounding=ROUND_HALF_UP)
                res['cells'] += 1; perys[y + ' ' + b] += 1
                if R != D(v): res['off'] += 1; off.append((y, b, str(i), x, v, str(R)))
    print(y, dict(perys), dict(res), flush=True)
json.dump(dict(summary=res, per_edition=perys, off=off[:500]), open(H + '/cfr/annual_table_s.json', 'w'), indent=0)
print(off[:20])
