#!/usr/bin/env python3
"""HMRC tax-kalculator 2.16.1 vs the Lean UK model (statute) and the Lean PAYE routine, 2025-26.

Runs three engines on one grid and classifies every difference:
  * kalc   : scripts/kalc (tax-kalculator's public Calculator API on the JVM)
  * uktax  : ~/cmp/uk/lean/.lake/build/bin/uktax (ITA 2007 s. 23 liability, Class 1 NI, annual earnings period)
  * payegrid: lean/.lake/build/bin/payegrid (HMRC PAYE tax table routine, 12 equal monthly payments)
A small exact-arithmetic model of the kalculator's documented conventions (`conv`) explains each difference;
the same model with the statute's settings must reproduce uktax (checks the replica, not the law).

Outputs: results/kalc_*.jsonl (one row per case) and results/kalc_summary.txt.
"""
import json, math, subprocess, sys, os
from fractions import Fraction as F
from collections import Counter, defaultdict

BASE = os.path.expanduser('~/cmp/official/uk-hmrc')
UKTAX = os.path.expanduser('~/cmp/uk/lean/.lake/build/bin/uktax')
PAYEGRID = BASE + '/lean/.lake/build/bin/payegrid'
KALC = BASE + '/scripts/kalc'
OUT = BASE + '/results'
os.makedirs(OUT, exist_ok=True)

RUK = [(37700, F(20, 100)), (87440, F(40, 100)), (None, F(45, 100))]
SCOT = [(2827, F(19, 100)), (12094, F(20, 100)), (16171, F(21, 100)), (31338, F(42, 100)), (62710, F(45, 100)),
        (None, F(48, 100))]


def band_tax(taxable, bands):
    t, rem = F(0), F(taxable)
    for width, rate in bands:
        if rem <= 0:
            break
        x = rem if width is None else min(rem, width)
        t += x * rate
        rem -= x
    return t


def conv(w, scot, extra9, round_taper, taper=True, pa=12570):
    """Annual tax on employment income w (pounds, Fraction) with tax-free amount pa (+9 if extra9),
    tapered above £100,000 (ITA s. 35(2)); round_taper: allowance rounded up to £1 (s. 35(3))."""
    w = F(w)
    a = F(pa + (9 if extra9 else 0))
    if taper and w > 100000:
        t = (w - 100000) / 2
        if round_taper:
            a = max(F(0), F(math.ceil(F(pa) - t)))      # statute: PA (12,570) reduced, rounded up
        else:
            a = max(F(0), a - min(t, a))                # kalculator: 12,579 - min(t, 12,579)
    return band_tax(max(F(0), w - a), SCOT if scot else RUK)


def ni(w):
    w = F(w)
    return max(F(0), min(w, 50270) - 12570) * F(8, 100) + max(F(0), w - 50270) * F(2, 100)


def floor_p(x):
    return F(math.floor(x * 100), 100)


def run_kalc(rows):
    inp = '\n'.join(r['kin'] for r in rows) + '\n'
    out = subprocess.run([KALC], input=inp, capture_output=True, text=True, check=True).stdout.splitlines()
    assert len(out) == len(rows), (len(out), len(rows))
    for r, o in zip(rows, out):
        r['k'] = json.loads(o)


def run_uktax(rows):
    lines = []
    for r in rows:
        h = {"id": r['id'], "year": 2025, "adults": [{"age": r['age'], "wages": r['lw'], "selfEmployment": 0,
             "pension": 0}], "married": False, "children": [], "interest": 0, "dividends": 0, "capitalGains": 0,
             "rentalIncome": 0, "charitable": 0, "pensionContributions": 0}
        if r['scot']:
            h['region'] = 'scotland'
        lines.append(json.dumps(h))
    out = subprocess.run([UKTAX], input='\n'.join(lines) + '\n', capture_output=True, text=True, check=True)
    outl = out.stdout.splitlines()
    assert len(outl) == len(rows)
    for r, o in zip(rows, outl):
        j = json.loads(o)
        r['lean'] = {'tax': F(str(j['detail']['liabilityITA2007s23'])), 'ni': F(str(j['employeeSocial']))}


def run_paye(rows):
    inp = '\n'.join(r['pin'] for r in rows) + '\n'
    out = subprocess.run([PAYEGRID], input=inp, capture_output=True, text=True, check=True).stdout.splitlines()
    assert len(out) == len(rows)
    for r, o in zip(rows, out):
        _, tot, cap = o.split(';')
        r['paye'] = {'tax': F(int(tot), 100), 'capped': int(cap)}


EDGES = [12570, 12579, 15397, 27491, 43662, 50270, 50279, 60000, 75000, 80000, 100000, 100002, 100018, 125140,
         125158, 150000]


def wage_grid(step=25, top=200000):
    ws = set(range(0, top + 1, step))
    for e in EDGES:
        for d in (-10, -9, -2, -1, 0, 1, 2, 9, 10):
            if e + d >= 0:
                ws.add(e + d)
    return sorted(ws)


def k(v):
    return F(str(v))


