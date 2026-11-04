"""Municipal ordinances (text/*-city-law) -> copy.json: articles that appear, word for word after normalising, in two or more cities.
Normalising lowercases, strips accents, digits and punctuation, so renumbered or re-dated copies still match. Short articles
(under 25 words) are left out because they are mostly boilerplate ("Comuníquese, regístrese...")."""
import csv, hashlib, json, re, subprocess, unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
MIN_WORDS = 25


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"^#.*$", " ", s, flags=re.M)
    s = re.sub(r"^\s*(articulo|art\.?|artigo)\s*[\w°ºo.-]*\s*[:.-]?", " ", s)
    s = re.sub(r"[^a-z]+", " ", s)
    return s.split()


cities, arts, sample = {}, defaultdict(list), {}    # hash -> [(city, ordinance, enacted, words)]; hash -> text
for repo in sorted((HERE / "text").iterdir()):
    jf = repo / "jurisdiction.json"
    if not jf.exists(): continue
    j = json.loads(jf.read_text(encoding="utf-8"))
    country = repo.name.split("-")[0]
    laws = {}
    lf = repo / "data" / "laws.csv"
    if lf.exists():
        with lf.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh): laws[row["key"]] = row
    # Read every article from git's object store in one stream: opening 200,000 small files one by one is far slower on Windows
    tree = subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=off", "ls-tree", "-r", "HEAD"], capture_output=True, text=True, encoding="utf-8").stdout
    files = []
    for line in tree.splitlines():
        meta_, path = line.split("\t", 1)
        parts = path.split("/")
        if len(parts) != 2 or not path.endswith(".md") or parts[0] in ("data", "tools") or parts[1] in ("README.md", "encabezado.md"): continue
        files.append((meta_.split()[2], parts[0]))
    proc = subprocess.Popen(["git", "-C", str(repo), "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    blobs = proc.communicate("\n".join(sha for sha, _ in files).encode())[0]
    pos, texts = 0, []
    for _ in files:
        nl = blobs.index(b"\n", pos); size = int(blobs[pos:nl].split()[2]); texts.append(blobs[nl + 1:nl + 1 + size].decode("utf-8", "replace")); pos = nl + 2 + size
    n_ord = len({o for _, o in files})
    for (sha, o), txt in zip(files, texts):
        meta = laws.get(o, {})
        w = norm(txt)
        if len(w) < MIN_WORDS: continue
        h = hashlib.sha1(" ".join(w).encode()).hexdigest()[:16]
        sample.setdefault(h, re.sub(r"\s+", " ", txt)[:600])
        arts[h].append((repo.name, o, meta.get("enacted") or meta.get("published") or "", len(w), meta.get("title", "")[:140]))
    cities[repo.name] = {"name": j.get("name", repo.name), "country": country, "parent": j.get("parent", ""), "ordinances": n_ord}

shared = {h: v for h, v in arts.items() if len({c for c, *_ in v}) >= 2}
edges = defaultdict(int)
for h, v in shared.items():
    cs = sorted({c for c, *_ in v})
    for i, a in enumerate(cs):
        for b in cs[i + 1:]: edges[(a, b)] += 1
# Group shared articles back into ordinances that were copied: same pair of ordinances sharing several articles
clusters = defaultdict(set)
for h, v in shared.items():
    key = tuple(sorted({(c, o) for c, o, *_ in v}))
    clusters[key].add(h)
copies = []
for key, hs in clusters.items():
    rows = [r for h in hs for r in shared[h]]
    first = {}
    for c, o, dt, w, t in rows:
        if (c, o) not in first or (dt and dt < first[(c, o)][0]): first[(c, o)] = (dt, t)
    copies.append({"members": [[c, o, first[(c, o)][0], first[(c, o)][1]] for c, o in key], "articles": len(hs),
                   "words": sum(shared[h][0][3] for h in hs)})
copies.sort(key=lambda x: (-len({m[0] for m in x["members"]}), -x["words"]))
out = {"cities": cities, "edges": [[a, b, n] for (a, b), n in sorted(edges.items(), key=lambda kv: -kv[1])], "copies": copies[:400],
       "n_articles": sum(len(v) for v in arts.values()), "n_shared": len(shared),
       "shared": [{"h": h, "cities": sorted({c for c, *_ in v}), "dates": sorted(d for _, _, d, *_ in v if d), "text": sample[h], "titles": sorted({r[4] for r in v if r[4]})[:12]} for h, v in shared.items()]}
(HERE / "copy.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(len(cities), "cities;", out["n_articles"], "long articles;", len(shared), "shared by 2+ cities;", len(edges), "city pairs")
for c in copies[:15]:
    print(len({m[0] for m in c["members"]}), "cities", c["articles"], "articles |", " / ".join(f"{m[0].replace('-city-law','')}:{m[2]}" for m in c["members"][:6]), "|", c["members"][0][3][:90])
