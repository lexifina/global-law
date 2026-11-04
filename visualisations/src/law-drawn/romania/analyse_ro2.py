"""More Romania data -> ro_data2.json: acts issued per year (highest number), emergency ordinances per prime minister,
the Fiscal Code's amendments, the four new codes' implementing laws, and the Official Gazette's rectifications."""
import csv, json, re
from bisect import bisect_left
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
D = HERE / "tip" / "data"
R = json.loads((HERE / "recs.json").read_text(encoding="utf-8"))
laws = list(csv.DictReader((D / "laws.csv").open(encoding="utf-8")))
out = {}

# 1. Numbered afresh each year: the highest number is the year's total, whatever the corpus holds
NUM = re.compile(r"^(Legea|OUG|OG|HG) nr\. (\d+)/(\d{4})$")
seen = defaultdict(dict)        # kind -> {(year, n): published}
for x in laws:
    m = NUM.match(x["label"])
    if m: seen[m.group(1)][(int(m.group(3)), int(m.group(2)))] = x["published"]
issued, dropped = {}, []
for k, s in seen.items():
    nums = defaultdict(list)
    for (y, n) in s: nums[y].append(n)
    issued[k] = {}
    for y in sorted(nums):
        ns = sorted(nums[y])
        # A top number far beyond the rest of the year's sequence is a typo or another kind of act in the source; drop it
        while len(ns) > 5 and ns[-1] - ns[-2] > max(40, .15 * ns[-2]): dropped.append(f"{k} {ns.pop()}/{y}")
        if 1990 <= y <= 2026: issued[k][y] = {"issued": ns[-1], "in_corpus": len(ns)}
    for d_ in [x for x in dropped if x.startswith(k + " ")]:
        n_, y_ = d_.split(" ")[1].split("/"); s.pop((int(y_), int(n_)), None)
print("dropped as outliers:", dropped)
out["issued"] = issued
for k in issued: print(k, {y: v["issued"] for y, v in issued[k].items() if y in (1997, 2000, 2005, 2010, 2015, 2018, 2020, 2024, 2025)})

# 2. Emergency ordinances per prime minister: date each numbered OUG, interpolating between dated neighbours of the same year
PMS = [("Petre Roman", "1989-12-26", "1991-10-16", "FSN"), ("Theodor Stolojan", "1991-10-16", "1992-11-19", "Independent"),
       ("Nicolae Văcăroiu", "1992-11-19", "1996-12-11", "PDSR"), ("Victor Ciorbea", "1996-12-12", "1998-03-30", "PNȚCD"),
       ("Radu Vasile", "1998-04-17", "1999-12-13", "PNȚCD"), ("Mugur Isărescu", "1999-12-22", "2000-12-28", "Independent"),
       ("Adrian Năstase", "2000-12-28", "2004-12-21", "PSD"), ("Călin Popescu-Tăriceanu", "2004-12-29", "2008-12-22", "PNL"),
       ("Emil Boc", "2008-12-22", "2012-02-06", "PDL"), ("Mihai Răzvan Ungureanu", "2012-02-09", "2012-05-07", "Independent"),
       ("Victor Ponta", "2012-05-07", "2015-11-05", "PSD"), ("Dacian Cioloș", "2015-11-17", "2017-01-04", "Independent"),
       ("Sorin Grindeanu", "2017-01-04", "2017-06-29", "PSD"), ("Mihai Tudose", "2017-06-29", "2018-01-16", "PSD"),
       ("Viorica Dăncilă", "2018-01-29", "2019-11-04", "PSD"), ("Ludovic Orban", "2019-11-04", "2020-12-07", "PNL"),
       ("Florin Cîțu", "2020-12-23", "2021-11-25", "PNL"), ("Nicolae Ciucă", "2021-11-25", "2023-06-12", "PNL"),
       ("Marcel Ciolacu", "2023-06-15", "2025-05-06", "PSD"), ("Ilie Bolojan", "2025-06-23", "2026-10-20", "PNL")]
BLOC = {"FSN": "Social democratic", "PDSR": "Social democratic", "PSD": "Social democratic", "PNȚCD": "Centre-right", "PNL": "Centre-right",
        "PDL": "Centre-right", "Independent": "Technocrat or independent"}
oug_dates = []
s = seen["OUG"]
for y in range(1997, 2027):
    known = sorted((n, d) for (yy, n), d in s.items() if yy == y and d)
    top = issued["OUG"].get(y, {}).get("issued", 0)
    if not known: continue
    ns = [n for n, _ in known]
    for n in range(1, top + 1):
        i = bisect_left(ns, n)
        if i < len(ns) and ns[i] == n: d = date.fromisoformat(known[i][1])
        else:
            lo = known[i - 1] if i > 0 else (0, f"{y}-01-01"); hi = known[i] if i < len(ns) else (top + 1, f"{y}-12-31")
            a, b = date.fromisoformat(lo[1]), date.fromisoformat(hi[1])
            d = a + (b - a) * (n - lo[0]) / max(1, hi[0] - lo[0])
        oug_dates.append(d)