def main():
    cases = []
    # A. statute comparison: default code (1257L, not supplied -> tapering), rUK and Scotland, age 40 and 70
    for scot in (0, 1):
        for w in wage_grid():
            cases.append(dict(set='A-default', scot=scot, age=40, w=w, lw=w, code='1257L', supplied=0, period='YEARLY',
                              kw=w, pa=0, pm='-', pv=0))
        for w in range(0, 200001, 1000):
            cases.append(dict(set='A-pensionage', scot=scot, age=70, w=w, lw=w, code='1257L', supplied=0,
                              period='YEARLY', kw=w, pa=1, pm='-', pv=0))
            # user-supplied 1257L above £100k: documented "no tapering"
            cases.append(dict(set='A-supplied', scot=scot, age=40, w=w, lw=w, code='1257L', supplied=1,
                              period='YEARLY', kw=w, pa=0, pm='-', pv=0))
            # 1257T: tax-free amount 10 x code, no £9
            cases.append(dict(set='A-Tcode', scot=scot, age=40, w=w, lw=w, code='1257T', supplied=1,
                              period='YEARLY', kw=w, pa=0, pm='-', pv=0))
    # B. pay periods: integer monthly and weekly wages
    for m in range(0, 16701, 25):
        cases.append(dict(set='B-monthly', scot=0, age=40, w=12 * m, lw=12 * m, code='1257L', supplied=0,
                          period='MONTHLY', kw=m, pa=0, pm='-', pv=0))
    for wk in range(0, 3851, 5):
        cases.append(dict(set='B-weekly', scot=0, age=40, w=52 * wk, lw=52 * wk, code='1257L', supplied=0,
                          period='WEEKLY', kw=wk, pa=0, pm='-', pv=0))
    # C. pension contributions (net pay arrangement: income tax on w - C, NI on w)
    for scot in (0, 1):
        for w in range(0, 200001, 500):
            c = w // 20  # 5 %
            cases.append(dict(set='C-pension5pc', scot=scot, age=40, w=w, lw=w - c, nw=w, code='1257L', supplied=0,
                              period='YEARLY', kw=w, pa=0, pm='PERCENTAGE', pv=5.0, C=c))
            if w >= 2400:
                cases.append(dict(set='C-pension200pm', scot=scot, age=40, w=w, lw=w - 2400, nw=w, code='1257L',
                                  supplied=0, period='YEARLY', kw=w, pa=0, pm='MONTHLY_AMOUNT_IN_POUNDS', pv=200.0,
                                  C=2400))
    for i, c in enumerate(cases):
        c['id'] = f"{c['set']}-{i}"
        c['kin'] = f"{c['id']};{c['code']};{c['scot']};{c['supplied']};{c['kw']};{c['period']};{c['pa']};{c['pm']};{c['pv']};2025"
    run_kalc(cases)
    run_uktax(cases)
    # NI for pension cases: Lean NI on gross wage (net pay arrangement does not reduce NICs)
    ni_rows = [dict(c, lw=c['nw'], id=c['id'] + 'ni') for c in cases if 'nw' in c]
    run_uktax(ni_rows)
    nimap = {r['id'][:-2]: r['lean']['ni'] for r in ni_rows}

    # D. tax codes vs Lean PAYE (12 equal monthly payments, cumulative)
    codes = [('1257L', 0, '1257'), ('1257T', 0, '1257'), ('0T', 0, '0'), ('1383M', 0, '1383'), ('1131N', 0, '1131'),
             ('K475', 0, 'K475'), ('K100', 0, 'K100'), ('K2000', 0, 'K2000'), ('BR', 0, 'BR'), ('D0', 0, 'D0'),
             ('D1', 0, 'D1'), ('NT', 0, 'NT'), ('1257L M1', 0, '1257'), ('C1257L', 0, '1257'), ('CBR', 0, 'BR'),
             ('CD0', 0, 'D0'), ('CD1', 0, 'D1'), ('CK475', 0, 'K475'), ('S1257L', 1, '1257'), ('S1257T', 1, '1257'),
             ('S0T', 1, '0'), ('SBR', 1, 'BR'), ('SD0', 1, 'D0'), ('SD1', 1, 'D1'), ('SD2', 1, 'D2'), ('SD3', 1, 'D3'),
             ('SK475', 1, 'K475')]
    prow = []
    for code, scot, pcode in codes:
        for m in range(0, 16001, 250):
            r = dict(set='D-codes', code=code, scot=scot, m=m, w=12 * m)
            r['id'] = f"D-{code.replace(' ', '')}-{m}"
            r['kin'] = f"{r['id']};{code};{scot};1;{m};MONTHLY;0;-;0;2025"
            r['pin'] = f"{r['id']};12;{pcode};{scot};{m * 100}"
            prow.append(r)
    run_kalc(prow)
    run_paye(prow)

    # ---- classify ----
    summ = defaultdict(Counter)
    maxd = defaultdict(F)
    unexplained = []
    rows_out = []
    for c in cases:
        kj = c['k']
        if not kj['ok']:
            summ[c['set']]['kalc-error'] += 1
            unexplained.append((c['id'], 'kalc error', kj['error']))
            continue
        y = kj['yearly']
        ktax, kraw, kni = k(y['tax']), k(y['taxRaw']), k(y['ee'])
        lt = c['lean']['tax']
        lni = nimap.get(c['id'], c['lean']['ni'])
        w = c['w']
        lw = c['lw']
        scot = bool(c['scot'])
        # replica checks: statute settings must reproduce Lean exactly (to the penny, liability floored)
        stat = floor_p(conv(lw, scot, extra9=False, round_taper=True))
        if stat != lt:
            unexplained.append((c['id'], 'replica!=lean', float(stat), float(lt)))
        if c['age'] >= 66:
            pred_ni = F(0)
        else:
            pred_ni = ni(c.get('nw', w))
        if c['pa'] == 1:
            kpred_ni = F(0)
        else:
            kpred_ni = ni(c['kw'] * {'YEARLY': 1, 'MONTHLY': 12, 'WEEKLY': 52}[c['period']])
        # kalculator conventions
        if c['code'] == '1257T':
            kpred = conv(lw, scot, extra9=False, round_taper=False, taper=False)
        else:
            kpred = conv(lw, scot, extra9=True, round_taper=False, taper=(c['supplied'] == 0))
        explained = abs(kraw - kpred) < F(1, 10 ** 6)
        dtax = ktax - lt
        dni = kni - lni
        if dtax == 0:
            cls = 'equal'
        elif explained:
            if c['code'] == '1257T':
                cls = '(c) other'
            elif c['supplied'] == 1 and lw > 100000:
                cls = '(c) no taper for a user-supplied code (README) + £9'
            else:
                # which convention: +£9 alone, or unrounded taper as well
                only9 = conv(lw, scot, extra9=True, round_taper=True) if False else None
                cls = '(c) PAYE free pay £9 (code x 10 + 9)' + (' + unrounded taper' if lw > 100000 else '')
            if abs(dtax) <= F(1, 100) and cls != 'equal':
                cls = '(c) penny rounding'
        else:
            cls = 'UNEXPLAINED'
            unexplained.append((c['id'], 'tax', float(ktax), float(lt), float(kpred)))
        if abs(dni) > F(1, 100):
            if abs(kni - kpred_ni) <= F(1, 100) and c['pa'] == 1 and c['age'] < 66:
                summ[c['set']]['ni (c)'] += 1
            else:
                summ[c['set']]['ni-diff'] += 1
                unexplained.append((c['id'], 'ni', float(kni), float(lni)))
        else:
            summ[c['set']]['ni-equal'] += 1
        summ[c['set']][cls] += 1
        maxd[(c['set'], cls)] = max(maxd[(c['set'], cls)], abs(dtax))
        rows_out.append(dict(id=c['id'], set=c['set'], scot=c['scot'], age=c['age'], w=w, code=c['code'],
                             supplied=c['supplied'], period=c['period'], kalcTax=float(ktax), leanTax=float(lt),
                             kalcNI=float(kni), leanNI=float(lni), dTax=float(dtax), dNI=float(dni), cls=cls,
                             kalcTaxFree=y['taxFree'], kalcTaxable=y['taxable']))
    # codes vs PAYE
    for r in prow:
        kj = r['k']
        if not kj['ok']:
            summ['D-codes:' + r['code']]['kalc-error'] += 1
            continue
        kt = k(kj['yearly']['tax'])
        pt = r['paye']['tax']
        d = kt - pt
        key = 'D-codes:' + r['code']
        if abs(d) <= F(1, 100):
            cls = 'equal (1p)'
        elif abs(d) <= F(1):
            cls = '<= £1 (PAYE period rounding)'
        else:
            cls = 'diff > £1'
        summ[key][cls] += 1
        maxd[(key, 'd')] = max(maxd[(key, 'd')], abs(d))
        maxd[(key, 'signed_max')] = max(maxd[(key, 'signed_max')], d)
        maxd[(key, 'signed_min')] = min(maxd.get((key, 'signed_min'), F(0)), d)
        rows_out.append(dict(id=r['id'], set='D-codes', code=r['code'], m=r['m'], kalcTax=float(kt),
                             payeTax=float(pt), d=float(d), taxFree=kj['yearly']['taxFree'], cls=cls))

    with open(OUT + '/kalc_rows.jsonl', 'w') as f:
        for r in rows_out:
            f.write(json.dumps(r) + '\n')
    with open(OUT + '/kalc_summary.txt', 'w') as f:
        f.write(f'cases (statute grid): {len(cases)}; code cases vs PAYE: {len(prow)}\n')
        for s in sorted(summ):
            f.write(f'{s}: ' + ', '.join(f'{k_}={v}' for k_, v in sorted(summ[s].items())) + '\n')
        f.write('\nmax |difference| by set/class:\n')
        for key_, v in sorted(maxd.items(), key=lambda x: str(x[0])):
            f.write(f'  {key_}: {float(v):.2f}\n')
        f.write(f'\nunexplained ({len(unexplained)}):\n')
        for u in unexplained[:200]:
            f.write('  ' + repr(u) + '\n')
    print(open(OUT + '/kalc_summary.txt').read()[:6000])


if __name__ == '__main__':
    main()
