"""Prototype of HMRC's PAYE tax table routines (Specification v24, method unchanged) against the 2025-26 test data."""
import json, re, math
RUK = dict(B=[37700, 87440], R=[2000, 4000, 4500], G=1)
SCOT = dict(B=[2827, 12094, 16171, 31338, 62710], R=[1900, 2000, 2100, 4200, 4500, 4800], G=2)
M = 5000
def freepay_pence(n, P):
    if n == 0: return 0
    q, r = (n - 1) // 500, (n - 1) % 500 + 1
    part = -((-(10 * r + 9) * 100) // P)          # ceil to the penny
    return part + q * (9616 if P == 52 else 41667)
def tax_to_date(U, nper, P, reg):           # U in u (1/10000 pound), returns pence
    if U <= 0: return 0
    C = [sum(reg['B'][:i + 1]) for i in range(len(reg['B']))]
    K = [sum(reg['B'][j] * reg['R'][j] for j in range(i + 1)) for i in range(len(reg['B']))]
    c = [C[i] * 10000 * nper // P for i in range(len(C))]
    k = [K[i] * nper // P for i in range(len(K))]
    v = [-((-c[i]) // 10000) for i in range(len(c))]
    j = next((i for i in range(len(c)) if U <= v[i] * 10000), len(c))
    T = U // 10000
    c0 = c[j - 1] if j > 0 else 0; k0 = k[j - 1] if j > 0 else 0
    L = k0 + (T * 10000 - c0) * reg['R'][j] // 10000
    return L // 100
def run_sheet(sheet):
    P = 12 if 'mthly' in sheet['rows'][0]['label'].lower() or 'monthly' in sheet['rows'][0]['label'].lower() else 52
    cum, Lprev, res, last = 0, 0, [], 0
    for r in sheet['rows']:
        if r['period'] <= last: cum, Lprev = 0, 0          # a new employee
        last = r['period']
        code = r['code']; reg = RUK
        if code.startswith('S'): reg = SCOT; code = code[1:]
        elif code.startswith('C'): code = code[1:]
        w1 = r['w1m1'] == 'WM1'
        cum += r['pay']
        Pn = r['pay'] if w1 else cum
        nper = 1 if w1 else r['period']
        if code == 'NT': L = 0
        elif code == 'BR': L = (Pn // 100) * reg['R'][reg['G'] - 1] // 100
        elif re.fullmatch(r'D\d', code): L = (Pn // 100) * reg['R'][reg['G'] - 1 + 1 + int(code[1])] // 100
        elif code.startswith('K'):
            e1 = freepay_pence(int(code[1:]), P)
            L = tax_to_date((Pn + nper * e1) * 100, nper, P, reg)
        else:
            n = int(re.match(r'\d+', code).group())
            L = tax_to_date((Pn - nper * freepay_pence(n, P)) * 100, nper, P, reg)
        prev = 0 if w1 else Lprev
        due = L - prev
        limit = r['pay'] * M // 10000
        if due > limit: due = limit; L = prev + limit
        if not w1: Lprev = L
        res.append((due, L if not w1 else due))
    return res
ok = bad = 0
for l in open('/home/lean/cmp/uk/runs/hmrc_paye_sheets.jsonl'):
    s = json.loads(l)
    for r, (due, todate) in zip(s['rows'], run_sheet(s)):
        if due == r['due'] and todate == r['todate']: ok += 1
        elif abs(due - r['due']) <= 1 and abs(todate - r['todate']) <= 1: bad += 1; print('1p', s['file'][:12], s['sheet'], r['code'], r['period'])
        else:
            bad += 1; print('MISMATCH', s['file'][:12], s['sheet'], r['code'], r['period'], r['pay'], 'exp', r['due'], r['todate'], 'got', due, todate)
print('rows ok', ok, 'bad', bad)
