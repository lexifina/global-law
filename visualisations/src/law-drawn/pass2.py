"""Second set: Spain's acts and norms, France's Code civil amendments, the published yearly series -> data2_raw.json.
Reads ~/Documents/spain-law and france-law and the global-law analysis11.json; writes only beside this script."""
import json, re, subprocess
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
D = Path.home() / "Documents"
ES, FR = D / "spain-law", D / "france-law"


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=off", *a], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def kind_of(s, an=""):
    if an.startswith("Sentencia") or s.startswith("Sentencia"): return "Court ruling"
    if "Decreto-ley" in s: return "Decree-law"
    if s.startswith("Ley Orgánica"): return "Organic law"
    if s.startswith("Ley "): return "Law"
    if s.startswith("Real Decreto Legislativo") or s.startswith("Decreto Legislativo"): return "Legislative decree"
    if s.startswith("Real Decreto") or s.startswith("Decreto"): return "Royal decree"
    if s.startswith("Orden"): return "Order"
    return "Other"


# Spain: every commit, with the norms it touched
acts, titles = [], {}
ID = re.compile(r"^- (.*) \((BOE-A-\d{4}-\d+)\):", re.M)
for rec in git(ES, "log", "--date=short", "--format=\x1e%ad\x1f%an\x1f%s\x1f%B").split("\x1e")[1:]:
    d, an, s, body = rec.split("\x1f", 3)
    if an == "Lexifina": continue
    n = re.search(r"^Laws-changed:\s*(\d+)", body, re.M)
    ids = []
    for m in ID.finditer(body):
        ids.append(m.group(2)); titles.setdefault(m.group(2), m.group(1)[:200])
    first = "texto inicial" in s
    acts.append([d, int(n.group(1)) if n else len(ids), kind_of(s, an), s.split(":")[0][:110], 1 if first else 0, sorted(set(ids)) if not first else []])
print("spain commits", len(acts))

# Spain: every norm's provisions, rank and year from the path; title from its README heading
norms = defaultdict(lambda: {"prov": 0})
for f in git(ES, "ls-files", "estatal").splitlines():
    parts = f.split("/")
    if len(parts) < 5 or not f.endswith(".md"): continue
    rank, year, nid, fn = parts[1], parts[2], parts[3], parts[-1]
    if fn == "README.md": continue
    n = norms[nid]; n["prov"] += 1; n["rank"] = rank; n["year"] = year
for line in git(ES, "grep", "-m1", "-e", "^# ", "--", "estatal/*/README.md").splitlines():
    path, _, head = line.partition(":")
    nid = path.split("/")[3] if path.count("/") >= 4 else None
    if nid in norms: norms[nid]["title"] = head[2:][:220]
amended = Counter(i for a in acts for i in a[5])
for nid, n in norms.items(): n["amended"] = amended.get(nid, 0)
print("spain norms", len(norms))

# France: every commit touching the Code civil, with the articles it changed
fr = []
for rec in git(FR, "log", "--reverse", "--date=short", "--name-status", "--format=\x1e%ad\x1f%an\x1f%s", "--", "code-civil").split("\x1e")[1:]:
    head, *rows = rec.strip("\n").split("\n")
    d, an, s = head.split("\x1f")
    arts = [r.split("\t")[-1].split("/")[-1][:-3] for r in rows if r and r.split("\t")[-1].startswith("code-civil/art-")]
    fr.append([d, an, s[:200], arts])
fr_articles = sorted(f.split("/")[-1][:-3] for f in git(FR, "ls-files", "code-civil").splitlines() if "/art-" in f)
print("code civil commits", len(fr), "articles", len(fr_articles))

a11 = json.loads((HERE.parent / "glsrc/visualisations/src/analysis11.json").read_text(encoding="utf-8"))
(HERE / "data2_raw.json").write_text(json.dumps({"es_acts": acts, "es_titles": titles, "es_norms": norms, "fr": fr, "fr_articles": fr_articles,
                                                 "years": {k: v["years"] for k, v in a11.items()}}, ensure_ascii=False), encoding="utf-8")
