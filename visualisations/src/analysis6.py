"""Round 3 analyses -> analysis6.json
  hubs: Basic Law articles by how often other articles cite them (today) against how often they were amended
  size: how many provisions each amending act touches, per jurisdiction
"""
import json, re, subprocess, statistics as st
from collections import Counter
from pathlib import Path

D = Path.home() / "Documents"
GG = D / "law-in-motion/corpora/grundgesetz"


def git(p, *a):
    return subprocess.run(["git", "-C", str(p), *a], capture_output=True, text=True, encoding="utf-8").stdout


# Hubs: in-degree of cross-references between articles, at HEAD
cites = Counter()
arts = {}
for f in sorted((GG / "artikel").glob("*.md")):
    a = f.stem.lstrip("0") or f.stem
    arts[a] = f
for a, f in arts.items():
    t = f.read_text(encoding="utf-8", errors="ignore")
    t = re.sub(r"^#.*$", "", t, flags=re.M)
    targets = set()
    for m in re.finditer(r"Artikel[ns]?\s+((?:\d+[a-z]?(?:\s*(?:,|und|bis|oder|sowie)\s*)?)+)", t):
        targets |= set(re.findall(r"\d+[a-z]?", m.group(1)))
    for b in targets:
        if b != a and b in arts: cites[b] += 1
amended = Counter()
for line in git(GG, "log", "--format=\x1e%an", "--name-only").split("\x1e")[1:]:
    an, *files = line.strip().split("\n")
    if an.startswith(("Grundgesetz (1949)", "Lexifina")): continue
    for f in files:
        m = re.match(r"artikel/0*(\w+)\.md$", f.strip())
        if m: amended[m.group(1)] += 1
hubs = [{"art": a, "cited": cites[a], "amended": amended[a]} for a in arts if a not in ("praeambel", "eingangsformel")]
xs = [h["cited"] for h in hubs]; ys = [h["amended"] for h in hubs]
def rank(v):
    s = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v)
    for k, i in enumerate(s): r[i] = k
    return r
rx, ry = rank(xs), rank(ys)
n = len(xs); mx, my = st.mean(rx), st.mean(ry)
rho = sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** .5
cited = [h for h in hubs if h["cited"] >= 3]; uncited = [h for h in hubs if h["cited"] == 0]
print("articles", n, "spearman", round(rho, 3), "mean amended: cited>=3", round(st.mean(h["amended"] for h in cited), 2), len(cited),
      "| uncited", round(st.mean(h["amended"] for h in uncited), 2), len(uncited))
print("top cited", sorted(hubs, key=lambda h: -h["cited"])[:10])

# Size of amending acts: provisions touched per act, per jurisdiction
REPOS = {"de": ("law-in-motion/corpora/grundgesetz", r"^artikel/"), "ch": ("swiss-law", r"^(101|235.1|281.1)/art-"), "gb": ("uk-law-history", r"^(ukpga|uksi)/"),
         "us": ("us-code-history", r"^title-\d+/"), "ee": ("estonia-law", r"^(ps|rkvs|iks)/(?!README)"), "li": ("liechtenstein-law", r"^(lv|vrg|stghg)/(?!README)"),
         "lu": ("luxembourg-law", r"^(constitution|loi)/.+/(?!README)[^/]+\.md$"), "mc": ("monaco-law", r"^(constitution|loi-1362)/(?!README)"),
         "sk": ("slovakia-law", r"^(ustava|volebny-zakon)/(?!README)"), "si": ("slovenia-law", r"^(urs|zvdz)/(?!README)"),
         "fi": ("finland-law", r"^perustuslaki/(?!README)"), "hr": ("croatia-law", r"^ustav/(?!README)"), "gi": ("gibraltar-law", r"^(constitution|stamp-duties)/(?!README|arrangement)"),
         "dk": ("denmark-law", r"^(grundloven|skatteforvaltningsloven)/(?!README)"), "hk": ("hong-kong-law", r"^cap-[0-9]+/(?!README)"), "kg": ("kyrgyzstan-law", r"^konstitutsiya-2021/(?!README)"), "it": ("italy-law", r"^costituzione/(?!README|allegati)"), "pt": ("portugal-law", r"^constituicao/(?!README)"), "mg": ("madagascar-law", r"^constitution/(?!README)"), "rw": ("rwanda-law", r"^(constitution|law-2020-017)/(?!README)")}
GENERIC = re.compile(r"^(Lexifina|Bundeskanzlei|Rechtsdienst|Riigi Teataja|Legimonaco|Retsinformation|Department of Justice|Service central|PIS RS|20\d\d edition|Grundgesetz \(1949\))")
size = {}
for code, (repo, pat) in REPOS.items():
    rx2 = re.compile(pat); per = Counter(); first = None
    log = git(D / repo, "log", "--reverse", "--format=\x1e%an", "--name-only").split("\x1e")[1:]
    for k, chunk in enumerate(log):
        an, *files = chunk.strip().split("\n")
        n_files = sum(1 for f in files if rx2.match(f.strip()) and f.strip().endswith(".md"))
        if not n_files: continue
        if first is None: first = an; continue  # the commit that loaded the law
        if GENERIC.match(an): continue
        per[an] += n_files
    if per: size[code] = sorted(per.values())
# Malta: units per amending instrument from the commit body
mt = []
for chunk in git(D / "law-in-motion/corpora/malta-law", "log", "--format=\x1e%B").split("\x1e")[1:]:
    if re.search(r"^Kind:\s*amendment", chunk, re.M):
        u = re.search(r"(\d+) unit", chunk)
        if u: mt.append(int(u.group(1)))
size["mt"] = sorted(mt)
size = {c: v for c, v in size.items() if v}
for c, v in size.items():
    print(c, len(v), "median", st.median(v), "p90", v[int(.9 * (len(v) - 1))], "max", v[-1], "share one", round(sum(x == 1 for x in v) / len(v), 2))
Path("analysis6.json").write_text(json.dumps({"hubs": hubs, "rho": rho, "size": size}, ensure_ascii=False), encoding="utf-8")
