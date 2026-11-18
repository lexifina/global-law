"""Novel search, part A: marginal rates > 100 % (the household's burden rises by more than the extra income) and
contributions that pay for themselves, on random households biased to every threshold, singles and couples, rUK and
Scotland. Each flagged event gets cause tags from the per-person detail lines that jumped.
usage: python3 scan.py N_BASE SEED OUT.jsonl   (writes one line per flagged event; summary to stdout)"""
import os
import json, random, sys, subprocess, copy
from multiprocessing import Pool
sys.path.insert(0, os.path.expanduser('~/cmp/loop/uk'))
from ukrun import EXE, burden

TH = [12570, 17570, 18570, 37700, 43663, 50270, 60000, 60100, 70000, 79900, 80000, 100000, 112570, 125140, 150000]
def amt(r, hi):
    if r.random() < 0.6:
        return max(0, r.choice(TH) + r.randint(-3000, 3000))
    return r.randint(0, hi)

def person(r):
    p = {'age': 40 if r.random() < 0.9 else r.choice([67, 72, 76])}
    if r.random() < 0.8: p['employment'] = amt(r, 200000)
    if r.random() < 0.2: p['trading'] = amt(r, 80000)
    if r.random() < 0.08: p['pension'] = amt(r, 60000)
    if r.random() < 0.4: p['interest'] = r.choice([r.randint(0, 2000), r.randint(0, 20000), r.choice([500, 1000, 5000, 6000])])
    if r.random() < 0.3: p['dividends'] = r.choice([r.randint(0, 3000), r.randint(0, 60000), 500])
    if r.random() < 0.25: p['gains'] = r.choice([r.randint(0, 6000), r.randint(0, 80000), 3000])
    if r.random() < 0.15:
        p['property'] = r.randint(0, 40000)
        if r.random() < 0.5: p['financeCosts'] = r.randint(0, 25000)
    if r.random() < 0.25: p['rasGross'] = r.choice([r.randint(0, 10000), r.randint(0, 40000), 3600])
    if r.random() < 0.15: p['giftAid'] = r.choice([r.randint(0, 2000), r.randint(0, 20000)])
    if r.random() < 0.05: p['vct'] = r.randint(0, 50000)
    if r.random() < 0.05: p['eis'] = r.randint(0, 50000)
    if r.random() < 0.05: p['bik'] = r.randint(0, 10000)
    if r.random() < 0.03: p['blind'] = True
    return p

def household(r, i):
    two = r.random() < 0.55
    h = {'id': f'b{i}', 'year': 2025, 'married': two and r.random() < 0.75,
         'children': [{'age': 5}] * r.choice([0, 0, 1, 2, 3, 4]),
         'persons': [person(r)] + ([person(r)] if two else [])}
    if r.random() < 0.3: h['region'] = 'scotland'
    return h

INC = ['employment', 'trading', 'pension', 'interest', 'dividends', 'gains', 'property']
CON = ['rasGross', 'giftAid', 'vct', 'eis', 'financeCosts']
def variants(h):
    out = []
    for k, p in enumerate(h['persons']):
        for f in INC:
            for d in (1, 100, 1000):
                g = copy.deepcopy(h); g['persons'][k][f] = p.get(f, 0) + d
                g['id'] = f"{h['id']}|{k}|{f}|{d}"; out.append(g)
        for f in CON:
            for d in (1, 100, 1000):
                if f in ('vct', 'eis', 'financeCosts') and f not in p: continue
                g = copy.deepcopy(h); g['persons'][k][f] = p.get(f, 0) + d
                g['id'] = f"{h['id']}|{k}|{f}|{d}"; out.append(g)
    if h['married'] or len(h['persons']) == 2:
        g = copy.deepcopy(h); g['married'] = not h['married']; g['id'] = f"{h['id']}|-|married|0"; out.append(g)
    return out

KEYS = ['personalAllowance', 'liability', 'marriageAllowanceReduction', 'giftAidCharge', 'capitalGainsTax', 'class4',
        'investmentAndFinanceReductions', 'bandsExtendedForPension', 'reliefAtSource', 'marriedCouplesAllowanceReduction',
        'blindPersonsAllowance', 'basicRateLimit']
