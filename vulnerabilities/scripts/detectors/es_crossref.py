"""dead_act_ref (Spain): a provision of an act still in force cites a numbered act that BOE marks as no longer in force
(vigencia agotada = S). Ranked by whether the citing provision was itself rewritten after the cited act died.

python detectors/es_crossref.py RUN -> findings/RUN/ranked_dead_act_ref.parquet
"""
from __future__ import annotations
import csv, io, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
import duckdb
from common import GIT_GREP_THREADS, FINDINGS, INDEX, CORPUS, FLAGS, pins, lower_priority

GIT = CORPUS / "spain-law.git"
SHA = [c["sha"] for c in pins()["corpora"] if c["repo"] == "spain-law"][0]
KIND = r"(Ley Orgánica|Real Decreto-ley|Real Decreto Legislativo|Real Decreto|Ley)"
CITE = re.compile(KIND + r"\s+(\d{1,4})/(\d{4})")
HIST = re.compile(r"(?i)(derog|redacción (dada|anterior)|modificad[oa] por|introducid[oa] por|añadid[oa] por|"
                  r"vigente hasta|sustitu|disposición transitoria|régimen transitorio|con anterioridad|anterior(es)? a la entrada|"
                  r"se entender[áa]n? (hecha|realizada)s?|al amparo de lo (dispuesto|previsto) en la (derogada|anterior)|texto refundido)")


def main() -> None:
    lower_priority()
    run = sys.argv[1] if len(sys.argv) > 1 else "run2"
    f = FINDINGS / run
    tsv = subprocess.run(["git", "-C", str(GIT), "show", f"{SHA}:normas.tsv"], capture_output=True, creationflags=FLAGS).stdout.decode("utf-8")
    norms = list(csv.DictReader(io.StringIO(tsv), delimiter="\t"))
    key = {}
    for n in norms:
        m = CITE.match(n["titulo"])
        if m:
            key[(m.group(1).lower(), int(m.group(2)), m.group(3))] = n
    live_paths = tuple(n["path"] + "/" for n in norms if n["vigencia_agotada"] == "N" and n["rango"] in
                       ("Ley", "Ley Orgánica", "Real Decreto Legislativo", "Real Decreto-ley"))
    print(len(norms), "norms;", len(key), "keyed;", len(live_paths), "live primary acts", flush=True)
    p = subprocess.run(["git", "-C", str(GIT), "grep", "--threads", GIT_GREP_THREADS, "-n", "-P", KIND + r"\s+\d{1,4}/\d{4}", SHA, "--", "estatal/ley", "estatal/ley-organica",
                        "estatal/real-decreto-legislativo", "estatal/real-decreto-ley"], capture_output=True, creationflags=FLAGS)
    rows = []
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        try:
            _, path, ln, text = line.split(":", 3)
        except ValueError:
            continue
        if not path.startswith(live_paths) or text.lstrip().startswith(("#", "|", ">", "*")):
            continue
        name = path.rsplit("/", 1)[1]
        if name.startswith(("dd", "dt", "pr", "preambulo", "index", "README", "nota")):   # repeal, transitional, preamble files
            continue
        for m in CITE.finditer(text):
            n = key.get((m.group(1).lower(), int(m.group(2)), m.group(3)))
            if not n or n["vigencia_agotada"] != "S":
                continue
            ctx = text[max(0, m.start() - 250): m.end() + 250]
            if HIST.search(ctx):
                continue
            rows.append((path, int(ln), m.group(0), n["id"], n["rango"], n["titulo"][:200], n["path"], ctx))
    con = duckdb.connect()
    con.execute("create table refs(path varchar, line int, cite varchar, cited_id varchar, cited_rango varchar, cited_title varchar, cited_path varchar, context varchar)")
    con.executemany("insert into refs values (?,?,?,?,?,?,?,?)", rows)
    I = INDEX.as_posix()
    con.sql(f"create view ch as select ch.path, r.in_force, r.law from '{I}/changes/spain-law.parquet' ch join '{I}/root.parquet' r on r.corpus_commit = ch.commit where r.corpus = 'spain/national/acts'")
    dst = (f / "ranked_dead_act_ref.parquet").as_posix()
    con.sql(f"""copy (
        with last_cite as (select path, max(in_force) citing_last_change, arg_max(law, in_force) citing_last_law from ch group by 1),
             dead as (select split_part(path, '/', 1) || '/' || split_part(path, '/', 2) || '/' || split_part(path, '/', 3) || '/' || split_part(path, '/', 4) folder,
                             max(in_force) cited_last_change from ch group by 1)
        select 'spain/national/acts' corpus, r.*, lc.citing_last_change, lc.citing_last_law, d.cited_last_change,
               0.4 + case when lc.citing_last_change > d.cited_last_change then 0.4 else 0 end
                   + case when r.cited_rango in ('Ley', 'Ley Orgánica', 'Real Decreto Legislativo') then 0.1 else 0 end
                   + case when regexp_matches(r.context, '(?i)(sanci|multa|infracci|delito|pena|plazo|derecho a|exen|bonific)') then 0.1 else 0 end score,
               'cites ' || r.cite || ' (' || r.cited_rango || ', no longer in force per BOE)' ||
               coalesce('; citing provision last rewritten ' || lc.citing_last_change, '') why
        from refs r left join last_cite lc on lc.path = r.path left join dead d on d.folder = r.cited_path
        order by score desc, citing_last_change desc) to '{dst}' (format parquet, compression zstd)""")
    print(con.sql(f"select count(*), count(distinct path), count(*) filter (where score >= 0.8) from '{dst}'").fetchall())


if __name__ == "__main__":
    main()
