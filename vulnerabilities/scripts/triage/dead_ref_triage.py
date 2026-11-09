"""Triage for dead_act_ref: is the dead citation cured (general substitution clause, implied remission), and if not,
what breaks? python triage/dead_ref_triage.py RUN [--min 0.8]  -> findings/RUN/dead_act_ref_triage.jsonl"""
from __future__ import annotations
import argparse, json, re, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from common import FINDINGS, CORPUS, FLAGS, pins, lower_priority
from llm import call
import triage as T
import subprocess

SCHEMA = {"type": "object", "additionalProperties": False, "required": [
    "cure", "cure_found", "what_breaks", "one_line", "verdict", "confidence"],
    "properties": {"cure": {"type": "string"}, "cure_found": {"type": "boolean"}, "what_breaks": {"type": "string"},
                   "one_line": {"type": "string"},
                   "verdict": {"type": "string", "enum": ["candidate_defect", "cured_or_harmless", "artefact"]},
                   "confidence": {"type": "number"}}}
PROMPT = """A provision of Spanish law that is in force today cites an act that BOE lists as no longer in force.
1. Is the dead citation cured? Look for: a general clause in the repealing/replacing act saying references to the old
   act are understood as references to the new one (name it exactly, e.g. 'disposición final X de la Ley Y'); an
   express transitional survival of the old act for this purpose; the citation being merely historical/descriptive.
2. If not cured, what concretely breaks (a tax exemption whose condition can no longer be met, a sanction whose
   infraction catalogue no longer exists, a deadline with no anchor, a body that no longer exists...)?
3. one_line: one plain-English sentence a non-lawyer would understand, e.g. "The VAT exemption for X still depends on
   article 108 of a 1988 law that was repealed in 2015."
Be strict: say cured if you know of a substitution clause. Say artefact if the cited act is a different act with the
same number (e.g. a regional law) or the corpus status looks wrong.

CITING PROVISION ({path}, last rewritten {lc} by {ll}):
{text}

CITED ACT: {title}  (BOE: no longer in force; last change in the record {dc})"""


def main() -> None:
    lower_priority()
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--min", type=float, default=0.8)
    a = ap.parse_args()
    f = FINDINGS / a.run
    rel = duckdb.sql(f"select * from '{(f/'ranked_dead_act_ref.parquet').as_posix()}' where score >= {a.min}")
    cols = rel.columns; rows = [dict(zip(cols, t)) for t in rel.fetchall()]
    MES = r"de (\d{1,2}) de (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
    keep, seen = [], set()
    for r in rows:
        m1 = re.search(re.escape(r["cite"]) + r",?\s*" + MES, r["context"]); m2 = re.search(MES, r["cited_title"])
        if m1 and m2 and m1.groups() != m2.groups():
            continue                      # same number, different act (regional or misread)
        k = (r["path"], r["cited_id"])
        if k not in seen:
            seen.add(k); keep.append(r)
    print(len(rows), "->", len(keep), flush=True)
    sha = [c["sha"] for c in pins()["corpora"] if c["repo"] == "spain-law"][0]
    out = f / "dead_act_ref_triage.jsonl"; lock = threading.Lock()

    def work(i, r):
        txt = subprocess.run(["git", "-C", str(CORPUS / "spain-law.git"), "show", f"{sha}:{r['path']}"], capture_output=True,
                             creationflags=FLAGS).stdout.decode("utf-8", "replace")[:6000]
        res = call(PROMPT.format(path=r["path"], lc=r["citing_last_change"], ll=r["citing_last_law"], text=txt,
                                 title=r["cited_title"], dc=r["cited_last_change"]), system=T.SYSTEM, schema=SCHEMA,
                   provider="azure-uk" if i % 2 else "azure", max_tokens=1800)
        return {"row": {k: str(v) for k, v in r.items()}, "j": res["json"], "tokens": [res["tokens_in"], res["tokens_out"]]}

    with ThreadPoolExecutor(32) as ex, out.open("w", encoding="utf-8") as fh:
        for n, fu in enumerate(as_completed([ex.submit(work, i, r) for i, r in enumerate(keep)]), 1):
            try:
                rec = fu.result()
            except Exception as e:
                print("error:", str(e)[:200], flush=True); continue
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
            if n % 25 == 0:
                print(n, flush=True)


if __name__ == "__main__":
    main()
