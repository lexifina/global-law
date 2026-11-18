"""Helpers: run the DeTax exe (read-only, ~/cmp/de) and exact § 32a / SolZG arithmetic for post-processing steps."""
import os
import json, subprocess
from fractions import Fraction as F
D = os.path.expanduser('~/cmp/de/lean/.lake/build/bin/detax')

def A(age=40, wages=0, se=0, pension=0):
    return dict(age=age, wages=wages, selfEmployment=se, pension=pension)

def H(adults, married=False, kids=(), **kw):
    h = dict(id='x', year=2025, adults=list(adults), married=married, children=[{'age': c} for c in kids],
             interest=0, dividends=0, capitalGains=0, rentalIncome=0, charitable=0, pensionContributions=0)
    h.update(kw); return h

def run(hs, *flags):
    inp = ''.join(json.dumps(h) + '\n' for h in hs)
    out = subprocess.run([D, *flags], input=inp, capture_output=True, text=True, check=True).stdout.splitlines()
    return [json.loads(l) for l in out]

def run1(h, *flags): return run([h], *flags)[0]

def burden(r):  # income tax + Soli + KiSt + employee contributions - Kindergeld kept
    return round(r['incomeTax'] + sum(r['surtaxes'].values()) + r['employeeSocial'] - r['benefits'], 2)

def gross(h):
    return sum(a['wages'] + a['selfEmployment'] + a['pension'] for a in h['adults']) + h['interest'] + \
        h['dividends'] + h['capitalGains'] + h['rentalIncome']

def net(h, r): return round(gross(h) - burden(r), 2)

def pap(re4_month_eur, stkl, zkf=0, pvz=0):
    j = dict(LZZ=2, RE4=int(round(re4_month_eur * 100)), STKL=stkl, ZKF=zkf, KRV=0, KVZ=2.5, PKV=0, PVS=0, PVZ=pvz,
             R=0, ALTER1=0, AJAHR=0, LZZFREIB=0, LZZHINZU=0)
    o = subprocess.run([D, '--pap'], input=json.dumps(j) + '\n', capture_output=True, text=True, check=True).stdout
    o = json.loads(o); return o['LSTLZZ'] / 100, o['SOLZLZZ'] / 100

# § 32a (1) EStG 2025 / 2026, exact integer form (units 1e-10 euro), as DeTax.Tariff
T = {2025: dict(gfb=12096, e2=17443, e3=68480, e4=277825, a2=93230, b2=1400, a3=17664, b3=2397, c3=101513, r4=42, c4=1091192, r5=45, c5=1924667),
     2026: dict(gfb=12348, e2=17799, e3=69878, e4=277825, a2=91451, b2=1400, a3=17310, b3=2397, c3=103487, r4=42, c4=1113563, r5=45, c5=1947038)}
def num(x, y=2025):
    t = T[y]
    if x <= t['gfb']: return 0
    if x <= t['e2']: d = x - t['gfb']; return (t['a2'] * d + t['b2'] * 10**6) * d
    if x <= t['e3']: d = x - t['e2']; return (t['a3'] * d + t['b3'] * 10**6) * d + t['c3'] * 10**8
    if x <= t['e4']: return (t['r4'] * x - t['c4']) * 10**8
    return (t['r5'] * x - t['c5']) * 10**8
def est(x, y=2025): return num(int(x // 1), y) // 10**10          # zvE rounded down first (Satz 1)
def split(x, y=2025): return 2 * est(int(x // 1) // 2, y)            # § 32a (5)

def soli(base, joint=False, abg=0.0):
    """SolZG § 3 (3), § 4: Freigrenze 19 950 / 39 900, Milderung 11,9 %; 5,5 % on Abgeltungsteuer; cents down."""
    fg = 39900 if joint else 19950
    s = F(0) if base <= fg else min(F(55, 1000) * base, F(119, 1000) * (base - fg))
    s += F(55, 1000) * F(str(abg))
    return float(int(s * 100) / F(100))
