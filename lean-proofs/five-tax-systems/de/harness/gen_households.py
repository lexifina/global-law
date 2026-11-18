#!/usr/bin/env python3
"""Random canonical households (CONTRACT.md format) for the referee runs.

gen_households.py N SEED [--no-charity] [--profile=all|employees|wide] > households.jsonl

The draw covers every feature the German model has: one or two adults, married or not, wages in each social-insurance
regime (none, Minijob, Übergangsbereich, regular, above each ceiling), self-employment, statutory pensions at ages
60-90, 0-4 children aged 0-30, interest/dividends/gains, rents, Basisrente contributions, and donations unless
--no-charity (GETTSIM has no § 10b).
"""
import json, random, sys

def wage(r):
    u = r.random()
    if u < 0.12: return 0
    if u < 0.20: return r.randint(1, 6672)              # Minijob
    if u < 0.32: return r.randint(6673, 24000)          # Übergangsbereich
    if u < 0.80: return r.randint(24001, 90000)
    if u < 0.93: return r.randint(90001, 160000)
    return r.randint(160001, 600000)

def adult(r, age):
    a = {"age": age, "wages": 0, "selfEmployment": 0, "pension": 0}
    if age < 67:
        a["wages"] = wage(r)
        if r.random() < 0.12:
            a["selfEmployment"] = r.choice([r.randint(1, 8000), r.randint(8001, 80000), r.randint(80001, 300000)])
    if age >= 60 and r.random() < (0.9 if age >= 66 else 0.15):
        a["pension"] = r.randint(3000, 36000)
    if age >= 66 and r.random() < 0.15:
        a["wages"] = r.randint(1, 30000)
    return a

def household(r, i, charity=True):
    n = 1 if r.random() < 0.45 else 2
    age1 = r.randint(19, 90)
    adults = [adult(r, age1)]
    if n == 2:
        adults.append(adult(r, max(18, min(95, age1 + r.randint(-8, 8)))))
    married = n == 2 and r.random() < 0.75
    kids = []
    if age1 < 60:
        k = r.choices([0, 1, 2, 3, 4], [40, 22, 25, 9, 4])[0]
        kids = [{"age": r.randint(0, min(30, max(0, age1 - 18)))} for _ in range(k)]
    cap = r.random() < 0.45
    h = {"id": f"h{i}", "year": 2025, "adults": adults, "married": married, "children": kids,
         "interest": r.choice([0, r.randint(1, 3000), r.randint(3001, 40000)]) if cap else 0,
         "dividends": r.choice([0, r.randint(1, 5000), r.randint(5001, 150000)]) if cap else 0,
         "capitalGains": r.choice([0, 0, r.randint(1, 50000)]) if cap else 0,
         "rentalIncome": r.choice([0] * 6 + [r.randint(1, 20000), r.randint(20001, 120000)]),
         "charitable": (r.choice([0] * 5 + [r.randint(1, 500), r.randint(501, 30000)]) if charity else 0),
         "pensionContributions": r.choice([0] * 8 + [r.randint(1, 5000), r.randint(5001, 30000)])}
    return h

if __name__ == "__main__":
    n, seed = int(sys.argv[1]), int(sys.argv[2])
    charity = "--no-charity" not in sys.argv
    r = random.Random(seed)
    for i in range(n):
        print(json.dumps(household(r, i, charity), separators=(",", ":")))
