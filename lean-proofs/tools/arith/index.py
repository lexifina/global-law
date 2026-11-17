"""Recompute every item of spec.ITEMS from the statutory formula and compare with the published amount.

COLA (Â§1(f)(3)) for calendar year Y and base year B, with C(y) = 12-month sum of C-CPI-U Sep(y-1)..Aug(y) and
P(y) = the same for CPI-U:
    B >= 2016:  ratio = C(Y-1) / C(B)                         (Â§1(f)(3)(A) with (B), or (C) for B > 2016)
    B <  2016:  ratio = C(Y-1) * P(2016) / (P(B) * C(2016))  (Â§1(f)(3)(A)(ii) x (B))
increase = base * (ratio - 1), then rounded as the item says.
Vintages: 'v' = C-CPI-U values as of the release of August (Y-1) (Â§1(f)(6)(A)); 'f' = latest (BLS, 2026-11-16).
Output: out/index.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cpi import vintage, bls, ysum
from spec import ITEMS
import spec_old  # noqa: F401  (appends item 6 to ITEMS)

P = bls('CUUR0000SA0'); CF = bls('SUUR0000SA0')

from cpi import med_vintage
PM = bls('CUUR0000SAM'); MF = bls('SUUR0000SAM')

def ratio(by, cy, vint):
    if by == 'med':   # §213(d)(10)(B)(ii): medical C-CPI-U Aug(cy-1) vs medical CPI Aug 1996 x §1(f)(3)(B)
        C = vintage(cy - 1) if vint == 'v' else CF
        M = med_vintage(cy - 1) if vint == 'v' else MF
        return M[(cy - 1, 8)] * ysum(P, 2016), PM[(1996, 8)] * ysum(C, 2016)
    C = vintage(cy - 1) if vint == 'v' else CF
    if by >= 2016:
        return ysum(C, cy - 1), ysum(C, by)
    return ysum(C, cy - 1) * ysum(P, 2016), ysum(P, by) * ysum(C, 2016)

def fdiv(a, b): return a // b
def rnd_near(n, d, m):  # nearest multiple of m to n/d, ties up
    return m * ((2 * n + m * d) // (2 * m * d))

def adjust(base, by, cy, rnd, vint='v'):
    kind = rnd[0]
    if kind == 'fixed': return base
    if isinstance(base, list):   # several statutory amounts added before one rounding (e.g. §32(b)(2)(A)+(B))
        tot_n, tot_d = 0, 1
        for b, y in base:
            num, den = ratio(y, cy, vint); tot_n, tot_d = tot_n * den + b * num * tot_d, tot_d * den
        assert kind == 'amt_near'
        return rnd_near(tot_n, tot_d, rnd[1])
    num, den = ratio(by, cy, vint)
    inc_n, inc_d = base * (num - den), den          # exact increase = inc_n / inc_d
    if kind == 'inc_down': return base + rnd[1] * (inc_n // (inc_d * rnd[1]))
    if kind == 'inc_near': return base + rnd_near(inc_n, inc_d, rnd[1])
    amt_n = base * num                                # exact amount = amt_n / den
    if kind == 'amt_down': return rnd[1] * (amt_n // (den * rnd[1]))
    if kind == 'amt_near': return rnd_near(amt_n, den, rnd[1])
    if kind == 'none': return amt_n // den
    if kind == 'pen':
        thr, big, small = rnd[1:]
        if amt_n >= thr * den: return big * (amt_n // (den * big))
        return small * (amt_n // (den * small))
    raise ValueError(kind)

def exact(base, by, cy, vint='v'):
    if by is None: return float(base)
    if isinstance(base, list): return sum(b * ratio(y, cy, vint)[0] / ratio(y, cy, vint)[1] for b, y in base)
    num, den = ratio(by, cy, vint); return base * num / den

if __name__ == '__main__':
    out = []
    for it in ITEMS:
        r = dict(it)
        try:
            r['comp'] = adjust(it['base'], it['by'], it['cy'], it['rnd'])
        except (KeyError, ValueError):
            r['comp'] = None   # index values missing (October 2025 C-CPI-U was never published)
        if r['comp'] is None:
            r['comp_final'] = None; r['exact'] = float('nan')
            r['comp_prev'] = adjust(it['base'], it['by'], it['cy'] - 1, it['rnd']); out.append(r); continue
        r['comp'] = adjust(it['base'], it['by'], it['cy'], it['rnd'])
        r['comp_final'] = adjust(it['base'], it['by'], it['cy'], it['rnd'], 'f') if it['by'] else r['comp']
        r['exact'] = exact(it['base'], it['by'], it['cy'])
        if it['id'].startswith(('p6', )) and it['by']:
            r['comp_prev'] = adjust(it['base'], it['by'], it['cy'] - 1, it['rnd'])
        out.append(r)
    for r in out:
        st = None
        if r['comp'] is None: st = 'not computable'
        elif r['pub'] is None: st = 'intermediate'
        elif r['comp'] == r['pub']: st = 'match'
        elif r['rnd'][0] == 'none':
            ex = r['exact']
            st = 'rounding' if any(abs(r['pub'] - ex) <= u / 2 and r['pub'] % u == 0 for u in (1, 10, 100, 1000)) else 'mismatch'
        else: st = 'mismatch'
        r['status'] = st
        if 'comp_prev' in r:
            import gen_lean
            r['alt'] = dict(tag='lag', val=r['comp_prev'], expr=gen_lean.comp_expr(r, cy=r['cy'] - 1),
                            why=f"IRS reading: COLA for {r['cy'] - 1} (the year before the filing year)")
    os.makedirs(os.path.join(os.path.dirname(__file__), 'out'), exist_ok=True)
    json.dump(out, open(os.path.join(os.path.dirname(__file__), 'out', 'index.json'), 'w'), indent=1)
    for r in out:
        flag = r['status']
        extra = f" final={r['comp_final']}" if r['comp_final'] != r['comp'] else ''
        if 'comp_prev' in r: extra += f" cola(cy-1)={r['comp_prev']}"
        if flag != 'match' or '-v' in sys.argv:
            print(f"{r['doc']} {r['sec']:8} {r['id']:20} base={r['base']} by={r['by']} cy={r['cy']} {r['rnd']} exact={r['exact']:.2f} comp={r['comp']} pub={r['pub']} {flag}{extra}")
    print(len(out), 'items;', sum(1 for r in out if r['pub'] is not None and r['comp'] == r['pub']), 'match')
