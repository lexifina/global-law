"""Detectors over the text scan (index/dates, index/amounts, index/amount_changes).

lapsed_limit  current text says "until <date>", the date has passed, and the provision has not changed since
stale_amount  a law replaced an amount in one provision; the old amount (same unit) still stands elsewhere

python detectors/text_detectors.py RUN   -> findings/RUN/ranked_lapsed_limit.parquet, ranked_stale_amount.parquet
"""
from __future__ import annotations
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
import duckdb
from common import FINDINGS, INDEX

TODAY = time.strftime("%Y-%m-%d")


def main() -> None:
    run = sys.argv[1] if len(sys.argv) > 1 else "run1"
    f = FINDINGS / run
    con = duckdb.connect()
    con.sql("set threads to 8")
    I = INDEX.as_posix()
    con.sql(f"create view changes as select * from '{I}/changes/*.parquet'")
    con.sql(f"create view root as select * from '{I}/root.parquet'")
    con.sql(f"""create temp table last_change as
        select ch.corpus, ch.path, max(r.in_force) last_in_force, arg_max(r.law, r.in_force) last_law
        from changes ch join root r on r.corpus_commit = ch.commit where r.kind in ('law','baseline') group by all""")
    q = {
    "lapsed_limit": f"""
      with d as (select distinct corpus, path, until, context from '{I}/dates/*.parquet' where until < '{TODAY}' and until >= '1950' and try_cast(until as date) is not null)
      select d.*, lc.last_in_force, lc.last_law,
        date_diff('day', try_cast(d.until as date), date '{TODAY}') lapsed_days,
        regexp_matches(lower(d.context), '(not later than|no later than|spätestens|a más tardar|au plus tard|senast|uiterlijk)') as deadline,
        (case when lc.last_in_force <= d.until then 0.45 else 0.1 end)
          + (case when regexp_matches(lower(d.context), '(not later than|no later than|spätestens|a más tardar|au plus tard|senast|uiterlijk|report|submit|bericht|informe)') then 0 else 0.3 end)
          + 0.25 * least(1.0, date_diff('day', try_cast(d.until as date), date '{TODAY}') / 1825.0) as score,
        'text limits the rule to ' || d.until || '; last change to the provision took effect ' || coalesce(lc.last_in_force,'?') as why
      from d left join last_change lc using (corpus, path)
      order by score desc""",
    "stale_amount": f"""
      with x as (
        select ac.corpus, ac.path, ac.in_force, ac.law, regexp_replace(split_part(o, '|', 1), '[.]00$', '') old_value, split_part(o, '|', 2) unit,
               list_filter(ac.added, lambda a: split_part(a, '|', 2) = split_part(o, '|', 2) and regexp_replace(split_part(a, '|', 1), '[.]00$', '') <> regexp_replace(split_part(o, '|', 1), '[.]00$', '')) new_values
        from '{I}/amount_changes/*.parquet' ac, unnest(ac.removed) u(o)),
      x2 as (select * from x where len(new_values) between 1 and 3 and unit <> '%' and length(old_value) >= 3),
      cur as (select distinct corpus, path, regexp_replace(value, '[.]00$', '') value, unit from '{I}/amounts/*.parquet'),
      hits as (
        select x2.corpus, x2.path, x2.in_force, x2.law, x2.old_value || ' ' || x2.unit old,
               array_to_string(list_transform(x2.new_values, lambda v: split_part(v,'|',1)), ', ') || ' ' || x2.unit new,
               list(distinct cur.path) still_in, count(distinct cur.path) n_other
        from x2 join cur on cur.corpus = x2.corpus and cur.value = x2.old_value and cur.unit = x2.unit and cur.path <> x2.path
        where not exists (select 1 from cur c2 where c2.corpus = x2.corpus and c2.path = x2.path and c2.value = x2.old_value and c2.unit = x2.unit)
        group by all)
      select *, (case when n_other <= 3 then 0.6 when n_other <= 10 then 0.4 else 0.1 end)
               + 0.4 * least(1.0, length(split_part(old, ' ', 1)) / 7.0) as score,
             law || ' changed ' || old || ' to ' || new || ' in ' || path || ', but ' || old || ' still appears in ' || n_other || ' other provision(s)' as why
      from hits where n_other <= 25 order by score desc""",
    }
    for name, sql in q.items():
        t0 = time.time()
        dst = (f / f"ranked_{name}.parquet").as_posix()
        con.sql(f"copy ({sql}) to '{dst}' (format parquet, compression zstd)")
        n = con.sql(f"select count(*), count(distinct corpus), count(*) filter (where score >= 0.6) from '{dst}'").fetchall()[0]
        print(f"{name:14s} {n[0]:>8,} in {n[1]:>3} corpora, {n[2]:>6,} score>=0.6 ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
