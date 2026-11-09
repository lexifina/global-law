"""Triage late_extension: did a real gap open (rule not in force between old end date and extension), and who gains?
python triage/late_ext_triage.py RUN -> findings/RUN/late_extension_triage.jsonl"""
from __future__ import annotations
import json, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from common import FINDINGS, INDEX, lower_priority
from llm import call
import triage as T

SCHEMA = {"type": "object", "additionalProperties": False, "required": [
    "rule_type", "gap_real", "retroactive_cure_likely", "what_was_possible", "one_line", "verdict", "strength", "confidence"],
    "properties": {
        "rule_type": {"type": "string", "enum": ["tax or levy", "prohibition or moratorium", "exemption or relief", "benefit or subsidy",
                                                  "authority or power", "transitional application", "deadline for authorities", "other"]},
        "gap_real": {"type": "boolean"}, "retroactive_cure_likely": {"type": "boolean"},
        "what_was_possible": {"type": "string"}, "one_line": {"type": "string"},
        "verdict": {"type": "string", "enum": ["candidate_gap", "no_gap", "artefact"]},
        "strength": {"type": "integer", "description": "1-5: how consequential and easy to explain"},
        "confidence": {"type": "number"}}}
PROMPT = """A time-limited rule ran 'until {old}'. The record shows it extended to '{new}' by {law}, which took effect on
{eff}, i.e. {gap} days AFTER the old end date. If the extension was not retroactive, the rule did not exist in between.
Judge:
- rule_type; gap_real: did the rule truly lapse (not merely a reporting deadline that nobody needs; not a corpus
  artefact such as wrong in-force date or a consolidation 'Stand' date)?
- retroactive_cure_likely: is it likely the amending act was expressly retroactive (e.g. 'mit Wirkung vom', 'avec effet
  au', 'effective as of', budget laws backdating levies)? Use your knowledge of this system; say so if unsure.
- what_was_possible: concretely, during the gap what could someone do (not pay the levy, plant GM crops, lose/keep an
  exemption, a power unusable)?
- one_line: one plain-English sentence for a non-lawyer.
- strength 1-5 (5 = consequential, crisp, Ringe-style).
Corpus: {corpus}. File: {path}.

TEXT BEFORE (around the old date):
{oc}

TEXT AFTER (around the new date):
{nc}

DIFF OF THE FILE:
{diff}"""


def main() -> None:
    lower_priority()
    run = sys.argv[1] if len(sys.argv) > 1 else "run2"
    f = FINDINGS / run
    rows = json.load(open(f / "late_extension_filtered.json", encoding="utf-8"))
    out = f / "late_extension_triage.jsonl"; lock = threading.Lock()
    I = INDEX.as_posix()

    def work(i, r):
        con = duckdb.connect(); con.execute("set threads to 1")
        ch = con.execute(f"""select ch.old_blob, ch.new_blob from '{I}/changes/{T._repo[r['corpus']]}.parquet' ch
            join '{I}/root.parquet' rr on rr.corpus_commit = ch.commit where ch.path = ? and rr.in_force like ? || '%' and rr.law = ? limit 1""",
                         [r["path"], r["extended_in_force"], r["law"]]).fetchall()
        diff = T.udiff(T.blob(r["corpus"], ch[0][0], 8000), T.blob(r["corpus"], ch[0][1], 8000), 3000) if ch else ""
        res = call(PROMPT.format(old=r["old_until"], new=r["new_until"], law=r["law"], eff=r["extended_in_force"], gap=r["gap_days"],
                                 corpus=r["corpus"], path=r["path"], oc=r["old_context"], nc=r["new_context"], diff=diff),
                   system=T.SYSTEM, schema=SCHEMA, provider="azure-uk" if i % 2 else "azure", max_tokens=1500)
        return {"row": r, "j": res["json"], "tokens": [res["tokens_in"], res["tokens_out"]]}

    with ThreadPoolExecutor(32) as ex, out.open("w", encoding="utf-8") as fh:
        for n, fu in enumerate(as_completed([ex.submit(work, i, r) for i, r in enumerate(rows)]), 1):
            try:
                rec = fu.result()
            except Exception as e:
                print("error:", str(e)[:160], flush=True); continue
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
            if n % 100 == 0:
                print(n, flush=True)


if __name__ == "__main__":
    main()
