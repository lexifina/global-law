"""Triage placeholder_ref: is it a real live reference to a repealed provision of the same act, and what breaks?
python triage/placeholder_triage.py RUN -> findings/RUN/placeholder_triage.jsonl"""
from __future__ import annotations
import json, re, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import FINDINGS, CORPUS, FLAGS, pins, lower_priority
from llm import call
import triage as T

SHA = {c["repo"]: c["sha"] for c in pins()["corpora"]}
SCHEMA = {"type": "object", "additionalProperties": False, "required": [
    "same_act_reference", "live_operative_text", "what_breaks", "cure", "kind", "one_line", "verdict", "strength", "confidence"],
    "properties": {
        "same_act_reference": {"type": "boolean"}, "live_operative_text": {"type": "boolean"},
        "what_breaks": {"type": "string"}, "cure": {"type": "string"},
        "kind": {"type": "string", "enum": ["fine or offence unenforceable", "right or exemption unusable", "power or duty points nowhere",
                                             "definition or condition empty", "harmless or cosmetic", "other"]},
        "one_line": {"type": "string"},
        "verdict": {"type": "string", "enum": ["candidate_defect", "harmless", "artefact"]},
        "strength": {"type": "integer"}, "confidence": {"type": "number"}}}
PROMPT = """A provision currently in force refers to another provision that, in the corpus, is now only a repeal
placeholder. Decide:
- same_act_reference: does the reference really point to that provision of the SAME act (not another law's article
  with the same number, not a sub-number like 141.5 of a different statute)?
- live_operative_text: is the citing text operative law in force (not a note, amendment instruction, history, index,
  transitional text that intentionally refers to old law)?
- what_breaks, concretely; cure: a renumbering, a general clause, an obvious successor provision courts would read in.
- kind; one_line in plain English for a non-lawyer ("You can be fined for X under § Y, but § Y was repealed in Z").
- strength 1-5: 5 = a clean logical mistake with real consequences (an unenforceable fine, a right nobody can use).
Corpus {corpus}.

CITING PROVISION ({path}):
{text}

REFERENCED PROVISION ({target}), current text:
{target_text}"""


def show(repo, path, n):
    p = subprocess.run(["git", "-C", str(CORPUS / f"{repo}.git"), "show", f"{SHA[repo]}:{path}"], capture_output=True, creationflags=FLAGS)
    return p.stdout.decode("utf-8", "replace")[:n]


def main() -> None:
    lower_priority()
    run = sys.argv[1] if len(sys.argv) > 1 else "run2"
    f = FINDINGS / run
    rows = json.load(open(f / "placeholder_ref_filtered.json", encoding="utf-8"))
    rows = [r for r in rows if "Source:" not in r["context"] and "Stats." not in r["context"]]
    rows = [r for r in rows if r["penal"] or r["repo"] not in ("united-states-california-law", "france-law", "spain-law", "armenia-law")]
    seen, keep = set(), []
    for r in rows:
        k = (r["path"], r["ref"])
        if k not in seen:
            seen.add(k); keep.append(r)
    print(len(keep), "to judge", flush=True)
    out = f / "placeholder_triage.jsonl"; lock = threading.Lock()

    def work(i, r):
        res = call(PROMPT.format(corpus=r["corpus"], path=r["path"], text=show(r["repo"], r["path"], 5000), target=r["target"],
                                 target_text=show(r["repo"], r["target"], 1500)),
                   system=T.SYSTEM, schema=SCHEMA, provider="azure-uk" if i % 2 else "azure", max_tokens=1500)
        return {"row": r, "j": res["json"], "tokens": [res["tokens_in"], res["tokens_out"]]}

    with ThreadPoolExecutor(32) as ex, out.open("w", encoding="utf-8") as fh:
        for n, fu in enumerate(as_completed([ex.submit(work, i, r) for i, r in enumerate(keep)]), 1):
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
