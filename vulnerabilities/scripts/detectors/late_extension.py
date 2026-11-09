"""late_extension: a time-limited rule ('until 31 Dec 2025') was extended by an amendment that took effect AFTER the
old end date, leaving a gap in which the rule did not exist (Swiss GMO moratorium pattern).

python detectors/late_extension.py RUN -> findings/RUN/late_extension.parquet
"""
from __future__ import annotations
import datetime as dt, json, re, sys
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
import duckdb
from common import FINDINGS, INDEX, CORPUS, WORKERS, pins, lower_priority
from textscan import limits, stream, is_law_file

I = INDEX.as_posix()


def one(c):
    lower_priority()
    repo = CORPUS / f"{c['repo']}.git"
    f = INDEX / "changes" / f"{c['repo']}.parquet"
    if not f.exists():
        return []
    con = duckdb.connect(); con.execute("set threads to 1")
    rows = con.execute(f"""select ch.path, ch.old_blob, ch.new_blob, r.in_force, r.law from '{f.as_posix()}' ch
        join '{I}/root.parquet' r on r.corpus_commit = ch.commit
        where left(ch.status, 1) = 'M' and r.kind = 'law' and r.in_force is not null and r.in_force <> ''""").fetchall()
    rows = [r for r in rows if is_law_file(r[0])]
    olds = sorted({r[1] for r in rows})
    lim_old = {}
    for sh, t in stream(repo, olds):
        if t:
            ls = list(limits(t, deadlines=False))
            if ls:
                lim_old[sh] = ls
    cand = [r for r in rows if r[1] in lim_old and any(d < r[3][:10] for d, _ in lim_old[r[1]])]
    lim_new = {}
    for sh, t in stream(repo, sorted({r[2] for r in cand})):
        lim_new[sh] = list(limits(t, deadlines=False)) if t else []
    out = []
    for path, a, b, inf, law in cand:
        newd = {d for d, _ in lim_new.get(b, [])}
        oldd = {d for d, _ in lim_old[a]}
        for d, ctx in lim_old[a]:
            if d >= inf[:10] or d in newd:
                continue
            later = sorted(x for x in newd - oldd if x > d)
            if not later:
                continue
            gap = (dt.date.fromisoformat(inf[:10]) - dt.date.fromisoformat(d)).days
            if gap < 2:
                continue
            nctx = next(cx for x, cx in lim_new[b] if x == later[0])
            out.append({"corpus": c["path"], "path": path, "old_until": d, "new_until": later[0], "extended_in_force": inf[:10],
                        "gap_days": gap, "law": law, "old_context": ctx[:400], "new_context": nctx[:400]})
    return out


def main() -> None:
    lower_priority()
    run = sys.argv[1] if len(sys.argv) > 1 else "run2"
    cs = [c for c in pins()["corpora"] if not c["repo"].startswith(("united-kingdom", "romania"))]
    cs.sort(key=lambda c: -(INDEX / "changes" / f"{c['repo']}.parquet").stat().st_size if (INDEX / "changes" / f"{c['repo']}.parquet").exists() else 0)
    allr = []
    with Pool(WORKERS) as p:
        for rs in p.imap_unordered(one, cs):
            allr += rs
            if rs:
                print(rs[0]["corpus"], len(rs), flush=True)
    dst = FINDINGS / run / "late_extension.jsonl"
    with dst.open("w", encoding="utf-8") as fh:
        for r in allr:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("late_extension", len(allr))


if __name__ == "__main__":
    main()
