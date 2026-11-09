"""delegation_deadline: a decree made under delegated legislative power (Spain RDLeg art. 82 CE; Peru decreto legislativo
art. 104; Colombia decreto-ley art. 150.10; Chile DFL art. 64; Argentina decreto delegado art. 76) signed after the
delegation expired, or outside its scope.

python triage/delegation_deadline.py RUN -> findings/RUN/delegation_deadline.jsonl
"""
from __future__ import annotations
import csv, io, json, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import FINDINGS, CORPUS, FLAGS, pins, lower_priority
from llm import call
import triage as T

SCHEMA = {"type": "object", "additionalProperties": False, "required": [
    "instrument", "instrument_date", "delegating_provision", "delegation_text_quoted", "deadline_rule",
    "delegating_act_in_force", "extensions", "deadline_date", "days_late", "scope_problem", "verdict", "reason", "confidence"],
    "properties": {
        "instrument": {"type": "string"}, "instrument_date": {"type": "string"},
        "delegating_provision": {"type": "string"}, "delegation_text_quoted": {"type": "string"},
        "deadline_rule": {"type": "string"}, "delegating_act_in_force": {"type": "string"},
        "extensions": {"type": "string"}, "deadline_date": {"type": "string"}, "days_late": {"type": "integer"},
        "scope_problem": {"type": "string"},
        "verdict": {"type": "string", "enum": ["late", "on_time", "scope_excess", "cannot_tell"]},
        "reason": {"type": "string"}, "confidence": {"type": "number"}}}

PROMPT = """This instrument was made by the executive under a power delegated by the legislature. The constitution
requires the delegation to have a fixed time limit (and a defined scope); a decree signed after the limit is ultra vires.
From the text below (and your knowledge of the delegating law, flagged as such), determine:
- the delegating provision and quote its time limit exactly if the text gives it;
- when the delegating act entered into force, any extensions of the period;
- the deadline date and whether the instrument date ({date}) is after it (days_late > 0 means late; 0 if on time).
Also note any obvious scope excess the text itself admits. If the text does not state the limit and you are unsure,
answer cannot_tell. Do not guess dates.

INSTRUMENT: {title}
DATE OF THE INSTRUMENT: {date}

TEXT (preamble / enacting formula / approving decree):
{text}"""


def show(repo, sha, path, n=9000):
    p = subprocess.run(["git", "-C", str(CORPUS / f"{repo}.git"), "show", f"{sha}:{path}"], capture_output=True, creationflags=FLAGS)
    return p.stdout.decode("utf-8", "replace")[:n] if p.returncode == 0 else ""


def spain():
    c = [c for c in pins()["corpora"] if c["repo"] == "spain-law"][0]
    tsv = show("spain-law", c["sha"], "normas.tsv", 10 ** 9)
    for n in csv.DictReader(io.StringIO(tsv), delimiter="\t"):
        if n["rango"] == "Real Decreto Legislativo":
            t = show("spain-law", c["sha"], n["path"] + "/preambulo.md") + "\n" + show("spain-law", c["sha"], n["path"] + "/aunico.md", 3000)
            if t.strip():
                yield {"corpus": c["path"], "id": n["id"], "title": n["titulo"], "date": n["fecha_disposicion"],
                       "in_force_now": n["vigencia_agotada"] == "N", "text": t}


def main() -> None:
    lower_priority()
    run = sys.argv[1] if len(sys.argv) > 1 else "run2"
    out = FINDINGS / run / "delegation_deadline.jsonl"
    items = list(spain())
    print(len(items), "instruments", flush=True)
    lock = threading.Lock()

    def work(i, it):
        res = call(PROMPT.format(title=it["title"], date=it["date"], text=it["text"]), system=T.SYSTEM, schema=SCHEMA,
                   provider="azure-uk" if i % 2 else "azure", max_tokens=2500)
        return {**{k: v for k, v in it.items() if k != "text"}, "j": res["json"], "tokens": [res["tokens_in"], res["tokens_out"]]}

    with ThreadPoolExecutor(24) as ex, out.open("a", encoding="utf-8") as fh:
        for fu in as_completed([ex.submit(work, i, it) for i, it in enumerate(items)]):
            try:
                r = fu.result()
            except Exception as e:
                print("error:", str(e)[:200], flush=True); continue
            with lock:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n"); fh.flush()
                print(r["j"]["verdict"], r["j"]["days_late"], r["title"][:90], flush=True)


if __name__ == "__main__":
    main()
