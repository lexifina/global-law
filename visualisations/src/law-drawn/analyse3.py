"""Every corpus's commit trailers (clones/*.git) -> acts3.json: per corpus, dated acts by in-force date.
Same act rules as global-law's analysis11.py: one act per (author, in-force date); generic and snapshot commits skipped."""
import json, re, subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
FORCE = re.compile(r"^(?:In-Kraft|In-force|In Kraft):\s*(\d{4}-\d\d-\d\d)", re.M)
ADOPT = re.compile(r"^(?:Adopted|Enacted|Beschlossen|Made|Signed|Promulgated):\s*(\d{4}-\d\d-\d\d)", re.M)
SKIP_KIND = re.compile(r"^Kind:\s*(consolidated|unexplained|documentation|original|editorial)", re.M | re.I)
GENERIC = re.compile(r"^(Lexifina|Bundeskanzlei|Rechtsdienst|Riigi Teataja|Legimonaco|Service central|PIS RS|Retsinformation|Department of Justice|"
                     r"Legislation Unit|20\d\d edition|Grundgesetz \(1949\)|Diário da República \(INCM\))")
corpora = json.loads((HERE / "corpora.json").read_text(encoding="utf-8"))


def level(path):
    country, region, _ = path.split("/")
    return "national" if region == "national" else "city" if region.endswith("-city") else "region"


def read(c):
    d = HERE / "clones" / f"{c['repo']}.git"
    if not d.exists() or c["commits"] < 3: return None
    proc = subprocess.Popen(["git", "-C", str(d), "log", "--format=\x1e%an\x1f%B"], stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    seen, dates, lags = set(), Counter(), []
    buf = []
    def take(chunk):
        an, _, b = chunk.partition("\x1f")
        if GENERIC.match(an) or SKIP_KIND.search(b): return
        f = FORCE.search(b)
        if not f or (an, f.group(1)) in seen: return
        seen.add((an, f.group(1)))
        if not ("1800" <= f.group(1)[:4] <= "2027"): return
        dates[f.group(1)] += 1
        a = ADOPT.search(b)
        if a:
            try:
                from datetime import date
                lags.append((date.fromisoformat(f.group(1)) - date.fromisoformat(a.group(1))).days)
            except ValueError: pass
    for line in proc.stdout:
        if line.startswith("\x1e"):
            if buf: take("".join(buf))
            buf = [line[1:]]
        else: buf.append(line)
    if buf: take("".join(buf))
    proc.wait()
    if not dates: return None
    lags.sort()
    country, region, _ = c["path"].split("/")
    return {"path": c["path"], "repo": c["repo"], "country": country, "region": region, "level": level(c["path"]), "commits": c["commits"],
            "acts": sum(dates.values()), "dates": dict(sorted(dates.items())), "lag_median": lags[len(lags) // 2] if len(lags) >= 5 else None}


with ThreadPoolExecutor(8) as ex:
    res = [r for r in ex.map(read, corpora) if r]
(HERE / "acts3.json").write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
lv = Counter(r["level"] for r in res)
print(len(res), "corpora with dated acts of", len(corpora), dict(lv), "acts", sum(r["acts"] for r in res))
print("countries", len({r["country"] for r in res}))
for l in ("national", "region", "city"):
    print(l, sum(r["acts"] for r in res if r["level"] == l))
