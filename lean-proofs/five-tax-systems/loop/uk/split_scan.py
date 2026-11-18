"""Novel search, part B: splitting a married couple's investment income, gains, rental property and Gift Aid
between the spouses (outright transfers: TCGA 1992 s. 58 no gain/no loss; ITA 2007 s. 836-837 for joint
property). For each random couple: every allocation on a 5-level grid (interest, dividends, gains, property:
0/25/50/75/100 % to spouse 1) x who makes the Gift Aid; best vs the contract's equal split, vs all with the
higher earner, vs all with the lower earner. Plus one crafted household optimised on a 21-level grid.
usage: python3 split_scan.py N SEED OUT.json"""
import os
import json, random, sys, itertools, subprocess
from multiprocessing import Pool
sys.path.insert(0, os.path.expanduser('~/cmp/loop/uk'))
from ukrun import EXE, burden

TH = [0, 0, 5000, 12570, 17570, 30000, 50270, 60000, 70000, 80000, 100000, 125140, 150000]
LV = [0, 0.25, 0.5, 0.75, 1]

def runexe(hs):
    inp = '\n'.join(json.dumps(x) for x in hs) + '\n'
    out = subprocess.run([EXE], input=inp, capture_output=True, text=True, check=True).stdout
    return [json.loads(l) for l in out.splitlines() if l.strip()]

def couple(r):
    w = lambda: max(0, r.choice(TH) + r.randint(-2000, 2000))
    c = dict(w1=w(), w2=w(), I=r.choice([0, r.randint(0, 10000), r.randint(0, 40000)]),
             D=r.choice([0, r.randint(0, 5000), r.randint(0, 60000)]), G=r.choice([0, r.randint(0, 10000), r.randint(0, 80000)]),
             R=r.choice([0, 0, r.randint(0, 40000)]), GA=r.choice([0, 0, r.randint(0, 10000)]),
             k=r.choice([0, 0, 1, 2, 3]), scot=r.random() < 0.2)
    c['F'] = int(c['R'] * r.random() * 0.6) if r.random() < 0.5 else 0
    return c

def build(c, a, gaBy1, id):
    fi, fd, fg, fr = a
    s = lambda x, f: int(round(x * f))
    p1 = dict(employment=c['w1'], interest=s(c['I'], fi), dividends=s(c['D'], fd), gains=s(c['G'], fg),
              property=s(c['R'], fr), financeCosts=s(c['F'], fr), giftAid=c['GA'] if gaBy1 else 0)
    p2 = dict(employment=c['w2'], interest=c['I'] - p1['interest'], dividends=c['D'] - p1['dividends'],
              gains=c['G'] - p1['gains'], property=c['R'] - p1['property'], financeCosts=c['F'] - p1['financeCosts'],
              giftAid=0 if gaBy1 else c['GA'])
    h = dict(id=id, year=2025, married=True, children=[{'age': 5}] * c['k'], persons=[p1, p2])
    if c['scot']: h['region'] = 'scotland'
    return h

def evaluate(c, levels):
    allocs = [(a, g) for a in itertools.product(levels, repeat=4) for g in (True, False)]
    outs = runexe([build(c, a, g, str(i)) for i, (a, g) in enumerate(allocs)])
    bs = [burden(o) for o in outs]
    best = min(range(len(bs)), key=lambda i: bs[i])
    hi1 = c['w1'] >= c['w2']
    def find(a, g): return bs[allocs.index((a, g))]
    eq = min(find((0.5,) * 4, True), find((0.5,) * 4, False))
    allhi = find(((1,) if hi1 else (0,)) * 4, hi1)
    alllo = find(((0,) if hi1 else (1,)) * 4, not hi1)
    return dict(c=c, best=bs[best], alloc=allocs[best][0], gaBy1=allocs[best][1], equal=eq, allHigher=allhi,
                allLower=alllo, interior=any(0 < x < 1 for x in allocs[best][0]),
                electionBest=outs[best]['detail']['election'])

def work(args):
    seed, n = args
    r = random.Random(seed)
    return [evaluate(couple(r), LV) for _ in range(n)]

if __name__ == '__main__':
    n, seed, outp = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    res = []
    with Pool(24) as pool:
        for rs in pool.imap_unordered(work, [(seed * 1000 + i, 10) for i in range(n // 10)]):
            res.extend(rs)
    crafted = dict(w1=110000, w2=0, I=18000, D=10000, G=40000, R=0, F=0, GA=0, k=2, scot=False)
    cr = evaluate(crafted, [i / 20 for i in range(21)][::2] + [0.05, 0.15])  # 12 levels per item
    json.dump(dict(couples=res, crafted=cr), open(outp, 'w'))
    gain_eq = sorted(x['equal'] - x['best'] for x in res)
    gain_hi = sorted(x['allHigher'] - x['best'] for x in res)
    print('couples', len(res))
    for name, g in (('vs equal split', gain_eq), ('vs all with higher earner', gain_hi)):
        print(name, 'median', g[len(g) // 2], 'p90', g[int(len(g) * .9)], 'max', g[-1], 'share >£100', sum(x > 100 for x in g) / len(g))
    print('best interior share', sum(x['interior'] for x in res) / len(res))
    print('worst-case equal split', max(res, key=lambda x: x['equal'] - x['best']))
    print('crafted', cr)
