"""The IRS actuarial tables (pub/irs-tege, Version 4 2010CM and Version 3 2000CM) recomputed from the life
table (Reg. 20.2031-7(d)(7) 2010CM from cfr/actuarial.json; 2000CM from table-2000cm.xls) with 50-digit decimals:
Table S (remainder A_x = sum v^(t+1) d_(x+t)/l_x, life estate 1-A_x, annuity (1-A_x)/i), Table U(1) (unitrust remainder,
discount 1-k), Table B (term certain: v^n, 1-v^n, (1-v^n)/i). Printed vs recomputed at the printed decimals.
-> cfr/tege_check.json; mismatches listed for review."""
import os, sys, re, json, collections, glob
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/pylib'))
import openpyxl, xlrd
from decimal import Decimal as D, getcontext, ROUND_HALF_UP
getcontext().prec = 50
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); T = H + '/cache/www.irs.gov/pub/irs-tege/'
def rnd(x, nd): return x.quantize(D(1).scaleb(-nd), rounding=ROUND_HALF_UP)
def decs(v):
    s = repr(v) if isinstance(v, float) else str(v); return len(s.split('.')[1]) if '.' in s else 0
lx10 = {int(k): D(str(v)) for k, v in json.load(open(H + '/cfr/actuarial.json'))['title-26-part-0020/sec-2031-0007.md']['lx'].items()}
def lx_from_xls(f):
    wb = xlrd.open_workbook(f); lx = {}
    for sh in wb.sheets():
        for r in range(sh.nrows):
            row = sh.row_values(r)
            for c in range(len(row) - 1):
                a, b = row[c], row[c + 1]
                if isinstance(a, float) and a == int(a) and 0 <= a <= 110 and isinstance(b, float) and b >= 0 and (int(a) not in lx) and (b > 1000 or a > 95): lx[int(a)] = D(str(b))
    return lx
lx00 = lx_from_xls(T + 'table-2000cm.xls') if os.path.exists(T + 'table-2000cm.xls') else {}
def remainder(lx, x, disc):
    s = D(0); lxx = lx[x]; v = D(1)
    for t in range(0, 111 - x):
        v *= disc
        d = lx.get(x + t, D(0)) - lx.get(x + t + 1, D(0))
        s += v * d
    return s / lxx
res = collections.Counter(); bad = []
ND = {'_rem': 5, '_life': 5, '_ann': 4, 'U1': 5, 'B_ann': 4, 'B_inc': 6, 'B_rem': 6, 'B_final_ann': 4, 'B_final_inc': 6, 'B_final_rem': 6}
def cmp(tag, printed, val, extra):
    if printed is None or printed == '': return
    nd = ND.get(tag) or next(v for k, v in ND.items() if tag.endswith(k) or tag.startswith(k)); p = rnd(D(repr(printed)), nd)
    res[tag + '_n'] += 1
    if rnd(val, nd) != p:
        res[tag + '_off'] += 1; bad.append(dict(table=tag, **extra, printed=str(p), recomputed=str(rnd(val, nd + 2))))
def table_s(f, lx, tag):
    ws = openpyxl.load_workbook(f, read_only=True, data_only=True).worksheets[0]; i = None
    for row in ws.iter_rows(values_only=True):
        txt = ' '.join(str(x) for x in row if x is not None)
        m = re.search(r'Interest at ([\d.]+) Percent', txt)
        if m: i = D(m.group(1)) / 100; continue
        if i is None: continue
        for k in (0, 4):
            seg = row[k: k + 4]
            if len(seg) == 4 and isinstance(seg[0], (int, float)) and seg[1] is not None and isinstance(seg[3], float) and int(seg[0]) in lx:
                x = int(seg[0]); A = remainder(lx, x, 1 / (1 + i)) * (1 + i / 2)   # mid-year adjustment, Reg. 20.2031-7(d)(2)(ii)(B) Figure 2
                cmp(tag + '_rem', seg[3], A, dict(rate=str(i), age=x)); cmp(tag + '_life', seg[2], 1 - A, dict(rate=str(i), age=x)); cmp(tag + '_ann', seg[1], (1 - A) / i, dict(rate=str(i), age=x))
def table_u1(f, lx, tag):
    ws = openpyxl.load_workbook(f, read_only=True, data_only=True).worksheets[0]; rates = None
    for row in ws.iter_rows(values_only=True):
        if row and str(row[0]).strip() == 'Age': rates = [D(str(x).strip('%')) / 100 if x else None for x in row[1:]]; continue
        if rates and row and row[0] is not None and str(row[0]).strip().isdigit() and int(str(row[0]).strip()) in lx:
            x = int(str(row[0]).strip())
            for k, v in zip(rates, row[1:]):
                if k is not None and isinstance(v, float): cmp(tag, v, remainder(lx, x, 1 - k) / (1 - k / 2), dict(rate=str(k), age=x))   # Reg. 1.664-4 mid-year adjustment
def table_b(f, tag):
    ws = openpyxl.load_workbook(f, read_only=True, data_only=True).worksheets[0]; rates = None
    for row in ws.iter_rows(values_only=True):
        if any(isinstance(x, str) and 'Interest Rate' in x for x in row) or (row[0] is None and isinstance(row[4] if len(row) > 4 else None, float)):
            rates = {c: D(str(row[c + 4])) for c in (0, 8) if len(row) > c + 4 and isinstance(row[c + 4], float)}; continue
        if not rates: continue
        for c, i in rates.items():
            seg = row[c: c + 8]
            if len(seg) >= 7 and isinstance(seg[0], (int, float)) and 1 <= seg[0] <= 60 and isinstance(seg[2], float):
                n = int(seg[0]); vn = (1 / (1 + i)) ** n
                cmp(tag + '_ann', seg[2], (1 - vn) / i, dict(rate=str(i), n=n)); cmp(tag + '_inc', seg[4], 1 - vn, dict(rate=str(i), n=n)); cmp(tag + '_rem', seg[6], vn, dict(rate=str(i), n=n))
table_s(T + 'table-s-2010cm-final.xlsx', lx10, 'S_2010CM'); print(dict(res), flush=True)
table_u1(T + 'table-u1-2010cm-final.xlsx', lx10, 'U1_2010CM'); print(dict(res), flush=True)
table_b(T + 'table-b-final.xlsx', 'B_final'); print(dict(res), flush=True)
if len(lx00) > 100 and os.path.exists(T + 'table-s-2000cm.xlsx'): table_s(T + 'table-s-2000cm.xlsx', lx00, 'S_2000CM')
print('lx2000CM ages', len(lx00)); print(dict(res))
json.dump(dict(summary=res, mismatches=bad[:2000]), open(H + '/cfr/tege_check.json', 'w'), indent=0)
for b in bad[:15]: print(b)
