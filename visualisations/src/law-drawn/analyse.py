"""lives.json + eu.json + Spain's commit trailers -> data.json for the five new charts."""
import json, re, subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
lives = json.loads((HERE / "lives.json").read_text(encoding="utf-8"))
ACT_FILES = {"czechia"}   # one file per whole act, not per provision
prov = {k: v for k, v in lives.items() if k not in ACT_FILES}
eu = json.loads((HERE / "eu.json").read_text(encoding="utf-8"))
NAMES = {"south-korea": "South Korea", "new-zealand": "New Zealand"}
nice = lambda k: NAMES.get(k, k.replace("-", " ").title())
out = {}

# 1. The amended few: how amendments spread over provisions
conc = []
for k, v in prov.items():
    counts = sorted((r[2] for r in v["rows"]), reverse=True)
    tot, n = sum(counts), len(counts)
    if tot < 200 or n < 300: continue
    cum, pts = 0, []
    for i, c in enumerate(counts, 1):
        cum += c
        pts.append((i / n, cum / tot))
    lorenz = [[0, 0]] + [[round(x, 4), round(y, 4)] for x, y in pts[:: max(1, n // 200)]] + [[1, 1]]
    top = lambda q: sum(counts[: max(1, round(n * q))]) / tot
    conc.append({"key": k, "name": nice(k), "provisions": n, "amendments": tot, "top1": top(0.01), "top10": top(0.10),
                 "never": sum(1 for c in counts if c == 0) / n, "max": counts[0], "most": v["most"], "lorenz": lorenz})
out["concentration"] = sorted(conc, key=lambda r: -r["top10"])

# 2. Time to first amendment (Kaplan-Meier), provisions first seen on a dated commit after the record began
km = []
for k, v in prov.items():
    last = date.fromisoformat(v["last"]); first = v["first"]
    obs = []
    for c, f1, n, rep, snap in v["rows"]:
        if not c or c <= first or snap: continue          # skip the record's opening snapshot: its true age is unknown
        c = date.fromisoformat(c)
        if f1:
            obs.append(((date.fromisoformat(f1) - c).days / 365.25, 1))
        else:
            end = date.fromisoformat(rep) if rep else last
            obs.append(((end - c).days / 365.25, 0))
    if len(obs) < 300: continue
    obs.sort()
    at_risk, s, curve, i = len(obs), 1.0, [[0, 1.0]], 0
    while i < len(obs):
        t = obs[i][0]; d = c0 = 0
        while i < len(obs) and obs[i][0] == t:
            d += obs[i][1]; c0 += 1; i += 1
        if d: s *= 1 - d / at_risk; curve.append([round(t, 3), round(s, 4)])
        at_risk -= c0
        if at_risk < 50: break
    surv_at = lambda y: next((p[1] for p in reversed(curve) if p[0] <= y), 1.0)
    med = next((p[0] for p in curve if p[1] <= 0.5), None)
    km.append({"key": k, "name": nice(k), "n": len(obs), "amended": sum(e for _, e in obs), "s1": surv_at(1), "s5": surv_at(5), "s10": surv_at(10),
               "median": med, "horizon": curve[-1][0], "curve": curve[:: max(1, len(curve) // 300)] + [curve[-1]]})
out["first_amendment"] = sorted(km, key=lambda r: r["s5"])

# 3. Each country's biggest day
days = []
for k, v in prov.items():
    total = sum(c.get("M", 0) + c.get("D", 0) + c.get("R", 0) for c in v["years"].values())
    if not v["top_days"]: continue
    n, d, subj = next((t for t in v["top_days"] if not re.search(r"unexplained|oldest version", t[2], re.I)), v["top_days"][0])
    days.append({"key": k, "name": nice(k), "date": d, "events": n, "share": n / total, "total": total, "subject": subj,
                 "runners": [[x[1], x[0], x[2]] for x in v["top_days"][1:3]]})
out["big_days"] = sorted(days, key=lambda r: r["date"])

# 4. EU law in Spanish and Czech statute books
TITLES = {"2016/679": "General Data Protection Regulation", "R575/2013": "Capital Requirements Regulation",
          "R1308/2013": "Common market organisation (farm products)", "1995/46": "Data Protection Directive (1995)",
          "R1234/2007": "Single CMO Regulation (2007)", "R1306/2013": "CAP financing and monitoring", "2021/241": "Recovery and Resilience Facility",
          "1998/34": "Technical standards notification (1998)", "2015/1535": "Technical standards notification (2015)", "R648/2012": "EMIR (derivatives)",
          "R765/2008": "Accreditation and market surveillance", "2021/2115": "CAP strategic plans", "R651/2014": "General Block Exemption Regulation",
          "R1305/2013": "Rural development (EAFRD)", "R73/2009": "CAP direct payments (2009)", "2009/65": "UCITS Directive", "R1224/2009": "Fisheries control",
          "R1069/2009": "Animal by-products", "2005/36": "Professional qualifications", "R1272/2008": "CLP (chemical labelling)", "R1907/2006": "REACH",
          "1998/48": "Amendment to 98/34 (information society)", "2000/60": "Water Framework Directive", "2017/625": "Official controls (2017)",
          "R1093/2010": "European Banking Authority", "R853/2004": "Hygiene of food of animal origin", "R178/2002": "General Food Law",
          "R1107/2009": "Plant protection products", "1999/45": "Dangerous preparations", "R882/2004": "Official food and feed controls (2004)",
          "R1307/2013": "CAP direct payments (2013)", "1967/548": "Dangerous substances (1967)", "1991/414": "Plant protection products (1991)",
          "2016/2031": "Plant health", "R1151/2012": "Food quality schemes", "R854/2004": "Controls on products of animal origin",
          "R396/2005": "Pesticide residue limits"}
es, cz = eu["spain"]["acts"], eu["czechia"]["acts"]
pts = []
for a in set(es) | set(cz):
    x, y = es.get(a, 0), cz.get(a, 0)
    if x + y >= 8:
        year = int(a.lstrip("R").split("/")[1] if a.startswith("R") else a.split("/")[0])
        pts.append({"act": a, "es": x, "cz": y, "year": year, "title": TITLES.get(a), "reg": a.startswith("R") or year >= 2015})
out["eu"] = {"points": pts, "es_total": len(es), "cz_total": len(cz), "shared": len(set(es) & set(cz)),
             "es_prov": eu["spain"]["provisions_citing"], "cz_prov": eu["czechia"]["provisions_citing"],
             "es_files": eu["spain"]["law_files"], "cz_files": eu["czechia"]["law_files"]}

# 5. Spain: how many laws one amending act reaches into
log = subprocess.run(["git", "-C", str(Path.home() / "Documents/spain-law"), "log", "--date=short",
                      "--format=%ad\x1f%an\x1f%(trailers:key=Laws-changed,valueonly,separator=)\x1f%s"],
                     capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
acts, kinds = [], Counter()
for l in log.splitlines():
    d, an, n, s = l.split("\x1f")
    if not n.strip() or "texto inicial" in s or d < "1979": continue
    n = int(n)
    kind = ("Court ruling" if an.startswith("Sentencia") or s.startswith("Sentencia") else "Decree-law" if "Decreto-ley" in s or "Decreto-ley" in an
            else "Legislative decree" if "Decreto Legislativo" in s else "Organic law" if "Ley Orgánica" in s else "Law" if s.startswith("Ley ")
            else "Royal decree" if s.startswith("Real Decreto") else "Order or other")
    acts.append([d, n, kind, s.split(":")[0][:120]])
by_year = defaultdict(list)
for d, n, k, s in acts: by_year[int(d[:4])].append(n)
out["omnibus"] = {"acts": [a for a in acts if a[1] >= 10], "n_acts": len(acts),
                  "years": [{"year": y, "acts": len(v), "mean": sum(v) / len(v), "share5": sum(1 for x in v if x >= 5) / len(v),
                             "reach": sum(v)} for y, v in sorted(by_year.items())],
                  "kinds": {k: {"acts": sum(1 for a in acts if a[2] == k), "mean": sum(a[1] for a in acts if a[2] == k) / max(1, sum(1 for a in acts if a[2] == k)),
                                "big": sum(1 for a in acts if a[2] == k and a[1] >= 10)} for k in sorted({a[2] for a in acts})}}
(HERE / "data.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")

for r in out["concentration"]: print(r["most"][0][:2], end=" "); print(f'{r["name"]:14s} prov {r["provisions"]:7d} amend {r["amendments"]:7d} top1 {r["top1"]:.2f} top10 {r["top10"]:.2f} never {r["never"]:.2f} max {r["max"]}')
print()
for r in out["first_amendment"]: print(f'{r["name"]:14s} n {r["n"]:6d} s1 {r["s1"]:.2f} s5 {r["s5"]:.2f} s10 {r["s10"]:.2f} median {r["median"]} horizon {r["horizon"]:.1f}')
print()
for r in out["big_days"]: print(r["name"], r["date"], r["events"], f'{r["share"]:.2f}', r["subject"][:90])
print()
print({k: v for k, v in out["eu"].items() if k != "points"})
print(out["omnibus"]["n_acts"], out["omnibus"]["kinds"])
for y in out["omnibus"]["years"][::4]: print(y)
print(sorted(out["omnibus"]["acts"], key=lambda a: -a[1])[:8])
