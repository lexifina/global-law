"""Pub 15 (Circular E) 1995-2019, Table 7 (annual percentage method): each row's base amount = previous base + previous
rate x (this row's floor - previous floor) (the tables are prescribed under s3402(a)(1); their internal arithmetic is
checkable, their offsets are a design choice); 2005-2017 offsets also against std deduction - personal exemption."""
import os, re, json, subprocess
from fractions import Fraction as F
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
def money(s): return F(s.replace('$', '').replace(',', ''))
ROW = re.compile(r'\$([\d,]+)\s*[—–-]+\s*\$([\d,]+)\s*(?:\.\s*)+\s*(?:\$([\d,.]+)\s*plus\s*)?([\d.]+)%\s*[—–-]+\s*\$([\d,]+)')
TOP = re.compile(r'\$([\d,]+)\s*(?:\.\s*){3,}\s*\$([\d,.]+)\s*plus\s*([\d.]+)%\s*[—–-]+\s*\$([\d,]+)')
res = {'years': 0, 'tables': 0, 'rows': 0, 'off': []}
for y in range(1995, 2020):
    f = H + '/cache/www.irs.gov/pub/irs-prior/p15--%d.pdf' % y
    if not os.path.exists(f): continue
    t = subprocess.run(['pdftotext', '-layout', f, '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True).stdout
    i = t.find('TABLE 7'); 
    if i < 0: continue
    seg = t[i: i + 6000]; res['years'] += 1
    cols = {}
    for l in seg.splitlines():
        parts = [(m.start(), m) for m in ROW.finditer(l)] + [(m.start(), m) for m in TOP.finditer(l) if not re.search(r'[—–-]\s*$', l[max(0, m.start() - 6): m.start()])]
        for pos, m in sorted(parts, key=lambda p: p[0]):
            c = 0 if pos < 60 else (1 if pos < 120 else 2)
            if m.re is ROW: cols.setdefault(c, []).append((money(m.group(1)), F(m.group(3).replace(',', '')) if m.group(3) else F(0), F(m.group(4)), money(m.group(5))))
            else: cols.setdefault(c, []).append((money(m.group(1)), F(m.group(2).replace(',', '')), F(m.group(3)), money(m.group(4))))
    for c, rows in cols.items():
        dd = []
        for r in rows:
            if not dd or r[0] != dd[-1][0]: dd.append(r)
        rows = dd
        res['tables'] += 1
        for k in range(1, len(rows)):
            lo0, b0, r0, ex0 = rows[k - 1]; lo1, b1, r1, ex1 = rows[k]
            res['rows'] += 1
            want = b0 + r0 / 100 * (lo1 - lo0)
            if b1 != want or ex1 != lo1: res['off'].append((y, c, k, str(lo1), str(b1), str(want), str(ex1)))
print(res['years'], 'years', res['tables'], 'tables', res['rows'], 'row steps', len(res['off']), 'off')
for o in res['off'][:20]: print(o)
json.dump(res, open(H + '/withholding/p15_arith.json', 'w'), indent=0)
