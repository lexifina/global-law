"""Rank raw detector output: drop known artefacts, add enactment dates and an instrument type, score.

Writes findings/<run>/ranked_<detector>.parquet with columns score, tier, why (+ the raw fields).
"""
from __future__ import annotations
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
import duckdb
from common import FINDINGS, INDEX

# Artefact laws: consolidation / publisher notes, not acts.
NOISE = r"(?i)^(Textänderung|Fin de vigueur|Regeringskansliet|Publisher|Consolidat|Baseline|Unknown|None$|Mevzuat Bilgi Sistemi|e-Sbírka)|ispravak|rectifica|berichtigung|corrigendum|erratum"
# Delegated / executive instruments: retroactivity and authority defects bite hardest here.
REG = (r"(?i)(arrêté|décret|ordonnance|real decreto|decreto|orden |resoluci[oó]n|circular|instrucci[oó]n|"
       r"verordnung|regulation|statutory instrument|order\b|rule[s]?\b|directive|notice|bekanntmachung|"
       r"hotărâre|vyhláška|nařízení|постановлени|приказ|որոշում|ბრძანებ|დადგენილებ|karar|yönetmelik|tebliğ|"
       r"emergency)")
DMY = r"(\d{1,2})[./](\d{1,2})[./](\d{4})"


def enacted_expr(col: str) -> str:
    """Best-effort enactment date from a law label ('... (26.03.2026)', '... du 29 décembre 1983')."""
    return (f"coalesce(try_cast(try_strptime(regexp_extract({col}, '{DMY}', 0), '%d.%m.%Y') as date),"
            f" try_cast(regexp_extract({col}, '(\\d{{4}}-\\d{{2}}-\\d{{2}})', 1) as date))")


def main() -> None:
    run = sys.argv[1] if len(sys.argv) > 1 else "run1"
    f = FINDINGS / run
    con = duckdb.connect()
    con.sql(f"create view root as select * from '{(INDEX / 'root.parquet').as_posix()}'")
    con.sql(f"create view commits as select * from '{(INDEX / 'commits').as_posix()}/*.parquet'")
    # one enactment date per (corpus, law) from the corpus's own trailers, else from the label
    con.sql(f"""create temp table law_made as
      select r.corpus, r.law, min(coalesce(
        try_cast(regexp_extract(json_extract_string(c.trailers,'$.Enacted[0]'),'\\d{{4}}-\\d{{2}}-\\d{{2}}') as date),
        try_cast(regexp_extract(json_extract_string(c.trailers,'$.Adopted[0]'),'\\d{{4}}-\\d{{2}}-\\d{{2}}') as date),
        try_cast(regexp_extract(json_extract_string(c.trailers,'$.Signed[0]'),'\\d{{4}}-\\d{{2}}-\\d{{2}}') as date),
        try_cast(regexp_extract(json_extract_string(c.trailers,'$.Published[0]'),'\\d{{4}}-\\d{{2}}-\\d{{2}}') as date),
        {enacted_expr('r.law')})) made
      from root r left join commits c on c.commit = r.corpus_commit
      where r.kind='law' group by all""")

    q = {
    "same_day_conflict": f"""
      with x as (
        select s.* from '{(f/'same_day_conflict.parquet').as_posix()}' s
        where not list_has_any(list_transform(s.laws, lambda l: regexp_matches(l, '{NOISE}')), [true])),
      m as (
        select x.corpus, x.path, x.in_force, x.laws, x.n_laws,
               min(lm.made) first_made, max(lm.made) last_made
        from x, unnest(x.laws) u(l) left join law_made lm on lm.corpus = x.corpus and lm.law = u.l
        group by all)
      select *, date_diff('day', first_made, last_made) spread_days,
        least(1.0, coalesce(date_diff('day', first_made, last_made), 0) / 365.0) * 0.7 + least(n_laws - 1, 3) / 3.0 * 0.3 as score,
        'two or more laws enacted ' || coalesce(date_diff('day', first_made, last_made)::varchar, '?') ||
        ' days apart take effect on the same day in one provision; the later may have been drafted against text the earlier had not yet changed' as why
      from m order by score desc""",

    "repeal_gap": f"""
      with g as (
        select g.*, lm.made back_made from '{(f/'repeal_gap.parquet').as_posix()}' g
        left join law_made lm on lm.corpus = g.corpus and lm.law = g.back_by
        where gap_days >= 2 and not regexp_matches(coalesce(back_by,''), '{NOISE}')
          and not regexp_matches(coalesce(removed_by,''), '^Textänderung'))
      select *,
        case when back_made is not null and back_made > try_cast(removed_on as date) then 'revived after lapse'
             when back_made is not null then 'gap foreseen when enacted' else 'unknown' end as kind,
        least(1.0, gap_days / 365.0) * 0.6 + (case when back_made > try_cast(removed_on as date) then 0.4 else 0.1 end) as score,
        'provision had no text for ' || gap_days || ' days (' || removed_on || ' to ' || back_on || ')' as why
      from g order by score desc""",

    "retroactive_date": f"""
      select *, regexp_matches(law, '{REG}') delegated,
        (case when regexp_matches(law, '{REG}') then 0.6 else 0.2 end) + least(1.0, back_days / 365.0) * 0.4 as score,
        law || ' is dated in force ' || back_days || ' days before it was ' || lower(made_field) as why
      from '{(f/'retroactive_date.parquet').as_posix()}'
      where back_days >= 2 and in_force >= '1800' and not regexp_matches(law, '{NOISE}') order by score desc""",
    }
    for name, sql in q.items():
        t0 = time.time()
        dst = (f / f"ranked_{name}.parquet").as_posix()
        con.sql(f"copy ({sql}) to '{dst}' (format parquet, compression zstd)")
        n = con.sql(f"select count(*), count(distinct corpus), count(*) filter (where score >= 0.6) from '{dst}'").fetchall()[0]
        print(f"{name:20s} {n[0]:>8,} kept in {n[1]:>3} corpora, {n[2]:>6,} score>=0.6  ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
