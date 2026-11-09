"""index/headings/<repo>.parquet: the heading (first non-empty line) and a short head of text for every blob version
of every law file, so 'did provision X of act Y exist on date D?' becomes a join.

python ingest/headings.py [repo ...]   (default: every corpus)
"""
from __future__ import annotations
import sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import duckdb, pyarrow as pa, pyarrow.parquet as pq
from common import CORPUS, INDEX, WORKERS, lower_priority, pins
from textscan import is_law_file, stream


def one(c: dict):
    lower_priority()
    t0 = time.time()
    repo = CORPUS / f"{c['repo']}.git"
    con = duckdb.connect()
    blobs = [b for (b,) in con.sql(f"""select distinct new_blob from '{(INDEX/'changes'/(c['repo']+'.parquet')).as_posix()}'
                                     where left(status,1) <> 'D'""").fetchall()]
    H = {"blob": [], "heading": [], "head": []}
    for sha, text in stream(repo, blobs):
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        H["blob"].append(sha)
        H["heading"].append(lines[0].lstrip("#").strip()[:300] if lines else "")
        H["head"].append(text[:1500])
    (INDEX / "headings").mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table(H), INDEX / "headings" / f"{c['repo']}.parquet", compression="zstd")
    return c["repo"], len(blobs), time.time() - t0


if __name__ == "__main__":
    only = set(sys.argv[1:])
    corp = [c for c in pins()["corpora"] if not only or c["repo"] in only]
    with ProcessPoolExecutor(min(WORKERS, len(corp))) as ex:
        for r in ex.map(one, corp):
            print("%-40s %9d blobs %6.0fs" % r, flush=True)
