"""commits/<repo>.parquet: every corpus commit with its own trailers (keys vary by corpus)."""
from __future__ import annotations
import json, re, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pyarrow as pa, pyarrow.parquet as pq
from common import CORPUS, INDEX, WORKERS, git, lower_priority, pins

TR = re.compile(r"^([A-Z][A-Za-z0-9-]{1,40}): ?(.*)$")


def one(c: dict):
    lower_priority()
    out = git("log", "--format=%x1e%H%x1f%aI%x1f%cI%x1f%B", c["sha"], cwd=CORPUS / f"{c['repo']}.git")
    rows = {k: [] for k in ("commit", "author_date", "commit_date", "subject", "trailers")}
    for rec in out.split("\x1e")[1:]:
        sha, ad, cd, body = rec.split("\x1f", 3)
        t: dict[str, list[str]] = {}
        for line in body.splitlines():
            m = TR.match(line.strip())
            if m:
                t.setdefault(m.group(1), []).append(m.group(2).strip()[:2000])
        rows["commit"].append(sha); rows["author_date"].append(ad); rows["commit_date"].append(cd)
        rows["subject"].append(body.split("\n", 1)[0][:500]); rows["trailers"].append(json.dumps(t, ensure_ascii=False))
    t = pa.table(rows).append_column("corpus", pa.array([c["path"]] * len(rows["commit"]), pa.string()))
    (INDEX / "commits").mkdir(parents=True, exist_ok=True)
    pq.write_table(t, INDEX / "commits" / f"{c['repo']}.parquet", compression="zstd")
    return c["repo"], len(rows["commit"])


if __name__ == "__main__":
    t0 = time.time()
    with ProcessPoolExecutor(WORKERS) as ex:
        n = sum(k for _, k in ex.map(one, pins()["corpora"]))
    print(f"{n:,} corpus commits in {time.time()-t0:.0f}s")
