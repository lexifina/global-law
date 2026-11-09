"""Model review against the taxonomy: each selected flag gets a category and a verdict from the written definitions
(taxonomy.py), with the provision's text (and the cited provision's) as evidence. Candidates then face a second model
that argues against them; only survivors stay 'candidate'.

python triage/taxonomy_review.py RUN FLAGS.parquet [--budget N]  -> findings/RUN/taxonomy_review.jsonl (resumable by id)

Selection (most valuable first, within the budget): every flag in A2, A3, B3, C2, C4; every unreviewed B1, B2, A4 flag
by score; A1 by score; then a fixed sample of every other category so its error rate is measured, not assumed.
"""
from __future__ import annotations
import argparse, json, random, re, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "ingest")); sys.path.insert(0, str(Path(__file__).parent))
import duckdb  # noqa: E402
import taxonomy as T  # noqa: E402
from common import CORPUS, FINDINGS, FLAGS, pins  # noqa: E402
from llm import call  # noqa: E402

ALL = ("A2", "A3", "B3", "C2", "C4")
BY_SCORE = ("B1", "B2", "A4", "A1")
SAMPLE = {"D1": 60, "D2": 60, "E1": 80, "E2": 60, "E3": 60, "E4": 80, "E5": 60, "C1": 30}

REVIEW = {"type": "object", "additionalProperties": False,
          "required": ["category", "verdict", "effect", "confidence", "one_line", "reason"],
          "properties": {"category": {"type": "string", "enum": sorted(T.C) + ["NONE"]},
                         "verdict": {"type": "string", "enum": ["candidate", "not_a_defect", "corpus_error", "detector_error"]},
                         "effect": {"type": "string", "enum": sorted(T.EFFECTS)}, "confidence": {"type": "number"},
                         "one_line": {"type": "string"}, "reason": {"type": "string"}}}
REBUT = {"type": "object", "additionalProperties": False, "required": ["survives", "strongest_objection", "confidence"],
         "properties": {"survives": {"type": "boolean"}, "strongest_objection": {"type": "string"}, "confidence": {"type": "number"}}}
SYSTEM = ("You review machine-found candidate defects in national legislation for theoretical research. Be strict and "
          "concrete; prefer 'not_a_defect', 'corpus_error' or 'detector_error' unless the text itself shows the defect.")
PROMPT = """Taxonomy (use these definitions; their includes/excludes decide boundaries):
{defs}

Verdicts: candidate = the text shows a defect of that category; not_a_defect = real text but lawful, cured, favourable or
harmless; corpus_error = the corpus is wrong (date, attribution, missing text); detector_error = the corpus is right but the
detector misread it (another act's section, a sub-unit, a heading, a note).

FLAG
category proposed by the detector: {code} {cname}
jurisdiction: {jur}  · provision: {path}  · date: {date}
reference / instrument: {ref}
what was flagged: {summary}

TEXT OF THE PROVISION (current, at the pinned commit):
{text}

TEXT OF THE CITED PROVISION (if found):
{target}

Give the category this flag actually alleges (it may differ from the proposal), your verdict, the effect if real, and a
one-line plain-English statement a non-lawyer would understand."""
REBUT_PROMPT = """Another reviewer says this is a real defect. Argue against it as strongly as the evidence allows
(transitional rules, substitution or conversion clauses, a successor provision courts would read in, a different reading
of the reference, a corpus or parsing error, case law). survives = true only if no objection is likely to defeat it.

Category: {code} {cname}. Claim: {one_line}
Reviewer's reasoning: {reason}

TEXT OF THE PROVISION:
{text}

TEXT OF THE CITED PROVISION:
{target}"""


def definitions():
    return "\n".join(f"{c} {d['name']}: {d['definition']} Excludes: {'; '.join(d['exclude']) or '-'}" for c, d in T.C.items())


def show(repo, sha, path, n=5000):
    if not path or path.startswith("http"):
        return ""
    p = subprocess.run(["git", "-C", str(CORPUS / f"{repo}.git"), "show", f"{sha}:{path}"], capture_output=True, creationflags=FLAGS)
    return p.stdout.decode("utf-8", "replace")[:n] if p.returncode == 0 else ""


