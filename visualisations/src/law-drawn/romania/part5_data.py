"""Data for part five of the Romania page (Romania against all of global law) -> part5_data.json. Reads the global clones' summaries in ~/Documents/law-drawn."""
import itertools, json, math
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

HERE, LD = Path(__file__).parent, Path(__file__).parent.parent
out = {}
SE = {"romania", "albania", "bosnia-and-herzegovina", "bulgaria", "croatia", "greece", "kosovo", "montenegro", "north-macedonia", "serbia", "slovenia", "moldova", "turkey"}
EU = {"austria", "belgium", "cyprus", "czechia", "denmark", "estonia", "finland", "france", "germany", "hungary", "ireland", "italy", "latvia", "lithuania",
      "luxembourg", "malta", "netherlands", "poland", "portugal", "slovakia", "spain", "sweden"}
EUROPE = {"united-kingdom", "switzerland", "norway", "iceland", "liechtenstein", "monaco", "andorra", "san-marino", "vatican-city", "ukraine", "belarus",
          "gibraltar", "faroe-islands", "aland", "greenland", "jersey", "guernsey", "isle-of-man", "georgia", "armenia", "azerbaijan", "russia"}
grp = lambda c: 0 if c == "romania" else 1 if c in SE else 2 if c in EU else 3 if c in EUROPE else 4

# 24. Every corpus in global-law as a circle, inside its country, sized by commits: [path, commits]
com = json.loads((LD / "commits.json").read_text(encoding="utf-8"))
out["pack"] = [[p, n] for p, _, n in com]
tot = sum(n for *_, n in com); bycountry = Counter(); [bycountry.update({p.split("/")[0]: n}) for p, _, n in com]
rank = sorted(com, key=lambda r: -r[2]); ro = next(i for i, r in enumerate(rank) if r[0].startswith("romania/"))
print("24 corpora", len(com), "commits", tot, "countries", len(bycountry), "| romania rank", ro + 1, rank[ro][2], f"{rank[ro][2]/tot:.1%}", "| top", rank[:3])
print("   countries", bycountry.most_common(6), "| countries smaller than romania combined:", sum(1 for v in bycountry.values() if v < bycountry["romania"]),
      "| sum of the smallest that fit under romania", (lambda s: next(i for i in range(len(s)) if sum(s[:i + 1]) > bycountry["romania"]))(sorted(bycountry.values())))

# 25. The legal year of every national corpus with 300+ dated acts (1990-2026, analysis11's act rule): acts per calendar day, 366 days
cmp = [x for x in json.loads((LD / "cmp2.json").read_text(encoding="utf-8")) if x["acts"] >= 300 and x["country"] != "trinidad-and-tobago"]
DAYS = [(date(2020, 1, 1) + timedelta(i)).strftime("%m-%d") for i in range(366)]
even = lambda x: -sum(v / x["acts"] * math.log(v / x["acts"]) for v in x["md"].values()) / math.log(366)
cmp.sort(key=lambda x: -even(x))
out["roses"] = [[x["country"], x["acts"], [x["md"].get(d, 0) for d in DAYS], round(even(x), 3), grp(x["country"])] for x in cmp]
print("25 roses", len(out["roses"]), "| most even", [(r[0], r[3]) for r in out["roses"][:4]], "| least", [(r[0], r[3]) for r in out["roses"][-4:]])
for x in cmp:
    if x["country"] in ("romania", "finland", "netherlands", "sweden", "norway", "france", "spain"): print(f"   {x['country']}: 1 Jan {x['jan1']:.1%}, 1st of a month {x['first']:.1%}, acts {x['acts']}")

# 26. Calendar families: average-linkage clustering of the 29 legal years by Jensen-Shannon distance between their 366-day distributions
def vec(x):
    v = [x["md"].get(d, 0) + .5 for d in DAYS]; t = sum(v); return [a / t for a in v]
V = {x["country"]: vec(x) for x in cmp}
def jsd(p, q):
    m = [(a + b) / 2 for a, b in zip(p, q)]; kl = lambda a, b: sum(x * math.log(x / y) for x, y in zip(a, b))
    return math.sqrt((kl(p, m) + kl(q, m)) / 2 / math.log(2))
names = list(V); Dm = {(a, b): jsd(V[a], V[b]) for a in names for b in names}
nodes = {n: {"name": n, "h": 0, "g": grp(n)} for n in names}; members = {n: [n] for n in names}
while len(nodes) > 1:
    h, i, j = min((sum(Dm[(a, b)] for a in members[i] for b in members[j]) / len(members[i]) / len(members[j]), i, j) for i, j in itertools.combinations(nodes, 2))
    k = i + "|" + j; nodes[k] = {"h": round(h, 4), "children": [nodes.pop(i), nodes.pop(j)]}; members[k] = members.pop(i) + members.pop(j)
out["tree"] = next(iter(nodes.values()))
near = sorted((Dm[("romania", b)], b) for b in names if b != "romania")
out["near"] = [[b, round(d, 3)] for d, b in near]
print("26 tree of", len(names), "| romania nearest", near[:4], "| farthest", near[-3:])

(HERE / "part5_data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
