"""Shape stories.json into what the Law in Motion page draws -> story_page.json"""
import json, re, subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

D = Path.home() / "Documents"
s = json.loads(Path("stories.json").read_text(encoding="utf-8"))
de = s["commits"]["de"]
git = lambda repo, *a: subprocess.run(["git", "-C", str(D / repo), *a], capture_output=True, text=True, encoding="utf-8").stdout
dd = date.fromisoformat
out = {}

# 1. Growth of the Basic Law
out["growth"] = [{"date": r["in_force"], "words": r["words"], "law": r["law"], "subject": r["subject"], "n": len(r["files"])} for r in de]

# 2. Votes
votes = []
for r in de:
    m = re.match(r"(\d+) ja, (\d+) nein, (\d+)", r["vote"] or "")
    if m:
        y, n, a = map(int, m.groups())
        votes.append({"date": r["in_force"], "law": r["law"], "subject": r["subject"], "yes": y, "no": n, "abst": a,
                      "share": y / (y + n + a), "initiative": r["initiative"]})
out["votes"] = votes

# 3. Signers, keeping office so the two Gerhard Schröders stay apart
sig = Counter()
for r in de:
    for x in r["signers"]:
        name, _, role = x.partition(",")
        role = re.sub(r"\s*\(.*\)", "", role).strip()
        role = role.replace("Bundesministerin", "Bundesminister").replace("Bundeskanzlerin", "Bundeskanzler").replace("Bundespräsidentin", "Bundespräsident")
        role = {"Bundesminister des Innern": "Interior minister", "Bundesminister der Justiz": "Justice minister", "Bundeskanzler": "Chancellor",
                "Bundeskanzlerin": "Chancellor", "Bundespräsident": "President", "Bundesminister der Finanzen": "Finance minister",
                "Bundesminister der Verteidigung": "Defence minister"}.get(role, role)
        sig[(name.strip(), role)] += 1
out["signers"] = [{"name": n, "role": r, "count": c} for (n, r), c in sig.most_common(40)]

# 4. Enactment to in force, per system
FIELD = {"de": "Beschlossen", "ch": "Adopted", "us": "Enacted", "gb": "Made|Enacted"}
REPO = {"de": "law-in-motion/corpora/grundgesetz", "ch": "swiss-law", "us": "us-code-history", "gb": "uk-law-history"}
lag = defaultdict(list)
for code, repo in REPO.items():
    seen = set()
    for chunk in git(repo, "log", "--format=\x1e%an\x1f%B").split("\x1e")[1:]:
        an, body = chunk.split("\x1f", 1)
        a = re.search(rf"^(?:{FIELD[code]}):\s*(\d{{4}}-\d\d-\d\d)", body, re.M)
        b = re.search(r"^(?:In-Kraft|In-force|In Kraft):\s*(\d{4}-\d\d-\d\d)", body, re.M)
        if not (a and b) or (an, b.group(1)) in seen: continue
        seen.add((an, b.group(1)))
        lag[code].append({"law": an, "enacted": a.group(1), "in_force": b.group(1), "days": (dd(b.group(1)) - dd(a.group(1))).days})
out["lag"] = lag

