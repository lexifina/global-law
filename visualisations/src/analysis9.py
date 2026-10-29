"""Round 5, global analyses -> analysis9.json
  lag: days from adoption to entry into force, every act in every repo that records both dates
  basis: how Georgia's acts set their start (on publication, a date in the act, ...)
  books: amending acts per year in the whole statute books (Malta, Armenia, Georgia)
"""
import json, re, subprocess, statistics as st
from collections import Counter
from datetime import date
from pathlib import Path

D = Path.home() / "Documents"
REPOS = {c: r for c, (r, _) in json.loads(Path("repos.json").read_text(encoding="utf-8")).items()}
REPOS.update({"mt": "law-in-motion/corpora/malta-law", "am": "armenia-law", "ge": "georgia-law"})
ADOPT = re.compile(r"^(?:Adopted|Enacted|Beschlossen|Made):\s*(\d{4}-\d\d-\d\d)", re.M)
FORCE = re.compile(r"^(?:In-Kraft|In-force|In Kraft):\s*(\d{4}-\d\d-\d\d)", re.M)
GENERIC = re.compile(r"^(Lexifina|Bundeskanzlei|Rechtsdienst|Riigi Teataja|Legimonaco|Service central|PIS RS|Retsinformation|Department of Justice|Legislation Unit|20\d\d edition)")


def git(repo, *a):
    return subprocess.run(["git", "-C", str(D / repo), *a], capture_output=True, text=True, encoding="utf-8").stdout


out = {"lag": {}, "basis": {}, "books": {}}
for code, repo in REPOS.items():
    seen, lags, years, basis = set(), [], Counter(), Counter()
    for chunk in git(repo, "log", "--format=\x1e%an\x1f%B").split("\x1e")[1:]:
        an, _, body = chunk.partition("\x1f")
        if GENERIC.match(an): continue
        kind = re.search(r"^Kind:\s*(\S+)", body, re.M)
        if kind and kind.group(1) in ("consolidated", "unexplained", "documentation", "original"): continue
        f = FORCE.search(body)
        if not f: continue
        key = (an, f.group(1))
        if key in seen: continue
        seen.add(key)
        years[int(f.group(1)[:4])] += 1
        a = ADOPT.search(body)
        if a:
            lags.append((date.fromisoformat(f.group(1)) - date.fromisoformat(a.group(1))).days)
        b = re.search(r"^In-force-basis:\s*(.+)$", body, re.M)
        if b: basis[b.group(1).strip()] += 1
    if lags:
        lags.sort()
        out["lag"][code] = {"n": len(lags), "median": st.median(lags), "q1": lags[len(lags) // 4], "q3": lags[3 * len(lags) // 4],
                            "p05": lags[len(lags) // 20], "p95": lags[19 * len(lags) // 20], "neg": sum(x < 0 for x in lags),
                            "same": sum(x == 0 for x in lags), "within30": sum(0 <= x <= 30 for x in lags),
                            "sample": lags if len(lags) <= 400 else lags[:: max(1, len(lags) // 400)]}
    if basis: out["basis"][code] = dict(basis.most_common())
    if code in ("mt", "am", "ge"): out["books"][code] = dict(sorted(years.items()))
    print(code, "acts", len(seen), "lags", len(lags), out["lag"].get(code, {}).get("median"), dict(list(basis.most_common(4))))
Path("analysis9.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
for c, v in out["books"].items():
    print(c, {y: n for y, n in v.items() if y >= 2015})
