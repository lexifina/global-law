"""Case files for the strongest survivors, in Ringe & Folkerts' shape, by a stronger model (gpt-6-astra, UK, <=3 at once).

python triage/casefile.py RUN [--min 0.5]
-> findings/RUN/casefiles.jsonl (resumable by id)
"""
from __future__ import annotations
import argparse, json, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import duckdb
from common import FINDINGS, INDEX
from llm import call
import triage as T

SCHEMA = {"type": "object", "additionalProperties": False, "required": [
    "title", "requires", "but", "consequence", "exploit", "follow_ups", "holds", "confidence", "verify_first"],
    "properties": {
        "title": {"type": "string"},
        "requires": {"type": "string"},
        "but": {"type": "string"},
        "consequence": {"type": "string"},
        "exploit": {"type": "string"},
        "follow_ups": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                       "required": ["argument", "rating"], "properties": {
                           "argument": {"type": "string"},
                           "rating": {"type": "string", "enum": ["highly unlikely", "unlikely", "plausible", "likely"]}}}},
        "holds": {"type": "boolean"},
        "confidence": {"type": "number"},
        "verify_first": {"type": "array", "items": {"type": "string"}}}}
PROMPT = """Write a case file for this candidate legal vulnerability, in this shape:
- requires: the rule of this legal system that the text must satisfy (cite it precisely)
- but: what the text / record actually shows
- consequence: what follows legally if the defect is real (void, inapplicable, unenforceable, gap, ...)
- exploit: one concrete, realistic scenario of who gains what
- follow_ups: the strongest counterarguments (transitional rules, curing amendments, implied repeal, interpretation,
  EU or constitutional law, case law, corpus error), each rated by how likely it defeats the claim
- holds: true only if every follow-up is 'unlikely' or 'highly unlikely'
- verify_first: what to check in official sources before relying on it
Theoretical research. Two earlier analysts' views are included; do not defer to them.

EVIDENCE
{ev}

ANALYST 1 (claims a defect)
{v}

ANALYST 2 (argues against)
{r}"""


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("run"); ap.add_argument("--min", type=float, default=0.5)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--deepen", action="store_true", help="re-run tier-B cases with the instrument's full text")
    a = ap.parse_args()
    f = FINDINGS / a.run
    out = f / ("casefiles_deep.jsonl" if a.deepen else "casefiles.jsonl")
    done = set()
    if out.exists():
        for l in out.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(l)["id"])
            except ValueError:
                pass
    recs = []
    for l in (f / "triage.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(l)
        except ValueError:
            continue
        rb = r.get("rebut") or {}
        if rb.get("survives") and (rb.get("remaining_confidence") or 0) >= a.min and r["id"] not in done:
            recs.append(r)
    recs = list({r["id"]: r for r in recs}.values())
    if a.deepen:
        import collections
        first = {}
        for l in (f / "casefiles.jsonl").read_text(encoding="utf-8").splitlines():
            try:
                c = json.loads(l); first[c["id"]] = c
            except ValueError:
                pass
        def tier_b(c):
            r = collections.Counter(x["rating"] for x in c["case"]["follow_ups"])
            return r["likely"] == 0
        recs = [r for r in recs if r["id"] in first and tier_b(first[r["id"]])]
    print(f"{len(recs)} survivors to write up", flush=True)
    lock = threading.Lock()

    def work(r):
        con = duckdb.connect()
        con.execute("set threads to 2")
        con.execute(f"create view changes as select * from '{(INDEX/'changes'/(T._repo[r['corpus']] + '.parquet')).as_posix()}'")
        con.execute(f"create view root as select * from '{(INDEX/'root.parquet').as_posix()}'")
        row = dict(r["row"])
        for k in ("laws", "still_in"):
            if isinstance(row.get(k), str) and row[k].startswith("["):
                try:
                    row[k] = json.loads(row[k].replace("'", '"'))
                except ValueError:
                    pass
        ev = T.evidence(con, r["detector"], row)
        if a.deepen:
            # every current file of the instrument's folder(s): all articles, visas, preamble
            paths = con.execute("""select distinct ch.path from changes ch join root rr on rr.corpus_commit = ch.commit
                where rr.corpus = ? and (rr.law = ? or ch.path = ?)""", [r["corpus"], row.get("law") or "", row.get("path") or ""]).fetchall()
            folders = sorted({p[0].rsplit("/", 1)[0] for p in paths})[:3]
            full = []
            for fo in folders:
                cur = con.execute("""select ch.path, arg_max(ch.new_blob, rr.in_force), arg_max(left(ch.status,1), rr.in_force)
                    from changes ch join root rr on rr.corpus_commit = ch.commit where ch.path like ? group by 1 order by 1""",
                    [fo + "/%"]).fetchall()
                for pth, b, st in cur[:40]:
                    if st != "D":
                        full.append(f"--- {pth}\n" + T.blob(r["corpus"], b, 2500))
            ev += "\n\nFULL TEXT OF THE INSTRUMENT (current files in its folder):\n" + "\n".join(full)[:14000]
        res = call(PROMPT.format(ev=ev, v=json.dumps(r["verify"], ensure_ascii=False), r=json.dumps(r["rebut"], ensure_ascii=False)),
                   system=T.SYSTEM, schema=SCHEMA, provider="azure-uk", model="gpt-6-astra", max_tokens=6000)
        return {"id": r["id"], "detector": r["detector"], "corpus": r["corpus"], "row": r["row"], "case": res["json"],
                "tokens": [res["tokens_in"], res["tokens_out"]]}

    n = 0
    with ThreadPoolExecutor(a.workers) as ex:
        for fu in as_completed([ex.submit(work, r) for r in recs]):
            try:
                rec = fu.result()
            except Exception as e:
                print("error:", str(e)[:200], flush=True); continue
            with lock:
                with out.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
                print(f"{n}/{len(recs)} {rec['corpus']} holds={rec['case']['holds']} conf={rec['case']['confidence']}", flush=True)
    print("finished", flush=True)


if __name__ == "__main__":
    main()
