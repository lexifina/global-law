"""Cases worth an independent arbiter: every place where Mlang, Lean or OpenFisca disagree, returns Mlang refuses,
statutory edges, and random households for income 2020-2023 (the DGFiP still serves calc-2021 ... calc-2026).

usage: build_targets.py out.jsonl
"""
import collections, json, os, random, re, sys

R = os.path.expanduser("~/fr/runs")
random.seed(11)
out, seen = [], set()


def add(src, tag, c):
    nid = f"{src}_{c['id']}"
    if nid in seen:
        return
    seen.add(nid)
    out.append({"id": nid, "year": c["year"], "boxes": c["boxes"], "tag": tag, "src_id": c["id"]})


def load(p):
    return {(c := json.loads(l))["id"]: c for l in open(p)}


final, old, bound = load("/tmp/final.jsonl"), load("/tmp/old.jsonl"), load("/tmp/bound.jsonl")

# 1. the targeted set: rounding margin (F5), union credit (F1), CEHR with flat-levy income (F2), Table 7 couples
for c in load("/tmp/targeted.jsonl").values():
    add("t", c["tag"], c)

# 2. every Lean/M disagreement left in the random sets
for p, src, cases in ((f"{R}/final/diffs.jsonl", "f", final), (f"{R}/old/diffs.jsonl", "o", old)):
    for l in open(p):
        d = json.loads(l)
        add(src, "M≠Lean " + "+".join(d["bad"]), cases[d["id"]])

# 3. OpenFisca disagreements (2024, 2025), stratified by the first figure that differs
of = json.load(open(f"{R}/openfisca_final.json"))
for y, yd in of["years"].items():
    groups = collections.defaultdict(list)
    for row in yd["rows"]:
        bad = [k for k, v in row["checks"].items() if v[0] is None or abs(v[0] - v[1]) > 0.5]
        if bad:
            groups[bad[0]].append(row["id"])
    for k, ids in groups.items():
        for i in random.sample(ids, min(12, len(ids))):
            add("f", f"OpenFisca≠M {k}", final[i])

# 4. returns Mlang refused, up to three per anomaly code and year
for p, src, cases in ((f"{R}/final/cal.log", "f", final), (f"{R}/old/cal.log", "o", old)):
    rej = collections.defaultdict(list)
    for block in open(p).read().split("traitement du fichier ")[1:]:
        cid = block.split('"')[1][:-4]
        ko = re.search(r"ATRT000 \| KO \| (\S+)", block)
        if ko and cid in cases:
            code = ko.group(1)
            rej[(cases[cid]["year"], code)].append(cid)
    for (y, code), ids in sorted(rej.items()):
        for i in random.sample(ids, min(3, len(ids))):
            add(src, f"M refuses {code}", cases[i])

# 5. statutory edges where OpenFisca and the others part (art. 157 bis bands, décote, micro minimum)
for c in bound.values():
    if c["tag"] in ("age_band", "decote", "micro_min"):
        add("b", f"edge {c['tag']}", c)

# 6. random households, income 2020-2023 (no earlier arbiter for these years)
for y in (2020, 2021, 2022, 2023):
    ys = [c for c in old.values() if c["year"] == y]
    high = [c for c in ys if any(c["boxes"].get(k, 0) > 100000 for k in ("1AJ", "2DC", "3VG"))]
    for c in random.sample(high, min(5, len(high))) + random.sample(ys, 20):
        add("o", "random", c)

open(sys.argv[1], "w").write("".join(json.dumps(c) + "\n" for c in out))
print(len(out), collections.Counter(c["tag"].split(" ")[0] for c in out))
