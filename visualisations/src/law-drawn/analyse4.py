"""acts3.json -> data3.json for the regional figures: the corpus pack, federation calendars, Russia's regional waves,
and how long regional law waits."""
import json
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
A = json.loads((HERE / "acts3.json").read_text(encoding="utf-8"))
nice = lambda s: {"united-states": "United States", "hong-kong": "Hong Kong", "new-zealand": "New Zealand", "south-korea": "South Korea",
                  "south-africa": "South Africa", "united-kingdom": "United Kingdom", "costa-rica": "Costa Rica"}.get(s, s.replace("-", " ").title())
out = {}

# 1. Pack: every corpus with dated acts, by country
out["pack"] = [[r["country"], nice(r["country"]), r["region"], r["level"], r["acts"], r["repo"]] for r in A]
lv = Counter(); [lv.update({r["level"]: r["acts"]}) for r in A]
print("pack", len(A), "corpora", len({r["country"] for r in A}), "countries", dict(lv))

# 2. Federation calendars: share of regional acts on each day of the year
FED = ["united-states", "switzerland", "australia", "germany", "canada", "spain", "mexico", "russia", "brazil", "argentina", "peru"]
cal = []
for c in FED:
    rs = [r for r in A if r["country"] == c and r["level"] != "national"]
    md = Counter()
    for r in rs:
        for d, n in r["dates"].items(): md[d[5:]] += n
    tot = sum(md.values())
    days = [(date(2024, 1, 1) + timedelta(i)).strftime("%m-%d") for i in range(366)]
    cal.append({"key": c, "name": nice(c), "corpora": len(rs), "acts": tot, "share": [md.get(d, 0) / tot for d in days],
                "first": sum(n for k, n in md.items() if k.endswith("-01")) / tot, "top": md.most_common(1)[0]})
out["calendars"] = cal
for x in cal: print(f'{x["name"]:14s} corpora {x["corpora"]:3d} acts {x["acts"]:6d} first-of-month {x["first"]:.0%} top {x["top"]}')

# 3. Russia: regional acts per week, 2015-2025
ru = [r for r in A if r["country"] == "russia" and r["level"] == "region"]
start = date(2015, 1, 5)
weeks = (date(2026, 1, 5) - start).days // 7
rows = []
for r in ru:
    w = [0] * weeks
    for d, n in r["dates"].items():
        k = (date.fromisoformat(d) - start).days // 7
        if 0 <= k < weeks: w[k] += n
    if sum(w) >= 20: rows.append({"region": nice(r["region"]), "weeks": w, "acts": sum(w)})
rows.sort(key=lambda x: -x["acts"])
wk_regions = [sum(1 for r in rows if r["weeks"][k]) for k in range(weeks)]
out["russia"] = {"start": start.isoformat(), "rows": rows, "active": wk_regions}
top = sorted(range(weeks), key=lambda k: -wk_regions[k])[:8]
print("russia", len(rows), "regions; busiest weeks", [((start + timedelta(7 * k)).isoformat(), wk_regions[k]) for k in top])
dec = sum(n for r in ru for d, n in r["dates"].items() if d[5:7] == "12" and "2015" <= d[:4] <= "2025")
allr = sum(n for r in ru for d, n in r["dates"].items() if "2015" <= d[:4] <= "2025")
print(f"russia december share {dec/allr:.1%} ({dec}/{allr})")

# 4. How long regional law waits: each corpus's median days from enactment to force
lag = [{"country": r["country"], "name": nice(r["country"]), "region": nice(r["region"]), "level": r["level"], "lag": r["lag_median"], "acts": r["acts"]}
       for r in A if r["lag_median"] is not None and r["level"] != "national" and r["acts"] >= 30]
out["lags"] = lag
by = defaultdict(list)
for x in lag: by[x["name"]].append(x["lag"])
for k, v in sorted(by.items(), key=lambda kv: sorted(kv[1])[len(kv[1]) // 2]): print(f"{k:14s} n {len(v):3d} median-of-medians {sorted(v)[len(v)//2]}")
(HERE / "data3.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
