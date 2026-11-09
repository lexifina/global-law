"""Mirror global-law and every pinned corpus as bare repositories under sources/ (read-only use).

Sources: a local global-law clone (GLOBAL_LAW) and its corpus cache when present, otherwise GitHub.

Writes pins.json: the global-law root sha and each corpus's pinned sha, so a run is
reproducible even if repos are force-pushed meanwhile. Never writes to the live repos.
"""
from __future__ import annotations
import configparser, json, os, re, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from common import CACHE_LIVE, CORPUS, GLOBAL, GLOBAL_LIVE, PINS, WORKERS, git, lower_priority


SKIP = re.compile(os.environ.get("LE_SKIP_CORPORA", r"(?i)caselaw|judgment|^united-kingdom|^romania"))


def main() -> None:
    lower_priority()
    t0 = time.time()
    CORPUS.mkdir(parents=True, exist_ok=True)
    origin = os.environ.get("GLOBAL_LAW_ORIGIN") or (str(GLOBAL_LIVE) if (GLOBAL_LIVE / ".git").exists() else "https://github.com/lexifina/global-law")
    if not GLOBAL.exists():
        git("clone", "--bare", "-q", "--single-branch", "--no-tags", origin, str(GLOBAL))
    else:
        git("fetch", "-q", "--no-tags", origin, "+HEAD:refs/heads/main", cwd=GLOBAL)
    head = git("rev-parse", "HEAD", cwd=GLOBAL).strip()
    modules = git("show", f"{head}:.gitmodules", cwd=GLOBAL)
    cfg = configparser.ConfigParser()
    cfg.read_string(modules)
    url = {cfg[s]["path"]: cfg[s]["url"] for s in cfg.sections()}
    gitlinks = {}
    for line in git("ls-tree", "-r", head, cwd=GLOBAL).splitlines():
        meta, path = line.split("\t", 1)
        mode, kind, sha = meta.split()
        if mode == "160000" and not SKIP.search(path):
            gitlinks[path] = sha
    manifest = json.loads(git("show", f"{head}:manifest.json", cwd=GLOBAL))
    manifest = manifest["corpora"] if isinstance(manifest, dict) else manifest
    man = {m["path"]: m for m in manifest}

    def one(path: str) -> dict:
        repo = url[path].rstrip("/").rsplit("/", 1)[1].removesuffix(".git")
        src, dst = CACHE_LIVE / repo, CORPUS / f"{repo}.git"
        src = src if src.exists() else url[path]
        sha = gitlinks[path]
        if dst.exists():
            ok = git("cat-file", "-e", f"{sha}^{{commit}}", cwd=dst, check=False) == ""
            if not ok:
                git("fetch", "-q", "--no-tags", str(src), "+refs/heads/*:refs/heads/*", cwd=dst)
        else:
            git("clone", "--bare", "-q", "--no-tags", str(src), str(dst))  # local: hardlinks objects
        if git("cat-file", "-e", f"{sha}^{{commit}}", cwd=dst, check=False) != "" or \
                subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=dst, capture_output=True).returncode:
            # the local cache is older than the pin: fetch the rest from the corpus's own remote
            git("fetch", "-q", "--no-tags", url[path], "+refs/heads/*:refs/heads/*", cwd=dst)
        git("cat-file", "-e", f"{sha}^{{commit}}", cwd=dst)
        m = man.get(path, {})
        return {"path": path, "repo": repo, "sha": sha, "name": m.get("name"), "code": m.get("code"),
                "language": m.get("language"), "contract": m.get("contract"), "history": m.get("history")}

    with ThreadPoolExecutor(WORKERS) as ex:
        corpora = list(ex.map(one, sorted(gitlinks)))
    PINS.write_text(json.dumps({"global_law": head, "made": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                "corpora": corpora}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"pinned {len(corpora)} corpora at global-law {head[:10]} in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
    main()
