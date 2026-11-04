"""data2_raw.json -> data2.json for the second five charts, and the numbers their captions quote."""
import json, math, re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
R = json.loads((HERE / "data2_raw.json").read_text(encoding="utf-8"))
out = {}

# 1. Spiral: every Spanish act in force 1979-2026
GROUP = {"Law": "Law", "Organic law": "Law", "Decree-law": "Decree-law", "Royal decree": "Royal decree"}
sp = [[a[0], min(a[1], 99), GROUP.get(a[2], "Other"), a[3], a[4]] for a in R["es_acts"] if "1979-01-01" <= a[0] <= "2026-12-31"]
out["spiral"] = sp
jan1 = sum(1 for a in sp if a[0][5:] == "01-01"); first = sum(1 for a in sp if a[0][8:] == "01")
dec = Counter(a[0][5:] for a in sp)
print(f"spiral {len(sp)} acts; 1 Jan {jan1} ({jan1/len(sp):.1%}); first of month {first/len(sp):.1%}; top dates {dec.most_common(6)}")
print("by month", [sum(1 for a in sp if a[0][5:7] == f"{m:02d}") for m in range(1, 13)])
print("acts with day 31-12/01-01 and laws>=10:", sum(1 for a in sp if a[0][5:] in ("01-01", "12-31") and a[1] >= 10), "of", sum(1 for a in sp if a[1] >= 10))

# 2. Chord: Spanish laws amended together, families merge successive recasts of the same law
FAM = {
 "BOE-A-1994-14960": ("Social Security Act", "Social"), "BOE-A-2015-11724": ("Social Security Act", "Social"),
 "BOE-A-2006-20764": ("Income Tax Act", "Tax"), "BOE-A-1992-28740": ("VAT Act", "Tax"), "BOE-A-1992-28925": ("VAT Regulation", "Tax"),
 "BOE-A-2000-323": ("Civil Procedure Act", "Justice"), "BOE-A-1985-12666": ("Judiciary Act", "Justice"), "BOE-A-1992-28741": ("Excise Duties Act", "Tax"),
 "BOE-A-1947-11795": ("Customs Ordinances", "Tax"), "BOE-A-1993-25359": ("Transfer Tax Act", "Tax"), "BOE-A-1889-4763": ("Civil Code", "Justice"),
 "BOE-A-2000-15060": ("Labour Offences Act", "Social"), "BOE-A-2004-4214": ("Local Finance Act", "Other"), "BOE-A-1988-18764": ("Securities Market Act", "Other"),
 "BOE-A-2004-4456": ("Corporate Tax Act", "Tax"), "BOE-A-2014-12328": ("Corporate Tax Act", "Tax"), "BOE-A-1995-25444": ("Criminal Code", "Justice"),
 "BOE-A-1995-7730": ("Workers' Statute", "Social"), "BOE-A-2015-11430": ("Workers' Statute", "Social"), "BOE-A-1987-12636": ("State Pensions Act", "Social"),
 "BOE-A-1984-17387": ("Civil Service Reform Act", "Other"), "BOE-A-1998-23284": ("Hydrocarbons Act", "Other"), "BOE-A-1882-6036": ("Criminal Procedure Act", "Justice"),
 "BOE-A-1991-14463": ("Canary Islands Tax Regime", "Tax"), "BOE-A-1985-11672": ("Electoral Act", "Other"), "BOE-A-1985-5392": ("Local Government Act", "Other"),
 "BOE-A-1998-16718": ("Administrative Courts Act", "Justice"),
}
names = sorted({v[0] for v in FAM.values()})
area = {v[0]: v[1] for v in FAM.values()}
M = defaultdict(Counter); solo = Counter()
for a in R["es_acts"]:
    fams = sorted({FAM[i][0] for i in a[5] if i in FAM})
    for f in fams: solo[f] += 1
    for i, f in enumerate(fams):
        for g in fams[i + 1:]: M[f][g] += 1; M[g][f] += 1
AREA_ORDER = ["Tax", "Social", "Justice", "Other"]
names = [n for n in names if sum(M[n].values())]   # drop laws that never share an act with another
order = sorted(names, key=lambda n: (AREA_ORDER.index(area[n]), -sum(M[n].values())))
out["chord"] = {"names": order, "area": [area[n] for n in order], "matrix": [[M[a][b] for b in order] for a in order], "acts": [solo[n] for n in order]}
pairs = sorted(((M[a][b], a, b) for a in names for b in names if a < b), reverse=True)[:10]
print("chord top pairs", pairs)
print("chord acts per law", solo.most_common())

# 3. Ridgeline: acts by in-force year since 1990 (the published analysis11 series)
KEEP = ["france", "czechia", "spain", "armenia", "georgia", "sweden", "hong-kong", "costa-rica", "switzerland", "azerbaijan", "malta",
        "australia-northern-territory", "turkey", "mexico", "canada-ontario", "austria", "australia-south-australia", "italy", "russia", "canada", "portugal"]
