"""Stress set: family structures. Every situation with combinations of the half-part boxes (T, L, P, F, W, S, G, N),
children wholly in charge / in shared residence / disabled, attached adult children, disabled people under the roof,
at incomes around the quotient-familial cap, for income 2020-2025. Some combinations are invalid on the form (T
for a couple, S for a single person): what each program does with them is part of the test.

usage: family_stress.py N seed out.jsonl
"""
import json, random, sys

n, seed, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
random.seed(seed)
FLAGS = ["0BT", "0AL", "0AP", "0AF", "0AW", "0AS", "0AG", "0AN"]
rows = []
for i in range(n):
    y = random.choice([2020, 2021, 2022, 2023, 2024, 2025])
    sit = random.choice(["0AC", "0AD", "0AV", "0AM", "0AO"])
    b = {sit: 1, "0DA": random.choice([1938, 1944, 1950, 1960, 1975, 1990])}
    couple = sit in ("0AM", "0AO")
    if couple:
        b["0DB"] = random.choice([1938, 1946, 1958, 1972, 1988])
    for f in random.sample(FLAGS, random.choice([0, 0, 1, 1, 1, 2, 2, 3])):
        b[f] = 1
    nf = random.choice([0, 0, 1, 1, 2, 2, 3, 4, 5])
    nh = random.choice([0, 0, 0, 1, 2, 3])
    if nf:
        b["0CF"] = nf
        for k in range(nf):
            b[f"0F{k}"] = y - random.randint(1, 17)
        if random.random() < 0.15:
            b["0CG"] = random.randint(1, nf)
    if nh:
        b["0CH"] = nh
        for k in range(nh):
            b[f"0H{k}"] = y - random.randint(1, 17)
        if random.random() < 0.15:
            b["0CI"] = random.randint(1, nh)
    if random.random() < 0.08:
        b["0DJ"] = 1
        b["0J0"] = y - 20
    if random.random() < 0.05:
        b["0CR"] = 1
    # income around the cap: tax saved by the extra parts close to what they may save
    lvl = random.choice([12000, 25000, 40000, 60000, 80000, 110000, 160000, 250000])
    inc = int(lvl * random.uniform(0.85, 1.15))
    if b["0DA"] < 1955 and random.random() < 0.6:
        b["1AS"] = inc
    else:
        b["1AJ"] = inc
    if couple and random.random() < 0.6:
        b["1BJ"] = int(inc * random.uniform(0.1, 0.9))
    rows.append({"id": f"fam{i}", "year": y, "boxes": b})
open(out, "w").write("".join(json.dumps(r) + "\n" for r in rows))
print(len(rows))
