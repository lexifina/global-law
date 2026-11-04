"""recs.json + data/*.json|csv -> ro_data.json, and the numbers the captions quote."""
import csv, json, re, unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
D = HERE / "tip" / "data"
R = json.loads((HERE / "recs.json").read_text(encoding="utf-8"))
laws = list(csv.DictReader((D / "laws.csv").open(encoding="utf-8")))
acts = json.loads((D / "acts.json").read_text(encoding="utf-8"))["acts"]
plain = lambda s: "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c)).replace("ş", "s").replace("ţ", "t")
days = lambda a, b: (date.fromisoformat(b) - date.fromisoformat(a)).days
out = {}

# Kind of each act from its label
def kind(label):
    l = label.split(" nr.")[0]
    return {"Legea": "Law", "OUG": "OUG", "OG": "OG", "HG": "HG", "Decizia": "CCR", "Rectificare": "Rectification"}.get(l, l)
L = {x["key"]: x for x in laws}

# 1. Emergency ordinances and the laws that approve or reject them (Constitution art. 115)
oug = {}
for x in laws:
    m = re.match(r"OUG nr\. (\d+)/(\d{4})", x["label"])
    if m and x["published"]: oug[(int(m.group(1)), int(m.group(2)))] = x
appr = []
for x in laws:
    if not x["label"].startswith("Legea"): continue
    t = plain(x["title"])
    m = re.search(r"privind (aprobarea|respingerea)( cu modificari si completari)? a? ?ordonantei de urgenta a guvernului nr\. ?(\d+)/(\d{4})", t)
    if not m:
        m = re.search(r"pentru (aprobarea|respingerea)( cu modificari si completari)? a? ?ordonantei de urgenta a guvernului nr\. ?(\d+)/(\d{4})", t)
    if not m: continue
    k = (int(m.group(3)), int(m.group(4)))
    o = oug.get(k)
    if not o or not x["enacted"]: continue
    appr.append({"oug": f"OUG {k[0]}/{k[1]}", "oug_pub": o["published"], "law": x["label"], "law_date": x["published"] or x["enacted"],
                 "verdict": "rejected" if m.group(1) == "respingerea" else ("amended" if m.group(2) else "approved"),
                 "lag": days(o["published"], x["published"] or x["enacted"]), "title": o["title"][:160]})
appr = [a for a in appr if a["lag"] >= 0]
out["approvals"] = appr
lags = sorted(a["lag"] for a in appr)
print(f"OUGs in laws.csv {len(oug)}; matched approval/rejection laws {len(appr)}; verdicts {Counter(a['verdict'] for a in appr)}")
print("lag median", lags[len(lags) // 2], "p90", lags[int(len(lags) * .9)], "over 1y", sum(l > 365 for l in lags), "over 5y", sum(l > 1826 for l in lags), "max", max(appr, key=lambda a: a["lag"]))

# 2. Primary acts per year by kind: laws, OUG, OG (and HG separately)
per_year = defaultdict(Counter)
for x in laws:
    if not x["published"]: continue
    per_year[int(x["published"][:4])][kind(x["label"])] += 1
out["per_year"] = {y: dict(c) for y, c in sorted(per_year.items()) if 1990 <= y <= 2026}
print("per year 2016-2019", {y: dict(per_year[y]) for y in (2016, 2017, 2018, 2019, 2020)})
o13 = [x for x in laws if x["label"] in ("OUG nr. 13/2017", "OUG nr. 14/2017")]
print("OUG 13/14 2017 present:", [(x["label"], x["published"], x["title"][:90]) for x in o13])

# 3. How each act decides its first day: days from publication to force, for acts as enacted
start = defaultdict(Counter)
for r in R:
    if not r["as_enacted"] or not r["published"] or not r["in_force"]: continue
    k = kind(r["law"] or r["author"])
    d = days(r["published"], r["in_force"])
    start[k][d if d <= 400 else 401] += 1
out["start"] = {k: dict(sorted(c.items())) for k, c in start.items() if sum(c.values()) >= 50}
for k, c in start.items():
    tot = sum(c.values())
    if tot >= 50: print(f"start {k:12s} n {tot:6d} same day {c[0]/tot:.1%} 3 days {c[3]/tot:.1%} >30 {sum(v for d,v in c.items() if d>30)/tot:.1%}")

# 4. The Constitutional Court: rulings that struck or conditioned text, by the act they hit
ccr = []
for r in R:
    if r["kind"] != "court": continue
    for a in r["affecting"]:
        m = re.match(r"(.+?) (Art\.|Anexa|Titlul|Capitolul|Partea)", a)
        tgt = m.group(1) if m else a
        ccr.append({"decision": r["law"] or r["author"], "date": r["in_force"], "enacted": r["enacted"], "target": tgt, "units": a[len(tgt):].strip()[:120]})
out["ccr"] = ccr
print("ccr", len(ccr), "rulings", len({c["decision"] for c in ccr}), Counter(c["target"] for c in ccr).most_common(10))

# 5. The Fiscal Code (Legea 227/2015) and its predecessor (571/2003): every amending act
fis = []
for r in R:
    for a in r["affecting"]:
        if a.startswith("Legea nr. 227/2015") or a.startswith("Legea nr. 571/2003"):
            fis.append({"code": "2015" if "227/2015" in a else "2003", "date": r["in_force"], "law": r["law"] or r["author"], "kind": kind(r["law"] or r["author"]) if r["kind"] != "publisher" else "Unexplained",
                        "units": len(re.findall(r"Art\.", a))})
            break
out["fiscal"] = fis
print("fiscal", len(fis), Counter((f["code"], f["kind"]) for f in fis).most_common())

# 6. Omnibus acts ("ordonanțe-trenuleț"): how many acts one amending act changed
reach = defaultdict(set); kd = {}; dt = {}
for r in R:
    if r["kind"] in ("publisher", "correction", None) or r["as_enacted"]: continue
    lab = r["law"] or r["author"]
    for a in r["affecting"]:
        m = re.match(r"(.+?) (Art\.|Anexa|Titlul|Capitolul|Partea|Preambul|Punctul|Alineatul)", a)
        reach[lab].add(m.group(1) if m else a.split(",")[0])
    kd[lab] = kind(lab); dt[lab] = min(dt.get(lab, "9999"), r["in_force"] or "9999")
om = sorted(((len(v), k) for k, v in reach.items()), reverse=True)
out["omnibus"] = [{"act": k, "n": n, "kind": kd[k], "date": dt[k], "title": (L.get(k.lower().replace(" nr. ", "-").replace("/", "-").replace("legea", "legea"), {}) or {}).get("title", "")[:160]} for n, k in om if n >= 2]
print("omnibus top", om[:12], "acts changing 2+", sum(1 for n, _ in om if n >= 2), "10+", sum(1 for n, _ in om if n >= 10))

# 7. Three regimes: every act by the year it was made, and whether it is still in force
reg = Counter()
for a in acts:
    y = int((a.get("from") or "0")[:4] or 0)
    if a.get("year") and a["year"].isdigit(): y = int(a["year"])
    reg[(y, a["kind"], a["status"])] += 1
out["regimes"] = [[y, k, s, n] for (y, k, s), n in sorted(reg.items()) if y]
print("status", Counter(a["status"] for a in acts), "pre-1990", sum(n for (y, k, s), n in reg.items() if y and y < 1990), "pre-1990 in force", sum(n for (y, k, s), n in reg.items() if y and y < 1990 and s == "in force"))
(HERE / "ro_data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
