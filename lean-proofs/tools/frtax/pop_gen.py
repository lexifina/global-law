"""Candidate pool for the population study: households with the boxes the Lean model reads, drawn broadly so that
a reweighting (pop_calib.py) can match the DGFiP's published box counts/amounts and RFR brackets.
Derived from harness/gen.py (copied, not edited). Differences: four income tiers (ordinary, affluent, rich, very
rich) to cover the RFR tail up to 30 M EUR; wider distributions; more boxes (1AK, 1GB, 1AA, 1AF, 6RS, 7AE, 7DG...);
no 2CK (the 12.8 % instalment is a payment on account; the DGFiP's net-tax aggregates exclude it and its credit).
usage: pop_gen.py N seed year out.jsonl
"""
import json, random, sys, math


def logn(med, sigma=0.8, lo=1, hi=None):
    v = int(round(med * math.exp(random.gauss(0, sigma))))
    v = max(lo, v)
    return min(v, hi) if hi else v


def household(i, year):
    b = {}
    tier = random.choices([0, 1, 2, 3], [78, 14, 6, 2])[0]
    sit = random.choices(["C", "M", "O", "D", "V"], [43, 27, 4.5, 16.5, 9])[0]
    b["0A" + sit] = 1
    couple = sit in ("M", "O")
    by1 = random.randint(year - 99, year - 30) if sit == "V" else random.randint(year - 92, year - 18)
    b["0DA"] = by1
    by2 = None
    if couple:
        by2 = max(year - 97, min(year - 18, by1 + random.randint(-8, 8)))
        b["0DB"] = by2
    young = by1 > year - 62
    nf = nh = nj = 0
    if young and by1 < year - 20 and random.random() < (0.5 if couple else 0.22):
        nf = random.choices([1, 2, 3, 4, 5, 6], [40, 38, 15, 5, 1.5, 0.5])[0]
    if young and random.random() < (0.03 if couple else 0.07):
        nh = random.choices([1, 2, 3], [55, 35, 10])[0]
    if year - 70 < by1 < year - 40 and random.random() < 0.11:
        nj = random.choices([1, 2, 3], [78, 19, 3])[0]
    kids_age, alt_age = [], []
    if nf:
        b["0CF"] = nf
        for k in range(nf):
            a = random.randint(0, 17)
            kids_age.append(a)
            b[f"0F{k}"] = year - a
        if random.random() < 0.03:
            b["0CG"] = 1
    if nh:
        b["0CH"] = nh
        for k in range(nh):
            a = random.randint(0, 17)
            alt_age.append(a)
            b[f"0H{k}"] = year - a
        if random.random() < 0.03:
            b["0CI"] = 1
    if nj:
        b["0DJ"] = nj
        for k in range(nj):
            b[f"0J{k}"] = year - random.randint(18, 24)
    if random.random() < 0.002:
        b["0CR"] = 1
    anykids = nf + nh + nj > 0
    if not couple and anykids and sit != "V" and random.random() < 0.45:
        b["0BT"] = 1
    if not couple and not anykids and by1 < year - 35 and random.random() < 0.07:
        b["0AL"] = 1
        if random.random() < 0.15:
            b["0AN"] = 1
    if random.random() < 0.03:
        b["0AP"] = 1
    if couple and random.random() < 0.02:
        b["0AF"] = 1
    if not couple and by1 <= year - 75 and random.random() < 0.06:
        b["0AW"] = 1
    if couple and min(by1, by2) <= year - 75 and random.random() < 0.09:
        b["0AS"] = 1
    if sit == "V" and random.random() < 0.01:    # M: case G is incoherent with situation D (A01007)
        b["0AG"] = 1
    # earned income scale by tier
    smed, ssig = {0: (24000, 0.75), 1: (65000, 0.45), 2: (160000, 0.6), 3: (500000, 1.0)}[tier]

    def person(born, sal_box, fr, hs, pen, inv, alim, cho, gb, aa):
        age = year - born
        retired = age >= 62 if tier == 0 else age >= 65
        if not retired and age >= 18 and random.random() < (0.80 if tier == 0 else 0.92):
            v = logn(smed, ssig, 300, 40000000)
            if tier < 3 and random.random() < 0.03:
                b[gb] = v                      # managers' pay (art. 62)
            elif tier == 0 and random.random() < 0.04:
                b[aa] = logn(6000, 0.8, 100, 30000)   # pay from private employers
            else:
                b[sal_box] = v
            base = b.get(sal_box, 0)
            if base and random.random() < 0.18:
                b[fr] = min(logn(3500, 0.7, 50, 80000), int(base * 0.9) if base > 1000 else 50)
            if base and tier < 3 and random.random() < 0.44:
                b[hs] = logn(1100, 0.95, 10, 7500)
        if not retired and age >= 18 and random.random() < 0.18:
            b[cho] = logn(5000, 0.9, 100, 60000)
        if retired and random.random() < 0.96:
            b[pen] = logn({0: 19000, 1: 38000, 2: 70000, 3: 120000}[tier], 0.5, 300, 1000000)
        if random.random() < 0.016:
            b[inv] = logn(9000, 0.6, 300, 60000)
        if random.random() < (0.025 if alim == "1AO" else 0.004):
            b[alim] = logn(3000, 0.8, 100, 40000)

    person(by1, "1AJ", "1AK", "1GH", "1AS", "1AZ", "1AO", "1AP", "1GB", "1AA")
    if couple:
        person(by2, "1BJ", "1BK", "1HH", "1BS", "1BZ", "1BO", "1BP", "1HB", "1BA")
        if random.random() < 0.1 and "1AJ" in b:     # partner with no income of their own
            for k in ("1BJ", "1BK", "1HH", "1BP"):
                b.pop(k, None)
    for k, a in enumerate([a for a in kids_age if a >= 16][:2]):
        if random.random() < 0.35:
            b[["1CJ", "1DJ"][k]] = logn(3500, 0.8, 100, 30000)
            if random.random() < 0.6:
                b[["1IH", "1JH"][k]] = logn(300, 0.8, 10, 3000)
    if nj and random.random() < 0.3:
        b["1CJ"] = b.get("1CJ", 0) + logn(5000, 0.8, 100, 30000)
    if random.random() < 0.0095:        # life annuities: the box follows the age at first payment
        a1 = year - by1
        box = "1AW" if a1 < 50 else "1BW" if a1 < 60 else "1CW" if a1 < 70 else "1DW"
        b[box] = logn(1600, 0.9, 50, 60000)
    # retirement savings (M requires the four ceiling boxes)
    pr_ns = {0: 0.02, 1: 0.07, 2: 0.15, 3: 0.2}[tier]
    for col, rcol, sfx in (("6NS", "6RS", "S"), ("6NT", "6RT", "T")):
        if (col == "6NS" or couple) and random.random() < pr_ns:
            b[col] = logn({0: 1500, 1: 3500, 2: 9000, 3: 20000}[tier], 0.9, 50, 80000)
            b["AP" + sfx] = logn(4500 * (1 + tier), 0.5, 4399, 35194)   # M caps the ceiling (A601)
            for pre in ("DP", "CP", "BP"):
                b[pre + sfx] = logn(3000, 1.0, 0, 60000) if random.random() < 0.5 else 0
            if random.random() < 0.15:
                b[rcol] = logn(1500, 0.8, 50, 30000)
    if couple and "6NS" in b and "6NT" in b and random.random() < 0.8:
        b["6QR"] = 1
    # investment income
    k = {0: 1.0, 1: 4.0, 2: 15.0, 3: 120.0}[tier]
    if random.random() < {0: 0.22, 1: 0.45, 2: 0.65, 3: 0.85}[tier]:
        b["2DC"] = logn(300 * k, 1.6, 1, 60000000)
    if random.random() < {0: 0.27, 1: 0.4, 2: 0.5, 3: 0.6}[tier]:
        b["2TR"] = logn(250 * k, 1.4, 1, 20000000)
    if random.random() < 0.015:
        b["2TS"] = logn(500 * k, 1.2, 1, 5000000)
    if random.random() < 0.025:
        b["2CH"] = logn(1000 * k, 1.1, 1, 2000000)
    inv = b.get("2DC", 0) + b.get("2TR", 0) + b.get("2TS", 0) + b.get("2CH", 0)
    if inv and random.random() < 0.13:
        b["2OP"] = 1
    if inv and random.random() < 0.9:
        b["2BH"] = inv
    if inv and random.random() < 0.02:
        b["2CA"] = logn(150, 0.8, 1, 20000)
    if inv and random.random() < 0.03:
        b["2AB"] = logn(80, 1.0, 1, 20000)
    if inv and random.random() < 0.04:
        b["2CG"] = logn(2000 * k ** 0.5, 1.2, 1, 2000000)
    r4 = random.random()
    if r4 < 0.016:
        v = logn(600 * k ** 0.5, 1.2, 1, 3000000); b["2VV"] = v; b["2UU"] = v
    elif r4 < 0.018:
        v = logn(1200 * k ** 0.5, 1.2, 1, 5000000); b["2WW"] = v; b["2UU"] = v
    elif r4 < 0.034:
        b["2ZZ"] = logn(1300 * k ** 0.5, 1.0, 1, 2000000)
    elif r4 < 0.053:
        b["2DH"] = logn(5000 * k ** 0.5, 1.2, 1, 2000000)
    elif r4 < 0.056:
        b["2YY"] = logn(300 * k ** 0.5, 1.0, 1, 500000)
    if random.random() < 0.0035:
        b["2EE"] = logn(2000, 1.2, 1, 500000)
    r3 = random.random()
    if r3 < {0: 0.001, 1: 0.005, 2: 0.02, 3: 0.12}[tier]:
        b["3VG"] = logn(5000 * k ** 0.8, 1.6, 1, 300000000)
    elif r3 < {0: 0.002, 1: 0.008, 2: 0.03, 3: 0.15}[tier]:
        b["3VH"] = logn(3000 * k ** 0.5, 1.2, 1, 5000000)
    if random.random() < {0: 0.004, 1: 0.01, 2: 0.03, 3: 0.08}[tier]:
        b["3VZ"] = logn(15000 * k ** 0.5, 1.2, 100, 30000000)
    # property
    r = random.random()
    pp = {0: 1.0, 1: 2.0, 2: 3.0, 3: 3.5}[tier]
    if r < 0.034 * pp:
        b["4BE"] = logn(5000, 0.7, 100, 15000)
    elif r < 0.100 * pp:
        b["4BA"] = logn(7000 * k ** 0.5, 1.0, 1, 20000000)
        if random.random() < 0.15:
            b["4BD"] = logn(8000, 1.0, 1, 500000)
    elif r < 0.110 * pp:
        if random.random() < 0.3:
            b["4BB"] = logn(4000, 0.9, 1, 100000)
        b["4BC"] = logn(4500, 0.7, 1, 10700)
        if random.random() < 0.3:
            b["4BD"] = logn(8000, 1.0, 1, 300000)
    # self-employed
    if random.random() < 0.02:
        b[random.choice(["5KO", "5KP", "5HQ", "5HQ"])] = logn(14000, 0.9, 100, 190000)
    if couple and random.random() < 0.02:
        b[random.choice(["5LO", "5LP", "5IQ"])] = logn(13000, 0.9, 100, 190000)
    if random.random() < 0.015 * pp:
        b["5ND"] = logn(7000, 0.8, 100, 200000)
    if couple and random.random() < 0.006 * pp:
        b["5OD"] = logn(7000, 0.8, 100, 200000)
    if random.random() < {0: 0.02, 1: 0.04, 2: 0.15, 3: 0.2}[tier]:
        b[random.choice(["5KC", "5QC", "5QC", "5HC"])] = logn(25000 * k ** 0.5, 1.0, 100, 50000000)
    if couple and random.random() < {0: 0.007, 1: 0.015, 2: 0.05, 3: 0.07}[tier]:
        b[random.choice(["5LC", "5RC", "5RC", "5IC"])] = logn(25000 * k ** 0.5, 1.0, 100, 20000000)
    if random.random() < {0: 0.016, 1: 0.016, 2: 0.03, 3: 0.03}[tier]:
        b[random.choice(["5TA", "5TB", "5TB", "5TE"])] = logn(12000, 1.0, 50, 77700)
    if couple and random.random() < 0.012:
        b[random.choice(["5UA", "5UB", "5UE"])] = logn(12000, 1.0, 50, 77700)
    # charges: CSG deductible, about 6.8 % of the patrimony income taxed at the scale (DD22 otherwise)
    if ("2OP" in b or "4BA" in b or "4BE" in b) and random.random() < 0.85:
        pat = (b.get("2BH", 0) if "2OP" in b else 0) + b.get("4BA", 0) + b.get("4BE", 0) // 2
        if pat > 100:
            b["6DE"] = max(1, int(0.068 * pat * random.uniform(0.3, 1.0)))
    if by1 < year - 40 and random.random() < 0.035:
        b["6EL"] = logn(4000, 0.4, 100, 6794)
        if random.random() < 0.2:
            b["6EM"] = logn(4000, 0.4, 100, 6794)
    if random.random() < 0.027:
        b["6GU"] = logn(3000, 0.8, 100, 60000)
    if random.random() < 0.0016:
        b["6GP"] = logn(5000, 0.7, 100, 50000)
    if random.random() < 0.011:
        b["6DD"] = logn(800, 1.2, 1, 100000)
    # reductions / credits
    gk = {0: 1.0, 1: 2.0, 2: 4.0, 3: 12.0}[tier]
    if random.random() < {0: 0.07, 1: 0.18, 2: 0.3, 3: 0.4}[tier]:
        b["7UF"] = logn(200 * gk, 1.3, 1, 3000000)
    if random.random() < {0: 0.045, 1: 0.1, 2: 0.15, 3: 0.2}[tier]:
        b["7UD"] = logn(150 * gk ** 0.5, 1.0, 1, 50000)
    if random.random() < 0.0045:
        b["7UH"] = logn(150, 1.2, 1, 15000)
    if random.random() < 0.006:
        b["7UJ"] = logn(150, 1.0, 1, 20000)
    if random.random() < 0.0055:
        b["7VC"] = logn(200, 1.2, 1, 20000)
    if random.random() < 0.002:
        b["7VA"] = logn(150, 1.2, 1, 10000)
    if year == 2024 and random.random() < 0.0045:
        b["7UO"] = logn(100, 1.0, 1, 5000)
    if random.random() < {0: 0.10, 1: 0.2, 2: 0.33, 3: 0.4}[tier] + (0.1 if by1 < year - 75 else 0):
        b["7DB"] = logn(2000 * gk ** 0.4, 0.9, 50, 50000)
        if random.random() < 0.08:
            b["7DR"] = min(b["7DB"], logn(1500, 0.8, 1, 20000))
        if random.random() < 0.02:
            b["7DQ"] = 1
        if by1 < year - 75 and random.random() < 0.1:
            b["7DG"] = 1
    for kk, a in enumerate([a for a in kids_age if a < 6][:3]):
        if random.random() < 0.55:
            b[["7GA", "7GB", "7GC"][kk]] = logn(2000, 0.6, 50, 7000)
    for kk, a in enumerate([a for a in alt_age if a < 6][:3]):
        if random.random() < 0.2:
            b[["7GE", "7GF", "7GG"][kk]] = logn(1000, 0.6, 50, 3500)
    col = sum(1 for a in kids_age if 11 <= a <= 14)
    lyc = sum(1 for a in kids_age if 15 <= a <= 17)
    if col and random.random() < 0.8:
        b["7EA"] = col
    if lyc and random.random() < 0.8:
        b["7EC"] = lyc
    acol = sum(1 for a in alt_age if 11 <= a <= 14)
    alyc = sum(1 for a in alt_age if 15 <= a <= 17)
    if acol and random.random() < 0.8:
        b["7EB"] = acol
    if alyc and random.random() < 0.8:
        b["7ED"] = alyc
    if nj and random.random() < 0.7:
        b["7EF"] = nj
    if by1 < year - 45 and random.random() < 0.012 + 0.01 * tier:
        b["7CD"] = logn(15000, 0.6, 100, 60000)
    # union dues: not with actual expenses (the dues are then in 1AK; M I00101/I00102)
    if (b.get("1AJ", 0) + b.get("1AA", 0)) and "1AK" not in b and random.random() < 0.05:
        b["7AC"] = logn(170, 0.6, 1, 1500)
    if b.get("1BJ") and "1BK" not in b and random.random() < 0.065:
        b["7AE"] = logn(160, 0.6, 1, 1500)
    return {"id": f"p{year}_{i}", "year": year, "tier": tier, "boxes": b}


if __name__ == "__main__":
    n = int(sys.argv[1]); seed = int(sys.argv[2]); year = int(sys.argv[3]); out = sys.argv[4]
    random.seed(seed)
    with open(out, "w") as f:
        for i in range(n):
            f.write(json.dumps(household(i, year)) + "\n")
