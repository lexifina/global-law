#!/usr/bin/env python3
"""Random inputs for the PAP 2025 (Lohnsteuer), covering its branches. pap_cases.py N SEED > cases.jsonl

Fields as in the PAP XML: LZZ, RE4 (cents for the pay period), STKL, ZKF (one decimal), KRV, KVZ (per cent, two
decimals), PKV, PKPV (monthly, cents), PVS, PVZ, PVA, R, ALTER1, AJAHR, LZZFREIB, LZZHINZU (cents per period).
"""
import json, math, random, sys

def case(r, i):
    lzz = r.choices([1, 2, 3, 4], [55, 35, 5, 5])[0]
    u = r.random()
    if u < 0.05: annual = r.randint(0, 12000)
    elif u < 0.15: annual = r.randint(12000, 25000)
    else: annual = int(math.exp(r.uniform(math.log(15000), math.log(450000))))
    cents = annual * 100 + r.randint(0, 99)
    re4 = {1: cents, 2: cents // 12, 3: cents * 7 // 360, 4: cents // 360}[lzz]
    stkl = r.choices([1, 2, 3, 4, 5, 6], [30, 10, 20, 20, 10, 10])[0]
    zkf = 0.0
    if stkl <= 4 and r.random() < 0.45:
        zkf = r.choice([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0])
    pkv = r.choices([0, 1, 2], [84, 7, 9])[0]
    pvz = 1 if r.random() < 0.3 else 0
    c = {"id": f"p{i}", "LZZ": lzz, "RE4": re4, "STKL": stkl, "ZKF": zkf,
         "KRV": 1 if r.random() < 0.15 else 0,
         "KVZ": round(r.choice([2.5, 2.5, r.uniform(0.5, 4.0)]), 2),
         "PKV": pkv, "PKPV": r.randint(20000, 120000) if pkv else 0,
         "PVS": 1 if r.random() < 0.1 else 0, "PVZ": pvz,
         "PVA": 0 if pvz else r.choices([0, 1, 2, 3, 4], [60, 20, 10, 5, 5])[0],
         "R": 1 if r.random() < 0.5 else 0, "ALTER1": 0, "AJAHR": 0, "LZZFREIB": 0, "LZZHINZU": 0}
    if r.random() < 0.1:
        c["ALTER1"] = 1
        c["AJAHR"] = r.randint(2003, 2025)
    if r.random() < 0.12:
        c["LZZFREIB"] = {1: 1, 2: 1, 3: 0, 4: 0}[lzz] * r.randint(10000, 2000000) // (12 if lzz == 2 else 1)
    if r.random() < 0.05:
        c["LZZHINZU"] = {1: 1, 2: 1, 3: 0, 4: 0}[lzz] * r.randint(10000, 1500000) // (12 if lzz == 2 else 1)
    return c

if __name__ == "__main__":
    n, seed = int(sys.argv[1]), int(sys.argv[2])
    r = random.Random(seed)
    for i in range(n):
        print(json.dumps(case(r, i)))