def select(rows, budget):
    random.seed(17)
    by = {}
    for r in rows:
        by.setdefault(r["taxonomy"], []).append(r)
    chosen = []
    for code in ALL:
        chosen += by.get(code, [])
    for code in BY_SCORE:
        rs = [r for r in by.get(code, []) if not r["review"]]
        chosen += sorted(rs, key=lambda r: -(r["score"] or 0))
    for code, n in SAMPLE.items():
        rs = by.get(code, [])
        chosen += random.sample(rs, min(n, len(rs)))
    seen, out = set(), []
    for r in chosen:
        if r["id"] not in seen:
            seen.add(r["id"]); out.append(r)
    # keep every A-family 'ALL' item and the samples; cut the score-ranked tails to the budget
    head = [r for r in out if r["taxonomy"] in ALL or r["taxonomy"] in SAMPLE]
    tail = [r for r in out if r not in head]
    return head + tail[: max(0, budget - len(head))]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("flags"); ap.add_argument("--budget", type=int, default=6000)
    ap.add_argument("--workers", type=int, default=24)
    a = ap.parse_args()
    rel = duckdb.sql(f"select * from '{Path(a.flags).as_posix()}'"); cols = rel.columns
    rows = [dict(zip(cols, r)) for r in rel.fetchall()]
    picked = select(rows, a.budget)
    out = FINDINGS / a.run / "taxonomy_review.jsonl"
    done = set()
    if out.exists():
        for l in out.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(l)["id"])
            except ValueError:
                pass
    todo = [r for r in picked if r["id"] not in done]
    print(f"{len(picked)} selected, {len(todo)} to review", flush=True)
    repo = {c["path"]: (c["repo"], c["sha"]) for c in pins()["corpora"]}
    defs = definitions(); lock = threading.Lock()

    def work(i, r):
        rp, sha = repo.get(r["corpus"], ("", ""))
        text = show(rp, sha, r["path"]) if rp else ""
        tgt = ""
        m = re.search(r"→\s*(\S+\.md)", r["reference"] or "")
        if m and rp:
            tgt = show(rp, sha, m.group(1), 1500)
        code = r["taxonomy"]
        res = call(PROMPT.format(defs=defs, code=code, cname=T.C.get(code, {}).get("name", ""), jur=r["jurisdiction"],
                                 path=r["path"], date=r["date"], ref=r["reference"], summary=r["summary"],
                                 text=text or "(not available)", target=tgt or "(not found)"),
                   system=SYSTEM, schema=REVIEW, provider="azure-uk" if i % 2 else "azure", max_tokens=1500)
        j = res["json"]; rec = {"id": r["id"], "detector": r["detector"], "proposed": code, **j,
                                "tokens": [res["tokens_in"], res["tokens_out"]]}
        if j["verdict"] == "candidate" and j["category"] in T.C:
            rb = call(REBUT_PROMPT.format(code=j["category"], cname=T.C[j["category"]]["name"], one_line=j["one_line"],
                                          reason=j["reason"], text=text or "(not available)", target=tgt or "(not found)"),
                      system=SYSTEM, schema=REBUT, provider="azure" if i % 2 else "azure-uk", max_tokens=1200)
            rec["rebut"] = rb["json"]
            rec["final_verdict"] = "candidate" if rb["json"]["survives"] else "not_a_defect"
            rec["review_label"] = "candidate_defect, survived rebuttal" if rb["json"]["survives"] else "candidate_defect, rebutted"
        else:
            rec["final_verdict"] = j["verdict"]; rec["review_label"] = j["verdict"]
        if j["category"] == "NONE":
            rec["category"] = None
        return rec

    with ThreadPoolExecutor(a.workers) as ex, out.open("a", encoding="utf-8") as fh:
        for n, fu in enumerate(as_completed([ex.submit(work, i, r) for i, r in enumerate(todo)]), 1):
            try:
                rec = fu.result()
            except Exception as e:
                print("error:", str(e)[:160], flush=True); continue
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
            if n % 200 == 0:
                print(n, flush=True)
    print("finished", flush=True)


if __name__ == "__main__":
    main()
