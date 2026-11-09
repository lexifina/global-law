"""Build index/: one uniform table set over every pinned corpus.

root.parquet   one row per global-law root commit: corpus, corpus_commit, law, in_force, kind
changes/<repo>.parquet  one row per file change in a corpus commit (git log --raw -M)
Text is not copied; blobs are read on demand with cat-file --batch.
"""
from __future__ import annotations
import re, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pyarrow as pa, pyarrow.parquet as pq
from common import CORPUS, GLOBAL, INDEX, WORKERS, git, lower_priority, pins

TR = re.compile(r"^([A-Z][A-Za-z-]+): ?(.*)$")


def root_table(head: str) -> pa.Table:
    out = git("log", "--format=%x1e%H%x1f%B", head, cwd=GLOBAL)
    rows = {k: [] for k in ("root", "corpus", "corpus_commit", "law", "in_force", "kind", "subject")}
    for rec in out.split("\x1e")[1:]:
        sha, body = rec.split("\x1f", 1)
        t = {}
        for line in body.splitlines():
            m = TR.match(line)
            if m and m.group(1) not in t:
                t[m.group(1)] = m.group(2).strip()
        if "Corpus-commit" not in t:
            continue
        rows["root"].append(sha); rows["corpus"].append(t.get("Corpus"))
        rows["corpus_commit"].append(t["Corpus-commit"]); rows["law"].append(t.get("Law"))
        rows["in_force"].append(t.get("In-force")); rows["kind"].append(t.get("Kind"))
        rows["subject"].append(body.split("\n", 1)[0][:300])
    return pa.table(rows)


def corpus_changes(c: dict) -> tuple[str, int, float]:
    lower_priority()
    t0 = time.time()
    repo = CORPUS / f"{c['repo']}.git"
    out = git("log", "--raw", "--no-abbrev", "-M", "-z", "--format=%x1e%H%x1f%P%x1f%aI%x1f%s",
              c["sha"], cwd=repo, binary=True).decode("utf-8", errors="replace")
    cols = {k: [] for k in ("commit", "author_date", "status", "old_blob", "new_blob", "old_path", "path")}
    for rec in out.split("\x1e")[1:]:
        head, _, raw = rec.partition("\n")
        parts = head.split("\x1f")
        sha, date = parts[0], parts[2]
        toks = raw.lstrip("\n").split("\x00")
        i = 0
        while i < len(toks):
            tok = toks[i].lstrip("\n")
            if not tok.startswith(":"):
                i += 1
                continue
            f = tok[1:].split()
            st = f[4]
            if st[0] in "RC":
                old, new = toks[i + 1], toks[i + 2]; i += 3
            else:
                old = new = toks[i + 1]; i += 2
            cols["commit"].append(sha); cols["author_date"].append(date); cols["status"].append(st)
            cols["old_blob"].append(f[2]); cols["new_blob"].append(f[3])
            cols["old_path"].append(old); cols["path"].append(new)
    t = pa.table(cols).append_column("corpus", pa.array([c["path"]] * len(cols["commit"]), pa.string()))
    (INDEX / "changes").mkdir(parents=True, exist_ok=True)
    pq.write_table(t, INDEX / "changes" / f"{c['repo']}.parquet", compression="zstd")
    return c["repo"], len(cols["commit"]), time.time() - t0


def main() -> None:
    lower_priority()
    p = pins(); INDEX.mkdir(exist_ok=True)
    t0 = time.time()
    pq.write_table(root_table(p["global_law"]), INDEX / "root.parquet", compression="zstd")
    print(f"root history parsed in {time.time()-t0:.0f}s", flush=True)
    corp = sorted(p["corpora"], key=lambda c: -(CORPUS / f"{c['repo']}.git").stat().st_size)
    with ProcessPoolExecutor(WORKERS) as ex:
        for repo, n, s in ex.map(corpus_changes, corp):
            print(f"{repo:45s} {n:>9,} changes {s:6.1f}s", flush=True)
    print(f"done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
