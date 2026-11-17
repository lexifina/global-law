"""Random but plausible French income-tax returns, restricted to the boxes the Lean model covers.

Writes cases.jsonl: {"id":..., "year":..., "boxes": {"1AJ": 30000, ...}}.
Distributions are rough shapes of the national box counts (DGFiP, ir-declarations-2042-nat), not a sample.
Birth-year boxes (0F0.., 0H0.., 0J0..) are filled so M's consistency checks IM1101/1102/1106 pass.
"""
import json, random, sys, math

def logn(med, sigma=0.8, lo=1, hi=None):
    v = int(round(med * math.exp(random.gauss(0, sigma))))
    v = max(lo, v)
    return min(v, hi) if hi else v

def household(i, year, profile="mixed"):
    b = {}
    sit = random.choices(["C", "M", "O", "D", "V"], [43, 27, 5, 16, 9])[0]
    b["0A" + sit] = 1
    couple = sit in ("M", "O")
    by1 = random.randint(year - 90, year - 19)
    b["0DA"] = by1
    by2 = None
    if couple:
        by2 = max(year - 95, min(year - 18, by1 + random.randint(-6, 6)))
        b["0DB"] = by2
    young = by1 > year - 60
    # children
    nf = 0
    if young and random.random() < (0.55 if couple else 0.3):
        nf = random.choices([1, 2, 3, 4, 5], [40, 38, 15, 5, 2])[0]
    nh = 0
    if young and not couple and random.random() < 0.08:
        nh = random.choices([1, 2, 3], [60, 30, 10])[0]
    nj = 0
    if by1 < year - 40 and random.random() < 0.08:
        nj = random.choices([1, 2], [80, 20])[0]
    kids_age = []
    alt_age = []
    if nf:
        b["0CF"] = nf
        for k in range(nf):
            a = random.randint(0, 17)
            kids_age.append(a)
            b[f"0F{k}"] = year - a
        if random.random() < 0.04:
            b["0CG"] = 1
    if nh:
        b["0CH"] = nh
        for k in range(nh):
            a = random.randint(0, 17)
            alt_age.append(a)
            b[f"0H{k}"] = year - a
        if random.random() < 0.04:
            b["0CI"] = 1
    if nj:
        b["0DJ"] = nj
        for k in range(nj):
            b[f"0J{k}"] = year - random.randint(18, 24)
    if random.random() < 0.01:
        b["0CR"] = 1
    anykids = nf + nh + nj > 0
    if not couple and anykids and sit != "V" and random.random() < 0.6:
        b["0BT"] = 1
    if not couple and not anykids and by1 < year - 40 and random.random() < 0.06:
        b["0AL"] = 1
    if random.random() < 0.03:
        b["0AP"] = 1
    if couple and random.random() < 0.03:
        b["0AF"] = 1
    if not couple and by1 < year - 74 and random.random() < 0.1:
        b["0AW"] = 1
    if couple and min(by1, by2) < year - 74 and random.random() < 0.1:
        b["0AS"] = 1
    if sit in ("D", "V") and random.random() < 0.01:
        b["0AG"] = 1

    def person(col_sal, col_fr, col_hs, col_pen, col_inv, col_alim, col_cho, born):
        retired = born < year - 62
        if not retired and random.random() < 0.85 and col_sal not in b:
            b[col_sal] = logn(28000, 0.6, 500, 400000)
            if random.random() < 0.12:
                b[col_fr] = logn(4000, 0.6, 100, 30000)
            if random.random() < 0.2:
                b[col_hs] = logn(1500, 0.7, 50, 7500)
        if not retired and random.random() < 0.08:
            b[col_cho] = logn(9000, 0.6, 200, 40000)
        if retired and random.random() < 0.95:
            b[col_pen] = logn(20000, 0.6, 300, 200000)
        if random.random() < 0.015:
            b[col_inv] = logn(8000, 0.5, 300, 40000)
        if random.random() < 0.02:
            b[col_alim] = logn(3000, 0.6, 100, 20000)

    person("1AJ", "1AK", "1GH", "1AS", "1AZ", "1AO", "1AP", by1)
    if couple:
        person("1BJ", "1BK", "1HH", "1BS", "1BZ", "1BO", "1BP", by2)
    for k, a in enumerate([a for a in kids_age if a >= 16][:2] + [0] * 0):
        if random.random() < 0.15:
            b[["1CJ", "1DJ"][k]] = logn(4000, 0.7, 100, 20000)
    if random.random() < 0.01:
        b[random.choice(["1AW", "1BW", "1CW", "1DW"])] = logn(3000, 0.7, 100, 30000)
    # retirement savings with the ceilings of the last notice (M requires all four ceiling boxes)
    for col, sfx in (("6NS", "S"), ("6NT", "T")):
        if (col == "6NS" or couple) and random.random() < 0.05:
            b[col] = logn(2500, 0.8, 50, 40000)
            b["AP" + sfx] = logn(4500, 0.5, 4399, 40000)
            for pre in ("DP", "CP", "BP"):
                b[pre + sfx] = logn(2000, 1.0, 0, 30000) if random.random() < 0.5 else 0
    if couple and "6NS" in b and "6NT" in b and random.random() < 0.3:
        b["6QR"] = 1
    # a high-income tail (CEHR, CDHR)
    if random.random() < 0.01:
        b[random.choice(["2DC", "3VG", "1AJ"])] = logn(400000, 0.8, 100000, 5000000)
    # investment income
    if random.random() < 0.28 and "2DC" not in b:
        b["2DC"] = logn(600, 1.2, 1, 200000)
    if random.random() < 0.3:
        b["2TR"] = logn(300, 1.1, 1, 100000)
    if random.random() < 0.05:
        b["2TS"] = logn(400, 1.0, 1, 50000)
    if ("2DC" in b or "2TR" in b) and random.random() < 0.15:
        b["2OP"] = 1
    inv = b.get("2DC", 0) + b.get("2TR", 0)
    if inv and random.random() < 0.7:
        b["2BH"] = inv
    if inv and random.random() < 0.5:
        b["2CK"] = int(round(0.128 * inv))
    if inv and random.random() < 0.03:
        b["2CA"] = logn(100, 0.6, 1, 2000)
    r3 = random.random()
    if r3 < 0.05 and "3VG" not in b:
        b["3VG"] = logn(3000, 1.2, 1, 500000)
    elif r3 < 0.06 and "3VG" not in b:  # the form makes 3VG (net gains) and 3VH (net losses) exclusive
        b["3VH"] = logn(1000, 1.0, 1, 50000)
    if random.random() < 0.03:
        b["2CH"] = logn(3000, 1.0, 1, 100000)
    r4 = random.random()
    if r4 < 0.03:
        v = logn(6000, 1.0, 1, 150000); b["2VV"] = v; b["2UU"] = v
    elif r4 < 0.035:
        v = logn(20000, 1.0, 1, 500000); b["2WW"] = v; b["2UU"] = v
    elif r4 < 0.06:
        b["2ZZ"] = logn(2000, 1.0, 1, 80000)
    elif r4 < 0.08:
        b["2DH"] = logn(3000, 1.0, 1, 80000)
    elif r4 < 0.085:
        b["2YY"] = logn(2000, 1.0, 1, 50000)
    if year <= 2024 and random.random() < 0.03:
        b["5ND"] = logn(8000, 0.7, 100, 70000)
    if (inv or "2TS" in b) and random.random() < 0.05:
        b["2CG"] = logn(300, 1.0, 1, 5000)
    # property
    r = random.random()
    if r < 0.04:
        b["4BE"] = logn(6000, 0.6, 100, 15000)
    elif r < 0.10:
        b["4BA"] = logn(9000, 0.8, 1, 200000)
        if random.random() < 0.1:
            b["4BD"] = logn(3000, 0.8, 1, 50000)
    elif r < 0.11:
        b["4BB"] = logn(3000, 0.8, 1, 20000)
        b["4BC"] = logn(3000, 0.8, 1, 10700)
    # micro enterprises
    if random.random() < 0.05:
        b[random.choice(["5KO", "5KP", "5HQ"])] = logn(15000, 0.8, 100, 70000)
    if couple and random.random() < 0.02:
        b[random.choice(["5LO", "5LP", "5IQ"])] = logn(15000, 0.8, 100, 70000)
    # real-regime profits and micro-entrepreneurs under the flat levy
    if random.random() < 0.03:
        b[random.choice(["5KC", "5QC", "5HC"])] = logn(25000, 0.9, 100, 300000)
    if random.random() < 0.03:
        b[random.choice(["5TA", "5TB", "5TE"])] = logn(15000, 0.8, 100, 77000)
    if random.random() < 0.01:
        b["3VZ"] = logn(40000, 0.8, 1000, 500000)
    if random.random() < 0.01:
        b["2EE"] = logn(500, 1.0, 1, 20000)
    if year == 2024 and random.random() < 0.02:
        b["7UO"] = logn(150, 1.0, 1, 5000)
    for g, pr in (("7UJ", 0.02), ("7VC", 0.02), ("7UH", 0.02)):
        if random.random() < pr:
            b[g] = logn(200, 1.0, 1, 15000)
    # charges
    if random.random() < 0.08:
        b["6DE"] = logn(150, 0.8, 1, 5000)
    if random.random() < 0.02:
        b["6EL"] = logn(4000, 0.5, 100, 12000)
    if random.random() < 0.03:
        b["6GU"] = logn(3000, 0.6, 100, 20000)
    if random.random() < 0.01:
        b["6DD"] = logn(500, 0.8, 1, 5000)
    # reductions / credits
    if random.random() < 0.1:
        b["7UF"] = logn(250, 1.0, 1, 20000)
    if random.random() < 0.06:
        b["7UD"] = logn(150, 1.0, 1, 5000)
    if year >= 2025 and random.random() < 0.03:
        b["7UQ"] = logn(150, 1.0, 1, 5000)
    tot = sum(v for k, v in b.items() if k[0] in "12345" and k not in ("2OP", "2BH", "2CK", "2CG"))
    if random.random() < 0.13 and tot > 6000:
        b["7DB"] = min(logn(2500, 0.8, 50, 25000), int(0.4 * tot))
        if random.random() < 0.08:
            b["7DR"] = min(b["7DB"], logn(800, 0.6, 1, 5000))
        if random.random() < 0.05:
            b["7DQ"] = 1
    young_kids = [a for a in kids_age if a < 6]
    for k, a in enumerate(young_kids[:3]):
        if random.random() < 0.5:
            b[["7GA", "7GB", "7GC"][k]] = logn(1800, 0.6, 50, 6000)
    for k, a in enumerate([a for a in alt_age if a < 6][:3]):
        if random.random() < 0.5:
            b[["7GE", "7GF", "7GG"][k]] = logn(900, 0.6, 50, 3000)
    col = sum(1 for a in kids_age if 11 <= a <= 14)
    lyc = sum(1 for a in kids_age if 15 <= a <= 17)
    if col and random.random() < 0.7:
        b["7EA"] = col
    if lyc and random.random() < 0.7:
        b["7EC"] = lyc
    acol = sum(1 for a in alt_age if 11 <= a <= 14)
    alyc = sum(1 for a in alt_age if 15 <= a <= 17)
    if acol and random.random() < 0.7:
        b["7EB"] = acol
    if alyc and random.random() < 0.7:
        b["7ED"] = alyc
    if nj and random.random() < 0.5:
        b["7EF"] = nj
    if by1 < year - 50 and random.random() < 0.015:
        b["7CD"] = logn(6000, 0.5, 100, 25000)
    if "1AJ" in b and random.random() < 0.04:
        b["7AC"] = logn(200, 0.5, 1, 800)
    return {"id": f"h{i}", "year": year, "boxes": b}

if __name__ == "__main__":
    n = int(sys.argv[1]); seed = int(sys.argv[2]); out = sys.argv[3]
    years = [int(y) for y in (sys.argv[4] if len(sys.argv) > 4 else "2024,2025").split(",")]
    random.seed(seed)
    with open(out, "w") as f:
        for i in range(n):
            f.write(json.dumps(household(i, random.choice(years))) + "\n")
