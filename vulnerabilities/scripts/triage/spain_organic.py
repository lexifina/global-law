"""organic_reserve (Spain, art. 81 CE): an instrument that is not a Ley Orgánica changed the text of a Ley Orgánica.
Defect if the changed provision has organic character (not listed as 'ley ordinaria' in the LO's final provisions)
and the matter is reserved to organic law.

python triage/spain_organic.py RUN -> findings/RUN/organic_reserve.jsonl
"""
from __future__ import annotations
import json, subprocess, sys, re, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from common import FINDINGS, INDEX, CORPUS, FLAGS, pins, lower_priority
from llm import call
import triage as T

C = "spain/national/acts"
SHA = [c["sha"] for c in pins()["corpora"] if c["repo"] == "spain-law"][0]
GIT = CORPUS / "spain-law.git"

SCHEMA = {"type": "object", "additionalProperties": False, "required": [
    "organic_law", "amending_instrument", "amending_kind", "provisions", "verdict", "reason", "confidence"],
    "properties": {
        "organic_law": {"type": "string"}, "amending_instrument": {"type": "string"},
        "amending_kind": {"type": "string", "enum": ["ley ordinaria", "real decreto-ley", "real decreto legislativo",
                                                       "real decreto / reglamento", "ley orgánica", "sentencia / otro", "unclear"]},
        "provisions": {"type": "array", "items": {"type": "object", "additionalProperties": False,
            "required": ["provision", "status"], "properties": {"provision": {"type": "string"},
            "status": {"type": "string", "enum": ["declared ordinary", "organic", "unclear"]}}}},
        "verdict": {"type": "string", "enum": ["candidate_defect", "lawful", "artefact"]},
        "reason": {"type": "string"}, "confidence": {"type": "number"}}}

PROMPT = """Spanish Constitution art. 81: matters reserved to Ley Orgánica (fundamental rights and public freedoms,
Estatutos de Autonomía, régimen electoral general, others named in the Constitution) may only be approved, amended or
repealed by Ley Orgánica (absolute majority of the Congreso). Ordinary laws may amend provisions of an LO only where the
LO itself (or a later LO) declares them 'carácter de ley ordinaria'. A Real Decreto-ley may not affect Title I rights,
the Estatutos or régimen electoral (art. 86.1); a Real Decreto legislativo may not touch organic matter (art. 82.1).
Statutes of Autonomy have their own reform procedures (art. 147.3).

The record below shows a NON-organic instrument (per the corpus label) changing the text of a Ley Orgánica.
Decide: is this a candidate defect (organic provision changed by a non-organic instrument), lawful (the provision is
declared ordinary, or the instrument is in fact an LO, or a permitted update), or a corpus artefact (wrong attribution,
the change is a court ruling or editorial)? Be strict and concrete; cite the carácter clause you rely on.

AMENDING INSTRUMENT (corpus label): {law}
TARGET LEY ORGÁNICA: {lo}  (in force from the record: {d})

CARÁCTER CLAUSES FOUND IN THE TARGET LO'S FINAL PROVISIONS:
{car}

CARÁCTER / FINAL CLAUSES OF THE AMENDING INSTRUMENT (if in the corpus):
{car2}

CHANGES MADE (unified diffs, before -> after):
{diffs}"""


def gitgrep(pathspec):
    p = subprocess.run(["git", "-C", str(GIT), "grep", "-h", "-i", "-E", r"car[aá]cter|org[aá]nic|ordinaria|habilita|fundamento", SHA, "--", pathspec],
                       capture_output=True, creationflags=FLAGS)
    return p.stdout.decode("utf-8", "replace")


def lo_title(folder):
    for f in ("index.md", "README.md"):
        p = subprocess.run(["git", "-C", str(GIT), "show", f"{SHA}:{folder}/{f}"], capture_output=True, creationflags=FLAGS)
        if p.returncode == 0:
            return p.stdout.decode("utf-8", "replace")[:400]
    return folder


def main() -> None:
    lower_priority()
    run = sys.argv[1] if len(sys.argv) > 1 else "run2"
    out = FINDINGS / run / "organic_reserve.jsonl"
    con = duckdb.connect()
    rows = con.sql(f"""select r.law, regexp_extract(ch.path, '^(estatal/ley-organica/[0-9]+/[^/]+)', 1) lo, min(r.in_force) d,
            list(struct_pack(path := ch.path, a := ch.old_blob, b := ch.new_blob, st := ch.status)) ch
        from '{(INDEX/'changes'/'spain-law.parquet').as_posix()}' ch join '{(INDEX/'root.parquet').as_posix()}' r on r.corpus_commit = ch.commit
        where ch.path like 'estatal/ley-organica/%' and r.kind = 'law' and r.law not ilike '%Orgánica%'
          and r.law not ilike '%Agencia Estatal%' and r.law not ilike '%Sentencia%' and r.law not ilike '%Instrucción%'
          and r.law not ilike '%Auto %'
        group by 1, 2""").fetchall()
    print(len(rows), "groups", flush=True)
    lock = threading.Lock()

    def work(i, row):
        law, lo, d, chs = row
        boe = re.search(r"BOE-A-\d{4}-\d+", law or "")
        car2 = gitgrep(f"*/{boe.group(0)}/d*") if boe else ""
        diffs = []
        for c in chs[:6]:
            diffs.append(f"--- {c['path']} ({c['st']})\n" + T.udiff(T.blob(C, c['a'], 6000), T.blob(C, c['b'], 6000), 2200))
        prompt = PROMPT.format(law=law, lo=lo_title(lo), d=d, car=gitgrep(f"{lo}/d*")[:5000] or "(none found)",
                               car2=car2[:2500] or "(not in corpus)", diffs="\n".join(diffs)[:12000])
        res = call(prompt, system=T.SYSTEM, schema=SCHEMA, provider="azure-uk" if i % 2 else "azure", max_tokens=2500)
        return {"law": law, "lo": lo, "date": str(d), "paths": [c["path"] for c in chs], "j": res["json"],
                "tokens": [res["tokens_in"], res["tokens_out"]]}

    n = 0
    with ThreadPoolExecutor(24) as ex, out.open("w", encoding="utf-8") as fh:
        for fu in as_completed([ex.submit(work, i, r) for i, r in enumerate(rows)]):
            try:
                rec = fu.result()
            except Exception as e:
                print("error:", str(e)[:200], flush=True); continue
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush(); n += 1
                print(n, rec["j"]["verdict"], rec["law"][:60], "->", rec["lo"], flush=True)


if __name__ == "__main__":
    main()