NICE = {"hong-kong": "Hong Kong", "costa-rica": "Costa Rica", "australia-northern-territory": "Northern Territory (AU)", "australia-south-australia": "South Australia",
        "canada-ontario": "Ontario"}
ridges = []
for k in KEEP:
    y = {int(a): b for a, b in R["years"][k].items() if 1990 <= int(a) <= 2025}   # 2026 is a partial year
    if not y: continue
    y0 = min(y)
    xs = [y0 + i / 4 for i in range(int((2026.0 - y0) * 4) + 1)]
    sm = [sum(c * math.exp(-((x - (yr + .5)) ** 2) / (2 * .9 ** 2)) for yr, c in y.items()) for x in xs]
    mx = max(sm) or 1
    peak = xs[sm.index(mx)]
    ridges.append({"key": k, "name": NICE.get(k, k.replace("-", " ").title()), "x0": y0, "pts": [round(v / mx, 3) for v in sm],
                   "total": sum(y.values()), "peak_year": max(y, key=y.get), "peak": max(y.values()), "years": y})
ridges.sort(key=lambda r: r["peak_year"])
out["ridges"] = ridges
for r in ridges: print(f'{r["name"]:24s} {r["x0"]} total {r["total"]:6d} peak {r["peak_year"]} ({r["peak"]})')

# 4. Circle packing: every norm of the Spanish statute book
RG = {"ley": "Laws", "ley-organica": "Laws", "constitucion": "Laws", "real-decreto": "Royal decrees", "decreto": "Royal decrees",
      "real-decreto-ley": "Decree-laws", "decreto-ley": "Decree-laws", "real-decreto-legislativo": "Legislative decrees", "orden": "Orders",
      "resolucion": "Resolutions, circulars and instructions", "circular": "Resolutions, circulars and instructions", "instruccion": "Resolutions, circulars and instructions",
      "acuerdo-internacional": "International agreements", "acuerdo": "Resolutions, circulars and instructions", "reglamento": "Royal decrees"}
pack = defaultdict(list)
for nid, n in R["es_norms"].items():
    pack[RG.get(n["rank"], "Other")].append([nid, n["prov"], n["amended"], n["year"], (n.get("title") or "")[:160]])
out["pack"] = {g: sorted(v, key=lambda r: -r[1]) for g, v in pack.items()}
tot = sum(n["prov"] for n in R["es_norms"].values())
print("pack", {g: (len(v), sum(r[1] for r in v)) for g, v in out["pack"].items()}, "total provisions", tot)
never = sum(1 for n in R["es_norms"].values() if n["amended"] == 0)
print(f"norms never amended {never}/{len(R['es_norms'])} = {never/len(R['es_norms']):.1%}; provisions in those {sum(n['prov'] for n in R['es_norms'].values() if n['amended']==0)/tot:.1%}")
for g in ("Laws", "Royal decrees", "Orders"):
    v = out["pack"][g]; print(g, "amended share", f"{sum(1 for r in v if r[2]) / len(v):.0%}")

# 5. Arc diagram: amendments to the Code civil, 1994-2026
arts = R["fr_articles"]; idx = {a: i for i, a in enumerate(arts)}
arcs, per_art, acts5 = [], Counter(), []
for d, an, s, changed in R["fr"]:
    if "oldest version" in s or an == "Lexifina": continue
    ii = sorted({idx[a] for a in changed if a in idx})
    if not ii: continue
    law = re.search(r"\(([^()]*(?:\([^()]*\))?[^()]*)\)\s*$", s)
    acts5.append([d, law.group(1) if law else s, len(ii), ii[0], ii[-1]])
    for a in ii: per_art[a] += 1
    for a, b in zip(ii, ii[1:]): arcs.append([a, b, int(d[:4]), len(acts5) - 1])
bounds = {}
for label, start in (("Preliminary title", "art-0001"), ("Book I · Persons", "art-0007"), ("Book II · Property", "art-0516"), ("Book III · Acquiring property", "art-0711"),
                     ("Book IV · Securities", "art-2284"), ("Book V · Mayotte", "art-2489")):
    bounds[label] = next(i for i, a in enumerate(arts) if a >= start)
out["arcs"] = {"n": len(arts), "arcs": arcs, "acts": acts5, "per_art": [per_art[i] for i in range(len(arts))], "bounds": bounds,
               "labels": [a[4:].lstrip("0").replace("-0", "-").replace("-00", "-") for a in arts]}
book_hits = Counter()
for a, c in per_art.items():
    b = max((v, k) for k, v in bounds.items() if v <= a)[1]; book_hits[b] += c
print("code civil acts", len(acts5), "arcs", len(arcs), "articles touched", len(per_art), "of", len(arts), book_hits)
print("widest acts", sorted(acts5, key=lambda a: -a[2])[:6])
print("most amended articles", [(arts[i], c) for i, c in per_art.most_common(8)])
(HERE / "data2.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print("data2.json", (HERE / "data2.json").stat().st_size)
