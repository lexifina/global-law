"""Bounded novel search (VZ 2025, DeTax exe). N1: 1-euro wage scans for net-income drops / marginal rates > 100 %.
N2: random couples, joint vs separate (> 2 € beyond the tariff bound of FINDINGS S3). N3: per-child vs all-together.
N4: 1-euro dividend scans for pensioners (§ 32d (6) x § 24a x Soli x KiSt). Output: runs/novel_*.json."""
import json, random, sys, itertools
from multiprocessing import Pool
import de
from de import A, H, run, burden, net

def scan(args):
    kind, prof, lo, hi = args
    hs = []
    for w in range(lo, hi + 1):
        if kind == 'married':
            p, kids, age2, kist = prof
            h = H([A(wages=p), A(age=age2, wages=w)], married=True, kids=kids)
        elif kind == 'single':
            kids, age, kist = prof
            h = H([A(age=age, wages=w)], kids=kids)
        elif kind == 'div':
            pen, married, kist, age = prof
            ad = [A(age=age, pension=pen)] + ([A(age=age, pension=pen)] if married else [])
            h = H(ad, married=married, dividends=w)
        hs.append(h)
    fl = [f'--kist={prof[-2] if kind == "div" else prof[-1]}'] if (prof[-2] if kind == 'div' else prof[-1]) else []
    rs = run(hs, *fl)
    ns = [net(h, r) for h, r in zip(hs, rs)]
    drops = []
    for i in range(1, len(ns)):
        d = ns[i] - ns[i - 1]
        if d < 0: drops.append((lo + i, round(d, 2)))
    # worst 100-euro window
    worst = min(((ns[i + 100] - ns[i]) / 100, lo + i) for i in range(0, len(ns) - 100, 25))
    return dict(kind=kind, prof=prof, drops=drops, worst100=(round(1 - worst[0], 4), worst[1]))

def n1():
    jobs = []
    for p, kids, age2, kist in itertools.product([0, 20000, 45000, 70000, 100000, 150000, 300000], [(), (5,), (5, 8), (3, 5, 8)], [40, 66], [0, 900]):
        for lo in range(0, 40000, 10000):
            jobs.append(('married', (p, kids, age2, kist), lo, lo + 10000))
    for kids, age, kist in itertools.product([(), (5,), (5, 8), (3, 5, 8)], [40, 66, 68], [0, 900]):
        for lo in range(0, 300000, 20000):
            jobs.append(('single', (kids, age, kist), lo, lo + 20000))
    for pen, married, kist, age in itertools.product(range(4000, 48001, 4000), [False, True], [0, 900], [70]):
        for lo in range(0, 60000, 20000):
            jobs.append(('div', (pen, married, kist, age), lo, lo + 20000))
    with Pool(16) as pool: res = pool.map(scan, jobs)
    json.dump(res, open('runs/novel_n1.json', 'w'))
    tot = sum(len(r['drops']) for r in res)
    print('N1 jobs', len(jobs), 'drops', tot)
    # summarise drops by (kind, size bucket)
    big = sorted((d for r in res for d in [(x[1], r['kind'], r['prof'], x[0]) for x in r['drops']]), key=lambda t: t[0])
    for t in big[:25]: print(' drop', t)
    small = [t for t in big if t[0] > -1]
    print(' drops of less than 1 €:', len(small), 'e.g.', small[:5])
    wr = sorted(((r['worst100'][0], r['kind'], r['prof'], r['worst100'][1]) for r in res), reverse=True)[:15]
    for t in wr: print(' worst100', t)

def couple(rng):
    kids = tuple(rng.randint(0, 24) for _ in range(rng.choice([0, 0, 1, 2, 3])))
    def adult():
        age = rng.choice([30, 40, 50, 60, 66, 70, 75])
        w = rng.choice([0, 0, rng.randint(0, 6672), rng.randint(6673, 30000), rng.randint(30000, 150000), rng.randint(150000, 400000)])
        pen = rng.randint(5000, 35000) if age >= 66 and rng.random() < .8 else 0
        se = rng.randint(0, 120000) if rng.random() < .15 else 0
        return A(age=age, wages=w, se=se, pension=pen)
    return H([adult(), adult()], married=True, kids=kids,
             interest=rng.choice([0, rng.randint(0, 20000)]), dividends=rng.choice([0, 0, rng.randint(0, 60000)]),
             capitalGains=rng.choice([0, 0, rng.randint(0, 50000)]), rentalIncome=rng.choice([0, 0, rng.randint(-20000, 40000)]),
             charitable=rng.choice([0, 0, rng.randint(0, 5000)]), pensionContributions=rng.choice([0, 0, rng.randint(0, 20000)]))

def n2_chunk(seed):
    rng = random.Random(seed); hs = [couple(rng) for _ in range(5000)]
    out = []
    for kist in (0, 900):
        fl = [f'--kist={kist}'] if kist else []
        j = run(hs, *fl); s = run(hs, *fl, '--separate'); a = run(hs, *fl, '--all-children-together')
        for h, rj, rs, ra in zip(hs, j, s, a):
            dj = burden(rj) - burden(rs); dc = burden(rj) - burden(ra)
            if dj > 2 or dc > 0.5: out.append(dict(h=h, kist=kist, joint_minus_sep=round(dj, 2), perchild_minus_all=round(dc, 2),
                                                 tax_j=rj['incomeTax'], tax_s=rs['incomeTax'], soli_j=rj['surtaxes'], soli_s=rs['surtaxes'],
                                                 ks_j=rj['benefits'], ks_s=rs['benefits']))
    return out

def n2():
    with Pool(16) as pool: res = pool.map(n2_chunk, range(64))
    out = [x for r in res for x in r]
    json.dump(out, open('runs/novel_n2.json', 'w'))
    print('N2 couples', 64 * 5000, 'x2 kist; joint worse than separate by >2 €:', sum(1 for x in out if x['joint_minus_sep'] > 2),
          '; per-child worse than all-together:', sum(1 for x in out if x['perchild_minus_all'] > 0.5))
    for x in sorted(out, key=lambda x: -x['joint_minus_sep'])[:8]:
        print(' ', x['joint_minus_sep'], x['perchild_minus_all'], x['kist'], json.dumps({k: v for k, v in x['h'].items() if k not in ('id', 'year')}))

if __name__ == '__main__':
    if 'n1' in sys.argv: n1()
    if 'n2' in sys.argv: n2()
