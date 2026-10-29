"""Commit-metadata analyses across every repo -> analysis3.json
  calendar: which day law takes effect (1 January, the 1st of a month, other)
  malta: Malta's whole statute book, amendments per month by instrument type
"""
import json, re, subprocess
from collections import Counter, defaultdict
from pathlib import Path

D = Path.home() / "Documents"
REPOS = {"de": "law-in-motion/corpora/grundgesetz", "ch": "swiss-law", "gb": "uk-law-history", "us": "us-code-history", "ee": "estonia-law",
         "li": "liechtenstein-law", "lu": "luxembourg-law", "mc": "monaco-law", "sk": "slovakia-law", "si": "slovenia-law", "fi": "finland-law", "hr": "croatia-law", "gi": "gibraltar-law", "dk": "denmark-law", "hk": "hong-kong-law", "kg": "kyrgyzstan-law", "it": "italy-law", "pt": "portugal-law", "mg": "madagascar-law", "rw": "rwanda-law", "mt": "law-in-motion/corpora/malta-law"}
GENERIC = re.compile(r"^(Lexifina|Lexifina Watch|Bundeskanzlei|Rechtsdienst|Riigi Teataja|Legimonaco|Legislation Unit|Retsinformation|Department of Justice|Service central|PIS RS|20\d\d edition)")


def git(repo, *a):
    return subprocess.run(["git", "-C", str(D / repo), *a], capture_output=True, text=True, encoding="utf-8").stdout


out = {"calendar": {}, "heads": {}}
mt_rows = []
for code, repo in REPOS.items():
    out["heads"][code] = git(repo, "rev-parse", "--short", "HEAD").strip()
    seen = set(); days = Counter(); n = 0
    for chunk in git(repo, "log", "--format=\x1e%an\x1f%B").split("\x1e")[1:]:
        an, b = chunk.split("\x1f", 1)
        if GENERIC.match(an): continue
        kind = re.search(r"^Kind:\s*(\S+)", b, re.M)
        if kind and kind.group(1) in ("consolidated", "unexplained"): continue
        m = re.search(r"^(?:In-Kraft|In-force|In Kraft):\s*(\d{4}-\d\d-\d\d)", b, re.M)
        if not m: continue
        d = m.group(1)
        if (an, d) in seen: continue
        seen.add((an, d)); n += 1
        days["jan1" if d[5:] == "01-01" else "first" if d[8:] == "01" else "other"] += 1
        if code == "mt":
            u = re.search(r"to (\d+) law\(s\), (\d+) unit", b)
            typ = "Act" if an.startswith("Act") else "Legal Notice" if an.startswith("L.N.") else "Other"
            mt_rows.append({"date": d, "law": an[:60], "type": typ, "laws": int(u.group(1)) if u else 1, "units": int(u.group(2)) if u else 0})
    out["calendar"][code] = {"n": n, **days}
by = defaultdict(lambda: Counter())
for r in mt_rows:
    if "2016-01" <= r["date"][:7] <= "2026-10":
        by[r["date"][:7]][r["type"]] += 1
        by[r["date"][:7]]["units"] += r["units"]
out["malta"] = {"months": [{"m": k, **v} for k, v in sorted(by.items())], "n": len(mt_rows),
                "top": sorted(mt_rows, key=lambda r: -r["units"])[:8]}
Path("analysis3.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
for c, v in out["calendar"].items():
    print(c, v["n"], {k: round(v.get(k, 0) / v["n"], 2) for k in ("jan1", "first", "other")} if v["n"] else "")
mm = out["malta"]["months"]
print("malta rows", len(mt_rows), "months", len(mm), "types", Counter(r["type"] for r in mt_rows))
print("busiest", sorted(mm, key=lambda x: -(x.get("Act", 0) + x.get("Legal Notice", 0)))[:6])
print("per year", {y: sum(x.get("Act", 0) + x.get("Legal Notice", 0) for x in mm if x["m"].startswith(y)) for y in map(str, range(2016, 2027))})
print("top", [(r["law"], r["date"], r["units"]) for r in out["malta"]["top"][:5]])
