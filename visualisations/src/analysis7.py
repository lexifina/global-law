"""Round 4 analyses -> analysis7.json
  activity: provisions changed per year by amending acts, per jurisdiction (Malta: units)
  coamend: Basic Law articles rewritten by the same act, for the most-amended articles
"""
import json, re, subprocess
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

D = Path.home() / "Documents"
REPOS = json.loads(Path("repos.json").read_text(encoding="utf-8"))
GENERIC = re.compile(r"^(Lexifina|Bundeskanzlei|Rechtsdienst|Riigi Teataja|Legimonaco|Service central|PIS RS|Retsinformation|Department of Justice|20\d\d edition|Grundgesetz \(1949\))")


def git(p, *a):
    return subprocess.run(["git", "-C", str(p), *a], capture_output=True, text=True, encoding="utf-8").stdout


activity = {}
acts_seen = {}
for code, (repo, pat) in REPOS.items():
    rx = re.compile(pat); per = Counter(); first = True
    for chunk in git(D / repo, "log", "--reverse", "--format=\x1e%an\x1f%B\x1d", "--name-status").split("\x1e")[1:]:
        head, _, names = chunk.partition("\x1d")
        an, body = head.split("\x1f", 1)
        rows = [l.split("\t") for l in names.split("\n") if "\t" in l]
        # Count rewritten or repealed provisions only; a newly added law is a birth, not an amendment
        n = sum(1 for r in rows if r[0][0] in "MD" and rx.match(r[-1].strip()) and r[-1].strip().endswith(".md"))
        born = any(r[0][0] == "A" and rx.match(r[-1].strip()) for r in rows)
        if first and (n or born): first = False; continue
        if not n: continue
        if GENERIC.match(an) or "ispravak" in an: continue
        m = re.search(r"^(?:In-Kraft|In-force|In Kraft):\s*(\d{4})", body, re.M)
        if m:
            per[int(m.group(1))] += n
            acts_seen.setdefault(code, set()).add((an, int(m.group(1))))
    if per: activity[code] = dict(sorted(per.items()))
mt = Counter(); mt_acts = set()
for chunk in git(D / "law-in-motion/corpora/malta-law", "log", "--format=\x1e%an\x1f%B").split("\x1e")[1:]:
    an, _, chunk = chunk.partition("\x1f")
    if re.search(r"^Kind:\s*amendment", chunk, re.M):
        y = re.search(r"^In-force:\s*(\d{4})", chunk, re.M); u = re.search(r"(\d+) unit", chunk)
        if y and u: mt[int(y.group(1))] += int(u.group(1))
        if y: mt_acts.add((an, int(y.group(1))))
activity["mt"] = dict(sorted(mt.items()))
acts_seen["mt"] = mt_acts
# Amending acts per year (an act counts once per in-force year)
acts_per_year = {c: dict(sorted(Counter(y for _, y in s).items())) for c, s in acts_seen.items()}

# Co-amendment among the Basic Law's most-amended articles
GG = D / REPOS["de"][0]
acts = []
for chunk in git(GG, "log", "--format=\x1e%an", "--name-only").split("\x1e")[1:]:
    an, *files = chunk.strip().split("\n")
    if GENERIC.match(an): continue
    arts = sorted({re.match(r"artikel/0*(\w+)\.md$", f.strip()).group(1) for f in files if re.match(r"artikel/0*(\w+)\.md$", f.strip())})
    if arts: acts.append(arts)
deg = Counter(a for arts in acts for a in arts)
top = [a for a, _ in deg.most_common(30)]
key = lambda a: (int(re.match(r"\d+", a).group(0)) if re.match(r"\d+", a) else 999, a)
top.sort(key=key)
pairs = Counter()
for arts in acts:
    for a, b in combinations([x for x in arts if x in top], 2):
        pairs[(a, b)] += 1
out = {"activity": activity, "acts_per_year": acts_per_year, "coamend": {"arts": top, "deg": {a: deg[a] for a in top}, "pairs": [[a, b, n] for (a, b), n in pairs.items()]}}
Path("analysis7.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
for c, v in activity.items():
    yrs = sorted(v)
    if not yrs: continue
    print(c, yrs[0], yrs[-1], "total", sum(v.values()), "peak", max(v, key=v.get), v[max(v, key=v.get)])
print("top pairs", sorted(pairs.items(), key=lambda x: -x[1])[:10])
