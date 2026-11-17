"""Targeted returns for the withholding rates (art. 204 H, 204 M), income 2020-2025. Each case carries a "family"
naming the edge it probes. Uses the Lean runner to pick returns at rounding boundaries.

usage: pas_edges.py out.jsonl
"""
import json, os, random, subprocess, sys

LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
YEARS = range(2020, 2026)
random.seed(204)
cases = []


def add(fam, year, boxes, note=""):
    b = dict(boxes)
    b.setdefault("0DA", year - 40)
    if "0AM" in b or "0AO" in b:
        b.setdefault("0DB", year - 38)
    for i in range(b.get("0CF", 0)):
        b.setdefault(f"0F{i}", year - 8 - i)
    cases.append({"id": f"p{len(cases)}", "year": year, "family": fam, "note": note, "boxes": b})


def lean(cs):
    inp = "".join(f"{c['id']};{c['year']};" + ",".join(f"{k}={v}" for k, v in c["boxes"].items()) + "\n" for c in cs)
    out = subprocess.run([LEAN], input=inp, capture_output=True, text=True).stdout
    r = {}
    for line in out.splitlines():
        p = line.split(";")
        r[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:] if "=" in kv}
    return r


# 1. rounding of the rate: exact tenth-and-a-half (.x5 exactly, statute and M both up) and fractions .49995-.49999
#    (statute down; M's arr margin up in 2020-2024)
for year in YEARS:
    cand = []
    for i in range(400000):
        sal = random.randint(18000, 160000)
        b = {"0AC": 1, "0DA": year - 40, "1AJ": sal}
        r = random.random()
        if r < 0.3:
            b["2DC"] = random.randint(100, 20000); b["2OP"] = 1
        elif r < 0.5:
            b["1AS"] = random.randint(1000, 30000); b["0DA"] = year - 66
        elif r < 0.7:
            b = {"0AM": 1, "0DA": year - 40, "0DB": year - 38, "1AJ": sal, "1BJ": random.randint(0, 90000)}
        cand.append({"id": f"c{i}", "year": year, "boxes": b})
    res = lean(cand)
    exact, margin = [], []
    for c in cand:
        v = res.get(c["id"], {})
        num, den = v.get("PASNUM", 0), v.get("PASDEN", 0)
        if not den or not num:
            continue
        rem = (1000 * int(num)) % int(den)
        if 2 * rem == int(den):
            exact.append(c)
        elif 0.49995 * den <= rem < 0.5 * den:
            margin.append(c)
    for c in exact[:4]:
        add("rate rounding: exact .x5", year, c["boxes"])
    for c in margin[:6]:
        add("rate rounding: fraction .49995-.49999", year, c["boxes"])

# 2. small tax: household tax after the décote between 1 and 60 EUR (M: rate 0)
for year in YEARS:
    found = 0
    for sal in range(14000, 30000, 7):
        if found >= 4:
            break
        c = {"id": "x", "year": year, "boxes": {"0AC": 1, "0DA": year - 40, "1AJ": sal}}
        v = lean([c])["x"]
        if 0 < v["PASIR"] < 61 and sal % 3 == 0:
            add("small tax (1-60 EUR) household", year, c["boxes"], f"tax {v['PASIR']:.0f}")
            found += 1

# 3. art. 204 H, II: tax nil this year (credit wipes it), prior year nil (8OT), RFR per part around the codified
#    threshold and M's (one indexation ahead)
TH_LEAN = {2020: 25654, 2021: 25705, 2022: 26065, 2023: 27473, 2024: 28792, 2025: 29310}
TH_M = {2020: 25705, 2021: 26065, 2022: 27473, 2023: 28792, 2024: 29310, 2025: 29574}
for year in YEARS:
    for rfr in (TH_LEAN[year] - 1, TH_LEAN[year], (TH_LEAN[year] + TH_M[year]) // 2, TH_M[year] - 1, TH_M[year]):
        sal = round(rfr / 0.9)  # single, salary only: RFR = salary less 10 %
        for adj in range(-3, 4):
            if round((sal + adj) * 0.9) == rfr or (sal + adj) - round((sal + adj) * 0.1) == rfr:
                sal = sal + adj
                break
        add("204 H II threshold (8OT, nil tax via home-help credit)", year,
            {"0AC": 1, "1AJ": sal, "7DB": 6000, "8OT": 1}, f"target RFR {rfr}")
    add("204 H II without 8OT (control)", year, {"0AC": 1, "1AJ": round(TH_LEAN[year] / 0.9) - 50, "7DB": 6000})

# 4. couples: very unequal incomes, equal incomes, one euro apart, lower earner in the décote zone, quarter parts
for year in YEARS:
    for lo in (0, 3000, 9000, 12000, 15000, 18000, 21000, 25000):
        add("couple: lower earner in decote zone", year, {"0AM": 1, "1AJ": 60000, "1BJ": lo})
    add("couple: equal salaries", year, {"0AM": 1, "1AJ": 40000, "1BJ": 40000})
    add("couple: one euro apart", year, {"0AM": 1, "1AJ": 40001, "1BJ": 40000})
    add("couple: equal pensions, one euro apart (allowance cap)", year,
        {"0AM": 1, "0DA": year - 70, "0DB": year - 70, "1AS": 45001, "1BS": 45000})
    add("couple: very unequal (1 to 50)", year, {"0AM": 1, "1AJ": 250000, "1BJ": 5000})
    add("couple: PACS, child (quarter part), unequal", year, {"0AO": 1, "0CF": 1, "1AJ": 65251, "1BJ": 48523})
    add("couple: shared-residence child (eighth parts)", year, {"0AM": 1, "0CH": 1, "0H0": year - 6, "1AJ": 52000, "1BJ": 31000})
    add("couple: lower earner pensions only", year, {"0AM": 1, "0DB": year - 66, "1AJ": 70000, "1BS": 14000})

# 5. income outside the PAS base, and deficits
for year in YEARS:
    add("outside base: dividends at the scale", year, {"0AC": 1, "1AJ": 35000, "2DC": 30000, "2OP": 1})
    add("outside base: gains at the scale", year, {"0AC": 1, "1AJ": 35000, "3VG": 20000, "2OP": 1})
    add("outside base: flat-levy micro (197 C)", year, {"0AC": 1, "1AJ": 35000, "5TB": 30000})
    add("in base: property and annuities", year, {"0AC": 1, "1AJ": 30000, "4BA": 12000, "1AW": 5000})
    add("in base: alimony with a pension", year, {"0AC": 1, "0DA": year - 66, "1AS": 30000, "1AO": 6000})
    add("deficit: actual expenses above salary, with a pension", year,
        {"0AC": 1, "0DA": year - 63, "1AJ": 10000, "1AK": 14000, "1AS": 30000})
    add("deficit: property deficit on global income (4BC)", year, {"0AC": 1, "1AJ": 40000, "4BB": 3000, "4BC": 5000})
    add("dependant's salary (common income for 204 M)", year,
        {"0AM": 1, "0CF": 1, "0F0": year - 17, "1AJ": 50000, "1BJ": 20000, "1CJ": 6000})
    add("charges halved for 204 M (alimony paid)", year, {"0AM": 1, "1AJ": 50000, "1BJ": 20000, "6GU": 4000})

with open(sys.argv[1], "w") as f:
    for c in cases:
        f.write(json.dumps(c) + "\n")
print(len(cases), "cases;", {fam: sum(1 for c in cases if c["family"] == fam) for fam in sorted({c["family"] for c in cases})})
