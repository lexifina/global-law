"""dangling_ref: a current provision refers to a provision of the same act that existed once and no longer exists.

python detectors/ref_detectors.py RUN -> findings/RUN/ranked_dangling_ref.parquet
"""
from __future__ import annotations
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
import duckdb
from common import FINDINGS, INDEX

NOISE = r"(?i)(Textänderung|Fin de vigueur|Mevzuat Bilgi Sistemi|RIS \(Bundeskanzleramt\)|Regeringskansliet|e-Sbírka|Consolidat)"


def main() -> None:
    run = sys.argv[1] if len(sys.argv) > 1 else "run1"
    f = FINDINGS / run
    con = duckdb.connect()
    I = INDEX.as_posix()
    con.sql(f"create view changes as select * from '{I}/changes/*.parquet'")
    con.sql(f"create view root as select * from '{I}/root.parquet'")
    con.sql(f"""create temp table removed as
        select ch.corpus, ch.path, max(r.in_force) removed_on, arg_max(r.law, r.in_force) removed_by
        from changes ch join root r on r.corpus_commit = ch.commit where left(ch.status,1) = 'D' and r.kind = 'law' group by all""")
    con.sql(f"""create temp table cite_last as
        select ch.corpus, ch.path, max(r.in_force) citing_last_change from changes ch join root r on r.corpus_commit = ch.commit
        where r.kind in ('law','baseline') group by all""")
    dst = (f / "ranked_dangling_ref.parquet").as_posix()
    con.sql(f"""copy (
      with d0 as (select distinct on (corpus, path, ref) * from (
                    select * from '{I}/refs/*.parquet' where corpus not like 'czechia/%'
                    union all select * from '{I}/refs_fileact/*.parquet')
                  where not regexp_matches(lower(context), '(se vkládají|se nahrazuj|se zrušuj|se doplňuj|pozbývají platnosti|wird ersetzt|werden ersetzt|wird aufgehoben|is replaced|is substituted|is repealed|se sustituye|se modifica|est remplacé|est abrogé|ersätts|upphävs)')),  -- one file per law inside year folders: folder is not the act
      d as (select * from d0 where
              not regexp_matches(tail, '^\s*(\.º|º|\.|\))?\s*\n')   -- a heading, not a reference
              and not (regexp_matches(lower(left(tail, 90)),
                '(\bdes\b|\bder\b|of (the )?(directive|regulation|act|law|code|convention|treaty|constitution|decree|order)|zákona|vyhlášky|nařízení|de la ley|del código|de la directiva|del reglamento|do código|da lei|del regolamento|direttiva|kanunu|kanunun|qanun|закона|кодекса|օրենքի|კანონის|directive|richtlinie|buches|gesetzes|verordnung)')
                and not regexp_matches(lower(left(tail, 90)), '(dieses|dieser|this act|this law|this code|these regulations|this regulation|ce code|la présente|este código|esta ley|deste código|presente|bu kanun|настоящего|этого)')))
      select d.corpus, d.path, d.ref, d.target_path, d.target_last_seen, rm.removed_on, coalesce(rm.removed_by, d.target_last_law) removed_by,
             cl.citing_last_change, d.context,
             0.4 + (case when rm.removed_by is not null and not regexp_matches(rm.removed_by, '{NOISE}') then 0.3 else 0 end)
                 + (case when cl.citing_last_change > coalesce(rm.removed_on, d.target_last_seen) then 0.3 else 0.1 end) as score,
             'refers to ' || d.ref || ' of the same act, last in the record ' || d.target_last_seen ||
               coalesce(', removed ' || rm.removed_on || ' by ' || rm.removed_by, '') as why
      from d left join removed rm on rm.corpus = d.corpus and rm.path = d.target_path
             left join cite_last cl on cl.corpus = d.corpus and cl.path = d.path
      order by score desc) to '{dst}' (format parquet, compression zstd)""")
    n = con.sql(f"select count(*), count(distinct corpus), count(*) filter (where score >= 0.7) from '{dst}'").fetchall()[0]
    print(f"dangling_ref {n[0]:,} in {n[1]} corpora, {n[2]:,} score>=0.7")


if __name__ == "__main__":
    main()