# 5. Temporary law that snapped back (dates from the US and UK histories)
out["sunsets"] = [
    {"lane": "US · Subchapter V debt limit, 11 U.S.C. § 1182(1)", "c": "us", "spans": [
        {"from": "2020-03-27", "to": "2022-03-27", "label": "$7,500,000", "law": "CARES Act, Pub. L. 116-136"},
        {"from": "2022-06-21", "to": "2024-06-21", "label": "$7,500,000", "law": "Bankruptcy Threshold Adjustment and Technical Corrections Act, Pub. L. 117-151"}],
     "gaps": [{"from": "2022-03-27", "to": "2022-06-21", "label": "lapsed 86 days"}],
     "base": "Otherwise \"debtor\" just means a small business debtor under § 101(51D), whose statutory figure is $2,000,000 before inflation indexing."},
    {"lane": "US · Chapter 13 debt limits, 11 U.S.C. § 109(e)", "c": "us", "spans": [
        {"from": "2022-06-21", "to": "2024-06-21", "label": "one $2,750,000 limit", "law": "Pub. L. 117-151"}],
     "gaps": [], "base": "Before and after: separate limits of $250,000 unsecured and $750,000 secured in the statutory text."},
    {"lane": "UK · 20-week deadline for EHC plans, SEND Regs 2014 reg. 13(3)", "c": "gb", "spans": [
        {"from": "2020-05-01", "to": "2020-09-25", "label": "\"(a) to (e)\"", "law": "S.I. 2020/471"}],
     "gaps": [], "base": "The exception list ran \"(a) to (d)\" before and after. The letter (e) added coronavirus as a reason the deadline could be missed."},
    {"lane": "UK · Children and Families Act 2014 s. 42, under the Coronavirus Act", "c": "gb", "spans": [
        {"from": "2020-03-25", "to": "2021-12-09", "label": "notice power available", "law": "Coronavirus Act 2020; ended early by S.I. 2021/1399"}],
     "gaps": [], "base": "The section's words never changed. The Coronavirus Act let the Secretary of State relax the duty by notice until the early-expiry regulations ended that power."},
]
out["cares"] = [{"date": e["in_force"], "law": e["law"], "files": e["files"]} for e in s["commits"]["us"] if "116-136" in e["law"]]

# 6. Omnibus reach in the US Code
om = []
for r in s["commits"]["us"]:
    if r["law"].startswith("2017 edition"): continue
    titles = sorted({int(f.split("/")[0].split("-")[1]) for f in r["files"]})
    om.append({"law": r["law"], "date": r["in_force"], "titles": titles, "sections": len(r["files"])})
agg = defaultdict(lambda: {"titles": set(), "sections": 0, "dates": []})
for o in om:
    k = re.sub(r"\s*\(.*", "", o["law"]); a = agg[o["law"]]
    a["titles"] |= set(o["titles"]); a["sections"] += o["sections"]; a["dates"].append(o["date"])
out["omnibus"] = sorted(({"law": k, "titles": sorted(v["titles"]), "sections": v["sections"], "dates": sorted(set(v["dates"]))} for k, v in agg.items()),
                        key=lambda x: (-len(x["titles"]), -x["sections"]))

# 7. Most-rewritten articles of the Basic Law, with words at birth and today
per = defaultdict(list)
for r in de[1:]:
    for f in r["files"]:
        per[f].append(r["in_force"][:4])
head = de[-1]["sha"]
def wc(rev, f):
    t = git("law-in-motion/corpora/grundgesetz", "show", f"{rev}:{f}")
    return len(re.findall(r"\w+", re.sub(r"^#.*$", "", t, flags=re.M))) if t else 0
hot = sorted(per.items(), key=lambda kv: -len(kv[1]))[:16]
first_rev = {}
for f, _ in hot:
    first_rev[f] = git("law-in-motion/corpora/grundgesetz", "log", "--reverse", "--format=%h", "--", f).split()[0]
out["hot"] = [{"art": "Art. " + f.split("/")[1][:-3].lstrip("0"), "years": ys, "born": git("law-in-motion/corpora/grundgesetz", "log", "--reverse", "--format=%an", "--", f).splitlines()[0],
               "w0": wc(first_rev[f], f), "w1": wc(head, f)} for f, ys in hot]
Path("story_page.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
for k in ("lag",):
    for c, v in out[k].items():
        ds = sorted(x["days"] for x in v); print(c, len(ds), "median", ds[len(ds) // 2], "min", ds[0], "max", ds[-1])
print("signers", out["signers"][:8])
print("omni", [(o["law"][:50], o["titles"], o["sections"]) for o in out["omnibus"][:6]])
print("hot", [(h["art"], len(h["years"]), h["w0"], h["w1"], h["born"]) for h in out["hot"][:10]])
print("cares", out["cares"])
