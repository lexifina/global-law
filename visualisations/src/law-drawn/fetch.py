"""Metadata-only bare clones (commits, no trees or files) of every corpus in global-law's .gitmodules -> clones/<repo>.git.
An existing clone is fetched instead, so the script can be rerun to refresh. Writes corpora.json: path, repo, commit count."""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
CL = HERE / "clones"


def modules():
    out = subprocess.run(["git", "config", "-f", str(HERE / "gitmodules.txt"), "--get-regexp", r"\.(path|url)$"], capture_output=True, text=True).stdout
    m = {}
    for line in out.splitlines():
        k, v = line.split(" ", 1)
        name, field = k.rsplit(".", 1)
        m.setdefault(name, {})[field] = v
    return [(v["path"], v["url"].rstrip("/").removesuffix(".git").split("/")[-1], v["url"]) for v in m.values() if "path" in v and "url" in v]


def one(item):
    path, repo, url = item
    d = CL / f"{repo}.git"
    cmd = ["git", "-C", str(d), "fetch", "-q", "origin", "+refs/heads/*:refs/heads/*"] if d.exists() else \
          ["git", "clone", "-q", "--bare", "--filter=tree:0", url, str(d)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    n = subprocess.run(["git", "-C", str(d), "rev-list", "--count", "HEAD"], capture_output=True, text=True).stdout.strip()
    print(f"{repo:50s} {n or 'FAILED ' + r.stderr.strip()[:80]}", flush=True)
    return {"path": path, "repo": repo, "commits": int(n) if n.isdigit() else 0}


if __name__ == "__main__":
    items = modules()
    with ThreadPoolExecutor(int(sys.argv[1]) if len(sys.argv) > 1 else 8) as ex:
        res = list(ex.map(one, items))
    (HERE / "corpora.json").write_text(json.dumps(res, indent=0), encoding="utf-8")
    print(len(res), "corpora;", sum(1 for r in res if r["commits"] > 2), "with history")