def tags(o0, o1, k, f):
    t = set()
    d0, d1 = o0['detail'], o1['detail']
    if d0['election'] != d1['election']: t.add('election:' + d0['election'] + '->' + d1['election'])
    if d0['hicbc'] != d1['hicbc']: t.add('hicbc')
    if d0['hicbcPayer'] != d1['hicbcPayer']: t.add('hicbcPayerSwitch')
    for j, (a, b) in enumerate(zip(d0['persons'], d1['persons'])):
        if a['charged']['savingsAllowance'] != b['charged']['savingsAllowance']: t.add(f'psa{j}')
        for key in KEYS:
            if a.get(key) != b.get(key) and key not in ('liability', 'basicRateLimit', 'reliefAtSource'):
                t.add(f'{key}{j}')
        if a['basicRateLimit'] != b['basicRateLimit'] and not (f in ('rasGross', 'giftAid')):
            t.add(f'bandShift{j}')
        if a['charged']['dividendNilRate'] != b['charged']['dividendNilRate'] and f != 'dividends': t.add(f'divNil{j}')
        if a['charged']['savingsStartingRate'] != b['charged']['savingsStartingRate'] and f != 'interest': t.add(f'sr{j}')
    return sorted(t)

def runexe(hs):
    inp = '\n'.join(json.dumps(x) for x in hs) + '\n'
    out = subprocess.run([EXE], input=inp, capture_output=True, text=True, check=True).stdout
    return [json.loads(l) for l in out.splitlines() if l.strip()]

def work(args):
    seed, n = args
    r = random.Random(seed)
    events = []
    hs = [household(r, f'{seed}_{i}') for i in range(n)]
    base = runexe(hs)
    for h, o0 in zip(hs, base):
        vs = variants(h)
        outs = runexe(vs)
        b0 = burden(o0)
        for v, o1 in zip(vs, outs):
            _, k, f, d = v['id'].split('|'); d = int(d)
            db = round(burden(o1) - b0, 2)
            if f in INC:
                bad = db > d + 0.005                 # burden rises by more than the extra income
                rate = db / d
            elif f == 'married':
                db = -db if not v['married'] else db  # burden(married) - burden(unmarried)
                bad = db > 0.005; rate = db
            else:
                # outlay: Gift Aid paid d; RAS gross d (member pays 0.8 d, pension +d: net cost 0.8 d minus the extra
                # relief beyond 20 % which is in db); VCT/EIS subscription d (shares acquired, cost 0); finance costs d
                outlay = d if f in ('giftAid', 'rasGross', 'financeCosts') else 0
                bad = (-db > outlay + 0.005) if f in ('giftAid', 'rasGross', 'financeCosts') else (db > 0.005)
                rate = -db / d
            if bad:
                events.append(dict(id=v['id'], field=f, d=d, dburden=db, rate=round(rate, 4), tags=tags(o0, o1, int(k) if k != '-' else 0, f),
                                   base=h))
    return events

if __name__ == '__main__':
    n, seed, outp = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    chunks = [(seed * 100000 + i, 50) for i in range(n // 50)]
    allev = []
    with Pool(24) as pool:
        for ev in pool.imap_unordered(work, chunks):
            allev.extend(ev)
    with open(outp, 'w') as fh:
        for e in allev: fh.write(json.dumps(e) + '\n')
    from collections import Counter, defaultdict
    by = defaultdict(list)
    for e in allev: by[(e['field'], tuple(e['tags']))].append(e)
    print(f'households {n}, flagged events {len(allev)}, distinct (field, tags) {len(by)}')
    for key, es in sorted(by.items(), key=lambda kv: -len(kv[1]))[:60]:
        worst = max(es, key=lambda e: e['dburden'] - (e['d'] if e['field'] in INC else 0))
        print(len(es), key, 'worst', worst['id'], worst['dburden'], 'per', worst['d'])
