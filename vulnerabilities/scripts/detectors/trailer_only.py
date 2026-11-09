"""Detectors that need only the history (which file, which law, which in-force date).

same_day_conflict  two different laws change the same provision with the same in-force date
repeal_gap         a provision is deleted, then the same path comes back later: a window with no text
retroactive_date   a change is in force before the law that made it was enacted / published

Usage: python detectors/trailer_only.py [RUN_ID]
"""
from __future__ import annotations
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
import duckdb
from common import FINDINGS, INDEX

LAWFILE = """(path ilike '%.md' or path ilike '%.txt')
  and lower(regexp_extract(path, '[^/]+$')) not in ('readme.md','reproduce.md','changelog.md','license.md','sources.md')
  and not regexp_matches(path, '^(docs|tools|tests|\\.github)/')"""

SQL = {
"same_day_conflict": f"""
with ev as (
  select ch.corpus, ch.path, ch.status, r.in_force, r.law, r.root
  from changes ch join root r on r.corpus_commit = ch.commit
  where r.kind = 'law' and left(ch.status,1) in ('M','A','R') and {LAWFILE})
select corpus, path, in_force, count(distinct law) n_laws, list(distinct law) laws, list(distinct root) roots
from ev group by all having count(distinct law) >= 2
order by n_laws desc, corpus, path""",

"repeal_gap": f"""
with ev as (
  select ch.corpus, ch.path, left(ch.status,1) st, r.in_force, r.law, r.kind, r.seq
  from changes ch join root r on r.corpus_commit = ch.commit
  where r.kind in ('law','baseline') and {LAWFILE}),
seq as (
  select *, lead(st) over w nst, lead(in_force) over w nin, lead(law) over w nlaw
  from ev window w as (partition by corpus, path order by in_force, seq desc))
select corpus, path, in_force as removed_on, law as removed_by, nin as back_on, nlaw as back_by,
       date_diff('day', try_cast(in_force as date), try_cast(nin as date)) as gap_days
from seq where st = 'D' and kind = 'law' and nst = 'A' and nin > in_force
order by gap_days desc""",

"retroactive_date": """
with c as (
  select corpus, commit,
    coalesce(
      try_cast(regexp_extract(json_extract_string(trailers, '$.Published[0]'), '\\d{4}-\\d{2}-\\d{2}') as date),
      try_cast(regexp_extract(json_extract_string(trailers, '$.Enacted[0]'), '\\d{4}-\\d{2}-\\d{2}') as date),
      try_cast(regexp_extract(json_extract_string(trailers, '$.Adopted[0]'), '\\d{4}-\\d{2}-\\d{2}') as date),
      try_cast(regexp_extract(json_extract_string(trailers, '$.Signed[0]'), '\\d{4}-\\d{2}-\\d{2}') as date),
      try_cast(regexp_extract(json_extract_string(trailers, '$.Issued[0]'), '\\d{4}-\\d{2}-\\d{2}') as date)) as made,
    case when json_extract_string(trailers, '$.Published[0]') is not null then 'Published'
         when json_extract_string(trailers, '$.Enacted[0]') is not null then 'Enacted'
         when json_extract_string(trailers, '$.Adopted[0]') is not null then 'Adopted'
         when json_extract_string(trailers, '$.Signed[0]') is not null then 'Signed'
         else 'Issued' end as made_field,
    trailers
  from commits)
select r.corpus, r.law, min(r.in_force) in_force, min(c.made) made, c.made_field,
       max(date_diff('day', try_cast(r.in_force as date), c.made)) back_days,
       count(*) commits, any_value(r.subject) subject, any_value(c.trailers) trailers
from root r join c on c.commit = r.corpus_commit
where r.kind = 'law' and c.made is not null and try_cast(r.in_force as date) < c.made
group by r.corpus, r.law, c.made_field
order by back_days desc""",
}


def main() -> None:
    run = sys.argv[1] if len(sys.argv) > 1 else time.strftime("%Y%m%d-%H%M")
    out = FINDINGS / run
    out.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.sql("set threads to 8")
    con.sql(f"create view changes as select * from '{(INDEX / 'changes').as_posix()}/*.parquet'")
    con.sql(f"create view root as select *, row_number() over () seq from '{(INDEX / 'root.parquet').as_posix()}'")
    con.sql(f"create view commits as select * from '{(INDEX / 'commits').as_posix()}/*.parquet'")
    for name, q in SQL.items():
        t0 = time.time()
        con.sql(f"copy ({q}) to '{(out / (name + '.parquet')).as_posix()}' (format parquet, compression zstd)")
        n = con.sql(f"select count(*), count(distinct corpus) from '{(out / (name + '.parquet')).as_posix()}'").fetchall()[0]
        print(f"{name:20s} {n[0]:>9,} candidates in {n[1]:>3} corpora  ({time.time()-t0:.0f}s)", flush=True)
    print(f"run {run} -> {out}")


if __name__ == "__main__":
    main()