pm = []
for name, a, b, party in PMS:
    a, b = date.fromisoformat(a), date.fromisoformat(b)
    if b < date(1997, 1, 1): continue
    a2 = max(a, date(1997, 1, 1))
    n = sum(1 for d in oug_dates if a2 <= d < b)
    pm.append({"name": name, "from": a.isoformat(), "to": b.isoformat(), "party": party, "bloc": BLOC[party], "ougs": n,
               "per_month": n / ((b - a2).days / 30.44), "counted_from": a2.isoformat()})
out["pm"] = pm
for p in pm: print(f'{p["name"]:24s} {p["from"]}..{p["to"]} OUGs {p["ougs"]:4d} per month {p["per_month"]:.1f}')
print("OUGs dated", len(oug_dates), "of issued", sum(v["issued"] for v in issued["OUG"].values() if True))

# 3. The Fiscal Code (2003 and 2015): every amendment, by the kind of act that made it
fis = []
for r in R:
    for a in r["affecting"]:
        m = re.match(r"(Codul fiscal(?: din 2003)?|Legea nr\. 227/2015|Legea nr\. 571/2003)", a)
        if m:
            lab = r["law"] or r["author"]
            k = "Unexplained" if r["kind"] == "publisher" else ("Correction" if r["kind"] == "correction" else lab.split(" nr.")[0])
            fis.append({"code": "2003" if "2003" in a or "571/2003" in a else "2015", "date": r["in_force"], "law": lab, "kind": k,
                        "units": len(re.findall(r"Art\. ", a)) or 1, "first": r["as_enacted"]})
            break
out["fiscal"] = fis
print("fiscal", Counter((f["code"], f["kind"]) for f in fis).most_common(12))
by_code = defaultdict(list)
for f in fis:
    if not f["first"] and f["kind"] not in ("Correction",): by_code[f["code"]].append(f)
for c, v in by_code.items():
    yrs = Counter(f["date"][:4] for f in v); print(c, len(v), "amending events; by year", sorted(yrs.items())[:30])

# 4. The four new codes' implementing laws and the acts each one changed
HUBS = {"Legea nr. 71/2011": "Civil Code", "Legea nr. 76/2012": "Code of Civil Procedure", "Legea nr. 187/2012": "Criminal Code",
        "Legea nr. 255/2013": "Code of Criminal Procedure", "OUG nr. 114/2018": "the 2018 omnibus ordinance"}
spokes = defaultdict(dict)
for r in R:
    lab = r["law"] or r["author"]
    if lab not in HUBS or r["as_enacted"]: continue
    for a in r["affecting"]:
        m = re.match(r"(.+?) (Art\.|Anexa|Titlul|Capitolul|Partea|Preambul|Punctul|Alineatul)", a)
        tgt = (m.group(1) if m else a.split(",")[0]).strip()
        spokes[lab][tgt] = spokes[lab].get(tgt, 0) + (len(re.findall(r"Art\. ", a)) or 1)
out["hubs"] = {h: {"name": HUBS[h], "date": min((r["in_force"] for r in R if (r["law"] or r["author"]) == h and r["in_force"]), default=None),
                   "targets": sorted(spokes[h].items(), key=lambda kv: -kv[1])} for h in HUBS}
for h, v in out["hubs"].items(): print(h, v["name"], v["date"], len(v["targets"]), v["targets"][:5])
shared = Counter(t for h in list(HUBS)[:4] for t in spokes[h]); print("targets hit by 2+ code laws", sum(1 for t, n in shared.items() if n >= 2), shared.most_common(6))

# 5. Rectifications: the Official Gazette correcting its own printed text
rec = []
for r in R:
    lab = r["law"] or r["author"]
    if not lab.startswith("Rectificare"): continue
    for a in r["affecting"][:1]:
        m = re.match(r"(.+?) (Art\.|Anexa|Titlul|Capitolul|Partea|Preambul|Punctul|Alineatul)", a)
        tgt = (m.group(1) if m else a.split(",")[0]).strip()
        o = next((x for x in laws if x["label"] == tgt), None)
        if o and o["published"] and r["published"]:
            rec.append({"rect": lab, "target": tgt, "kind": tgt.split(" nr.")[0], "pub": o["published"], "rect_pub": r["published"],
                        "lag": (date.fromisoformat(r["published"]) - date.fromisoformat(o["published"])).days})
out["rect"] = rec
lg = sorted(x["lag"] for x in rec)
print("rectifications", len(rec), Counter(x["kind"] for x in rec), "median lag", lg[len(lg) // 2] if lg else None, "within 30d", sum(l <= 30 for l in lg))
(HERE / "ro_data2.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"), default=str), encoding="utf-8")
