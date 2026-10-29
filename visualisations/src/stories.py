"""Real-data stories from the four law histories -> stories.json (git only, no model calls)."""
import json, re, subprocess
from collections import Counter, defaultdict
from pathlib import Path

D = Path.home() / "Documents"
REPOS = {"de": ("law-in-motion/corpora/grundgesetz", r"^artikel/"), "ch": ("swiss-law", r"^(101|235.1|281.1)/art-"),
         "gb": ("uk-law-history", r"^(ukpga|uksi)/"), "us": ("us-code-history", r"^title-\d+/")}
DOC = {"Lexifina", "Lexifina Watch"}


def git(repo, *a, inp=None):
    return subprocess.run(["git", "-C", str(D / repo), *a], capture_output=True, input=inp, text=True, encoding="utf-8").stdout


class Blobs:
    def __init__(self, repo):
        self.p = subprocess.Popen(["git", "-C", str(D / repo), "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.cache = {}

    def text(self, sha):
        if sha not in self.cache:
            self.p.stdin.write((sha + "\n").encode()); self.p.stdin.flush()
            head = self.p.stdout.readline().split()
            n = int(head[2]); body = self.p.stdout.read(n); self.p.stdout.read(1)
            self.cache[sha] = body.decode("utf-8", "ignore")
        return self.cache[sha]


def words(t):
    t = re.sub(r"^---.*?---", "", t, flags=re.S)
    return len(re.findall(r"\w+", t))


def field(body, *names):
    for n in names:
        m = re.search(rf"^{n}:\s*(.+)$", body, re.M)
        if m: return m.group(1).strip()
    return None


def day(s):
    m = re.search(r"\d{4}-\d\d-\d\d", s or "")
    return m.group(0) if m else None


out = {"commits": {}, "growth": {}}
for code, (repo, pref) in REPOS.items():
    pat = re.compile(pref)
    blobs = Blobs(repo)
    log = git(repo, "log", "--reverse", "--format=\x1e%H\x1f%an\x1f%B", *(["--", "101", "235.1", "281.1"] if repo == "swiss-law" else []))
    rows = []
    for chunk in log.split("\x1e")[1:]:
        sha, author, body = chunk.split("\x1f", 2)
        if author in DOC: continue
        files = [l.split("\t", 1)[1] for l in git(repo, "diff-tree", "--root", "--no-commit-id", "-r", "--name-status", sha).splitlines() if "\t" in l]
        files = [f.split("\t")[-1] for f in files if pat.match(f.split("\t")[-1])]
        if not files: continue
        tree = {l.split("\t")[1]: l.split()[2] for l in git(repo, "ls-tree", "-r", sha).splitlines() if pat.match(l.split("\t")[1])}
        total = sum(words(blobs.text(b)) for b in tree.values())
        r = {"sha": sha[:10], "law": author, "files": files, "words": total, "provisions": len(tree),
             "in_force": day(field(body, "In-Kraft", "In-force", "In Kraft")),
             "enacted": day(field(body, "Beschlossen", "Enacted", "Made")),
             "signed": day(field(body, "Ausgefertigt")), "published": day(field(body, "Verkündet", "Veröffentlicht")),
             "vote": field(body, "Abstimmung"), "initiative": field(body, "Initiative"),
             "signers": re.findall(r"^Unterzeichnet:\s*(.+)$", body, re.M), "subject": body.splitlines()[0][:160]}
        rows.append(r)
    out["commits"][code] = rows
    print(code, len(rows), "commits; words", rows[0]["words"], "->", rows[-1]["words"])

# Dollar figures in the US Bankruptcy Code, version by version
repo = "us-code-history"; blobs = Blobs(repo)
law_commits = [r for r in out["commits"]["us"]]
money = defaultdict(list)  # file -> [(in_force, law, amounts)]
for r in law_commits:
    for f in r["files"]:
        if not f.startswith("title-11/"): continue
        sha_blob = git(repo, "rev-parse", f"{r['sha']}:{f}").strip()
        prev = git(repo, "rev-parse", f"{r['sha']}~1:{f}").strip() if git(repo, "cat-file", "-t", f"{r['sha']}~1:{f}").strip() == "blob" else None
        amt = lambda s: Counter(re.findall(r"\$[\d,]{4,}", blobs.text(s))) if s else Counter()
        a0, a1 = amt(prev), amt(sha_blob)
        if a0 != a1:
            money[f].append({"date": r["in_force"], "law": r["law"], "before": sorted((a0 - a1).elements()), "after": sorted((a1 - a0).elements())})
out["money"] = money

# Text of the subchapter V debt limit (11 USC 1182(1)) at every version
hist = []
for line in git(repo, "log", "--reverse", "--format=%H\x1f%an", "--", "title-11/1182.md").splitlines():
    sha, an = line.split("\x1f")
    t = git(repo, "show", f"{sha}:title-11/1182.md")
    m = re.search(r"aggregate noncontingent liquidated[^$]*\$([\d,]+)", t)
    inf = re.search(r"In-force:\s*(\S+)", git(repo, "log", "-1", "--format=%B", sha))
    hist.append({"law": an, "date": inf.group(1) if inf else None, "limit": m.group(1) if m else None})
out["subv"] = hist
Path("stories.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print("money files", {k: len(v) for k, v in money.items()})
print("subv", hist)
