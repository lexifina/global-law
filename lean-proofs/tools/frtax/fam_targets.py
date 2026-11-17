"""Family-structure cases for the production simulator: each remaining Lean/M disagreement family, the patterns the
Lean model was just corrected on (to confirm), and returns M refuses.  usage: fam_targets.py out.jsonl"""
import collections, json, os, random, re, sys

R = os.path.expanduser("~/fr/runs")
random.seed(3)
cases = {(c := json.loads(l))["id"]: c for l in open(f"{R}/fam.jsonl")}
FL = ("0BT", "0AL", "0AP", "0AF", "0AW", "0AS", "0AG", "0AN")
SIT = ("0AC", "0AD", "0AV", "0AM", "0AO")


def key(c):
    b = c["boxes"]
    kids = any(k in b for k in ("0CF", "0CH", "0DJ", "0CR"))
    return (next(k for k in SIT if k in b), tuple(sorted(k for k in b if k in FL)), kids)


out, seen = [], set()


def add(tag, c):
    if c["id"] not in seen:
        seen.add(c["id"])
        out.append(dict(c, tag=tag))


groups = collections.defaultdict(list)
for l in open(f"{R}/fam/diffs.jsonl"):
    d = json.loads(l)
    c = cases[d["id"]]
    groups[(c["year"] < 2022,) + key(c)].append(c)
for k, cs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    for c in random.sample(cs, min(2, len(cs))):
        add("fam M≠Lean " + "+".join(k[2]) + (" kids" if k[3] else ""), c)
    if len(out) >= 60:
        break
# patterns corrected in Lean on statute grounds (T for a widow(er); S and W need over 74)
acc = {json.loads(l)["id"] for l in open(f"{R}/fam/m.jsonl")}
fixed = collections.defaultdict(list)
for c in cases.values():
    b = c["boxes"]
    if c["id"] not in acc:
        continue
    s, fl, kids = key(c)
    if s == "0AV" and fl == ("0BT",) and kids:
        fixed["T widowed"].append(c)
    if s in ("0AM", "0AO") and fl == ("0AS",) and max(b["0DA"], b["0DB"]) > c["year"] - 74 and min(b["0DA"], b["0DB"]) > c["year"] - 74:
        fixed["S under 74"].append(c)
    if s in ("0AC", "0AD") and fl == ("0AW",) and not kids and b["0DA"] > c["year"] - 74:
        fixed["W under 74"].append(c)
    if s in ("0AC", "0AD", "0AV") and fl == ("0AL", "0AN") and not kids:
        fixed["L with N"].append(c)
    if s in ("0AC", "0AD", "0AV") and fl == ("0AL",) and not kids:
        fixed["L alone"].append(c)
for t, cs in fixed.items():
    for c in random.sample(cs, min(6, len(cs))):
        add("fam fixed " + t, c)
# returns M refuses: two per anomaly code
rej = collections.defaultdict(list)
for block in open(f"{R}/fam/cal.log").read().split("traitement du fichier ")[1:]:
    ko = re.search(r"ATRT000 \| KO \| (\S+)", block)
    if ko:
        rej[ko.group(1)].append(cases[block.split('"')[1][:-4]])
for code, cs in sorted(rej.items()):
    for c in random.sample(cs, min(3, len(cs))):
        add(f"fam M refuses {code}", c)
open(sys.argv[1], "w").write("".join(json.dumps(c) + "\n" for c in out))
print(len(out), collections.Counter(c["tag"].split(" ")[1] for c in out))
