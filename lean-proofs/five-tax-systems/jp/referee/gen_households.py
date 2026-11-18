"""Random canonical households (contract format) for differential testing.
usage: python3 gen_households.py N SEED [profile] > households.jsonl
profiles: wage (default: wages, pensions, children incl. working students),
          full (adds self-employment, rental, investment income, donations, iDeCo),
          rich (the same with incomes up to billions: top brackets and the 22.5 % floor)."""
import sys, json, random

N, SEED = int(sys.argv[1]), int(sys.argv[2])
profile = sys.argv[3] if len(sys.argv) > 3 else "wage"
rnd = random.Random(SEED)


def wage():
    u = rnd.random()
    if u < 0.12:
        return 0
    if u < 0.35:
        return rnd.randrange(0, 3000000)
    if u < 0.80:
        return int(rnd.lognormvariate(15.3, 0.45))          # median ~ 4.4 M yen
    if u < 0.95:
        return rnd.randrange(6000000, 20000000)
    return rnd.randrange(20000000, 60000000)


def edge_wage():
    """Salaries at the thresholds that matter (and one yen either side)."""
    pts = [650999, 651000, 1059999, 1056000, 1100000, 1230000, 1230001, 1299999, 1300000, 1500000, 1600000,
           1600001, 1650000, 1900000, 1903999, 1904000, 1971999, 1972000, 2015999, 2016000, 3600000, 6600000,
           8500000, 8500001, 10000000, 10950000, 11950000, 20000000, 25450000, 26950000]
    return rnd.choice(pts) + rnd.choice([-1, 0, 0, 1])


def household(i):
    n = 1 if rnd.random() < 0.35 else 2
    married = n == 2 and rnd.random() < 0.85
    adults = []
    for k in range(n):
        age = rnd.randrange(20, 80)
        w = edge_wage() if rnd.random() < 0.15 else wage()
        if age >= 70 and rnd.random() < 0.6:
            w = 0
        pension = 0
        if age >= 60 and rnd.random() < 0.7:
            pension = rnd.randrange(500000, 3500000)
        se = 0
        if profile == "full" and rnd.random() < 0.15:
            se = rnd.randrange(-500000, 15000000)
        adults.append({"age": age, "wages": max(0, w), "selfEmployment": se, "pension": pension})
    kids = []
    if rnd.random() < 0.55:
        for _ in range(rnd.choice([1, 1, 2, 2, 2, 3, 3, 4])):
            age = rnd.randrange(0, 23)
            c = {"age": age}
            if age >= 16 and rnd.random() < 0.5:
                c["wages"] = rnd.choice([rnd.randrange(0, 2200000), edge_wage() if rnd.random() < 0.3 else 0])
            kids.append(c)
    h = {"id": "r%d-%d" % (SEED, i), "year": 2025, "adults": adults, "married": married, "children": kids,
         "interest": 0, "dividends": 0, "capitalGains": 0, "rentalIncome": 0, "charitable": 0,
         "pensionContributions": 0}
    if profile == "rich":
        for a in adults:
            a["wages"] = rnd.choice([0, rnd.randrange(0, 100000000)])
            a["selfEmployment"] = rnd.choice([0, 0, rnd.randrange(-5000000, 300000000)])
        h["capitalGains"] = rnd.choice([0, rnd.randrange(0, 5000000000)])
        h["dividends"] = rnd.choice([0, rnd.randrange(0, 1000000000)])
        h["interest"] = rnd.choice([0, rnd.randrange(0, 50000000)])
        h["rentalIncome"] = rnd.choice([0, rnd.randrange(-10000000, 100000000)])
        h["charitable"] = rnd.choice([0, rnd.randrange(0, 50000000)])
        h["pensionContributions"] = rnd.choice([0, rnd.randrange(0, 2000000)])
        h["jpDividends"] = rnd.choice(["separate", "aggregate", "declared"])
        if rnd.random() < 0.4:
            h["jpGains"] = "declared"
    if profile == "full":
        h["interest"] = rnd.choice([0, 0, rnd.randrange(0, 200000)])
        h["dividends"] = rnd.choice([0, 0, rnd.randrange(0, 3000000)])
        h["capitalGains"] = rnd.choice([0, 0, rnd.randrange(0, 10000000)])
        h["rentalIncome"] = rnd.choice([0, 0, 0, rnd.randrange(-1000000, 5000000)])
        h["charitable"] = rnd.choice([0, 0, rnd.randrange(0, 500000)])
        h["pensionContributions"] = rnd.choice([0, 0, rnd.randrange(0, 600000)])
        h["jpDividends"] = rnd.choice(["separate", "separate", "aggregate", "declared"])
        if rnd.random() < 0.3:
            h["jpGains"] = "declared"
    if n == 1 and kids and rnd.random() < 0.3:
        h["jpSingleParentSex"] = "M"
    return h


for i in range(N):
    print(json.dumps(household(i), ensure_ascii=False))
