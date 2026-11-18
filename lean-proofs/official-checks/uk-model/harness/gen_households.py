"""Random canonical households (contract format), seeded. usage: gen_households.py N seed out.jsonl [profile]
profile: mixed (default) | simple (wages only) | invest (investment-heavy) | edges (near thresholds)"""
import json, random, sys

def lognum(r, lo, hi):
    import math
    return int(math.exp(r.uniform(math.log(lo), math.log(hi))))

def money(r, p_zero, lo, hi):
    return 0 if r.random() < p_zero else lognum(r, lo, hi)

EDGE = [12570, 17570, 37700, 50270, 60000, 80000, 100000, 125140, 6845, 3000, 5000, 500, 1000, 125, 242,
        50270 - 1260, 12570 - 1260, 11310, 13830]

def edge(r):
    b = r.choice(EDGE)
    return max(0, b + r.choice([-2, -1, 0, 1, 2, r.randint(-300, 300)]))

def household(r, i, profile):
    n_adults = 1 if r.random() < 0.45 else 2
    adults = []
    for k in range(n_adults):
        age = r.choice([r.randint(18, 65), r.randint(18, 65), r.randint(18, 95)])
        if profile == 'edges':
            wages = edge(r) if r.random() < 0.7 else 0
            se = edge(r) if r.random() < 0.2 else 0
            pen = edge(r) if (age >= 60 and r.random() < 0.5) else 0
        else:
            wages = money(r, 0.25, 1000, 300000)
            se = money(r, 0.8, 500, 150000)
            pen = money(r, 0.5 if age >= 60 else 0.95, 1000, 60000)
        if profile == 'simple':
            se = 0; pen = 0
        adults.append({"age": age, "wages": wages, "selfEmployment": se, "pension": pen})
    married = n_adults == 2 and r.random() < 0.7
    n_kids = r.choice([0, 0, 0, 1, 2, 2, 3, 4]) if any(a["age"] < 60 for a in adults) else 0
    children = [{"age": r.randint(0, 21)} for _ in range(n_kids)]
    if profile == 'simple':
        inv = dict(interest=0, dividends=0, capitalGains=0, rentalIncome=0, charitable=0, pensionContributions=0)
    elif profile == 'invest':
        inv = dict(interest=money(r, 0.1, 10, 60000), dividends=money(r, 0.1, 10, 150000),
                   capitalGains=money(r, 0.3, 100, 200000), rentalIncome=money(r, 0.6, 500, 60000),
                   charitable=money(r, 0.7, 10, 20000), pensionContributions=money(r, 0.7, 100, 40000))
    elif profile == 'edges':
        inv = dict(interest=edge(r) if r.random() < 0.5 else money(r, 0.5, 10, 3000),
                   dividends=edge(r) if r.random() < 0.4 else money(r, 0.5, 10, 3000),
                   capitalGains=edge(r) if r.random() < 0.3 else 0, rentalIncome=0,
                   charitable=money(r, 0.8, 10, 5000), pensionContributions=money(r, 0.8, 100, 10000))
    else:
        inv = dict(interest=money(r, 0.5, 10, 30000), dividends=money(r, 0.6, 10, 80000),
                   capitalGains=money(r, 0.8, 100, 100000), rentalIncome=money(r, 0.85, 500, 40000),
                   charitable=money(r, 0.85, 10, 10000), pensionContributions=money(r, 0.8, 100, 30000))
    h = {"id": f"{profile}-{i}", "year": 2025, "adults": adults, "married": married, "children": children}
    h.update(inv)
    return h

if __name__ == '__main__':
    n, seed, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    profile = sys.argv[4] if len(sys.argv) > 4 else 'mixed'
    r = random.Random(seed)
    with open(out, 'w') as f:
        for i in range(n):
            f.write(json.dumps(household(r, i, profile)) + '\n')
