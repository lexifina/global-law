"""Scan household income I0 (before the sec. 162(l) deduction for specified premiums) and classify the
consistent (deduction, credit) pairs; compare with the Rev. Proc. 2014-41 / Pub. 974 methods.
Uses fp.py (statute model). Illustrative premiums (not sourced): benchmark Bm per scenario."""
import sys, json, math
import numpy as np
sys.path.insert(0, '.')
import fp

def vec_credit(year, h, P, Q, Bm, mode, aptc):
    pct = 100.0 * h / P
    if mode == 'form':
        pct = np.floor(pct)
    tab = fp.T2025 if year == 2025 else fp.T2026
    a = np.full_like(pct, (8.5 if year == 2025 else 9.96) / 100.0)
    for lo, hi, a0, a1 in tab:
        m = (pct >= lo) & (pct < hi)
        a = np.where(m, (a0 + (a1 - a0) * (pct - lo) / (hi - lo)) / 100.0, a)
    if mode == 'form':
        a = np.round(a, 4)
        contrib = np.round(h * a)
    else:
        contrib = h * a
    C = np.minimum(Q, np.maximum(0.0, Bm - contrib))
    ok = (pct >= 100) | (aptc > 0)
    if year == 2026:
        ok &= pct <= 400
    return np.where(ok, C, 0.0)

def scan_one(year, I0, P, Q, Bm, L, mode='exact', aptc=0.0, single=True, tol=1.0):
    top = int(min(Q, L))
    d = np.arange(0, top + 1, dtype=float)
    h = I0 - d
    C = vec_credit(year, h, P, Q, Bm, mode, aptc)
    cap = Q - C
    if aptc > 0 and year == 2025:
        pct = 100.0 * h / P
        lim = np.full_like(pct, np.inf)
        for b, s, o in reversed(fp.LIM2025):
            lim = np.where(pct < b, s if single else o, lim)
        cap = np.minimum(cap, Q - aptc + np.minimum(np.maximum(aptc - C, 0), lim))
    gd = np.maximum(0.0, np.minimum(L, cap))
    F = d - gd
    good = np.abs(F) <= tol
    sols = []
    idx = np.nonzero(good)[0]
    if idx.size:
        groups = np.split(idx, np.nonzero(np.diff(idx) > 1)[0] + 1)
        for gp in groups:
            k = gp[len(gp) // 2]
            sols.append((float(d[k]), float(C[k])))
    return sols

def fed_tax_2026_single(ti):
    br = [(12400, .10), (50400, .12), (105700, .22), (201775, .24), (256225, .32), (640600, .35), (1e18, .37)]
    t, lo = 0.0, 0.0
    for hi, r in br:
        if ti > lo:
            t += (min(ti, hi) - lo) * r
        lo = hi
    return t

def run(name, year, n, Bm, Q, L, lo_pct, hi_pct, step, mode='exact', aptc=0.0, single=True):
    P = fp.pov(year, n)
    rows = []
    I0 = lo_pct * P / 100
    while I0 <= hi_pct * P / 100:
        I = round(I0)
        sols = scan_one(year, I, P, Q, Bm, L, mode, aptc, single)
        it = fp.iterative(year, I, P, Q, Bm, L, mode, aptc, single)
        sm = fp.simplified(year, I, P, Q, Bm, L, mode, aptc, single)
        rows.append(dict(I0=I, pct=round(100 * I / P, 2), n_sol=len(sols), sols=sols, it=it, simp=sm))
        I0 += step
    # summarise bands
    bands, cur = [], None
    for r in rows:
        k = (r['n_sol'], r['it'][0])
        if cur is None or cur['key'] != k:
            cur = dict(key=k, start=r['I0'], end=r['I0'], ex=r)
            bands.append(cur)
        cur['end'] = r['I0']
    print(f"\n== {name}: year {year}, family {n}, P={P}, Bm={Bm}, Q={Q}, L={L}, mode={mode}, aptc={aptc}")
    for b in bands:
        r = b['ex']
        print(f"  I0 {b['start']:>7}-{b['end']:>7} ({100*b['start']/P:6.1f}%-{100*b['end']/P:6.1f}%): "
              f"consistent answers={b['key'][0]} {[(round(x),round(y)) for x,y in r['sols']]} | iterative={r['it'][0]} "
              f"(d={r['it'][1]:.0f},C={r['it'][2]:.0f}) | simplified={r['simp'][0]} (d={r['simp'][1]:.0f},C={r['simp'][2]:.0f})")
    return rows, bands

if __name__ == '__main__':
    out = {}
    L = 10**9
    # S1: single, 2026, benchmark plan, two ages (illustrative benchmarks)
    for Bm in (7500, 14000):
        out[f'2026_single_B{Bm}_cliff'] = run(f'2026 single cliff Bm={Bm}', 2026, 1, Bm, Bm, L, 370, 460, 10)[1]
        out[f'2026_single_B{Bm}_floor'] = run(f'2026 single floor Bm={Bm}', 2026, 1, Bm, Bm, L, 90, 180, 10)[1]
        out[f'2025_single_B{Bm}_floor'] = run(f'2025 single floor Bm={Bm}', 2025, 1, Bm, Bm, L, 90, 180, 10)[1]
        out[f'2025_single_B{Bm}_cliff'] = run(f'2025 single 400% Bm={Bm}', 2025, 1, Bm, Bm, L, 370, 460, 10)[1]
    # couple 60, 2026
    run('2026 couple cliff Bm=28000', 2026, 2, 28000, 28000, L, 370, 520, 20)
    run('2026 couple floor Bm=28000', 2026, 2, 28000, 28000, L, 90, 250, 20)
    # bronze plan cheaper than benchmark
    run('2026 single floor bronze Q=5000 Bm=7500', 2026, 1, 7500, 5000, L, 90, 140, 10)
    # form rounding: fraction of I0 where iterative fails in a sloped tier
    for year in (2025, 2026):
        P = fp.pov(year, 1)
        tot = fail = nos = 0
        for I in range(int(1.6 * P), int(3.9 * P), 7):
            it = fp.iterative(year, I, P, 14000, 14000, L, 'form')
            s = scan_one(year, I, P, 14000, 14000, L, 'form')
            tot += 1; fail += it[0] != 'converged'; nos += len(s) == 0
        print(f"\n{year} form-rounded schedule, single Bm=Q=14000, I0 160%-390% FPL step $7: iterative fails {fail}/{tot}, no consistent answer {nos}/{tot}")
    # 2025 with APTC and the repayment limitation
    run('2025 single 400% Bm=14000 APTC=9000', 2025, 1, 14000, 14000, L, 370, 470, 10, aptc=9000)
    run('2025 single 100% Bm=7500 APTC=6000', 2025, 1, 7500, 7500, L, 90, 160, 10, aptc=6000)
