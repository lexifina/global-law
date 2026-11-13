"""Step 3 of the split pipeline: choose the interpretive decisions per subsection, and read each one's holdings on that
subsection as yes/no questions (gpt-5.4-mini), from numbered sentences of the citation windows.

    python splits_extract.py [--per 45] [--scotus 12] [--threads 40]
reads data/holdings_work/split_windows.jsonl + split_subsections.tsv; writes data/holdings_work/raw_splits.jsonl
(resumable by (key, nid)).
"""
import collections, json, os, sys, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core, llm, text

OUT = os.path.join(text.WORK, "caselaw-lean-2", "data", "holdings_work")
CIRC = {1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth", 6: "Sixth", 7: "Seventh", 8: "Eighth", 9: "Ninth",
        10: "Tenth", 11: "Eleventh", 12: "D.C.", 13: "Federal", 0: "Supreme Court"}

SYSTEM = """You read passages of a US court opinion that cite one US Code subsection, and say what this court HOLDS about that subsection's meaning or legal rule.
You get the subsection's text and numbered sentences from the opinion (only this court's own opinion).
1. interprets: true only if this court itself decides a question about what the subsection means or requires (its elements, scope, a term's meaning, who/what it covers, the standard it sets, how it interacts with another provision). Citing it in passing, reciting a standard without deciding anything contested, or only applying settled law to facts is false.
2. For each such holding (at most 3), state it as a general yes/no QUESTION about the subsection that any federal court of appeals could answer, without party names or case facts (e.g. "Does 18 U.S.C. 924(c)(3)(B)'s residual clause apply to conspiracy to commit Hobbs Act robbery?" or "Is attempted Hobbs Act robbery a crime of violence under 18 U.S.C. 924(c)(3)(A)?"), and this court's ANSWER (yes or no). Phrase the question at the level of generality at which courts disagree, not tied to one record.
Give s = the id of the sentence that states the holding most directly; kind = holding | alternative; proposition = the holding as a rule (<= 300 chars); confidence 0-1 that this is the court's own holding (not dicta, not a description of another court's view) and the answer is right.
3. conflict: true if the passages say other circuits disagree or are divided on the question."""

SCOTUS_EXTRA = """
This is a US Supreme Court decision. Also give resolves_conflict: true if the Court says it took the case to resolve a conflict or split among the courts of appeals (or the passages describe such a split it resolves), and conflict_question: that question as a yes/no question in the same style ("" if none)."""

SCHEMA = {"type": "object", "properties": {
    "interprets": {"type": "boolean"}, "conflict": {"type": "boolean"},
    "resolves_conflict": {"type": "boolean"}, "conflict_question": {"type": "string"},
    "holdings": {"type": "array", "items": {"type": "object", "properties": {
        "s": {"type": "integer"}, "question": {"type": "string"}, "answer": {"type": "string", "enum": ["yes", "no"]},
        "kind": {"type": "string", "enum": ["holding", "alternative"]}, "proposition": {"type": "string"},
        "confidence": {"type": "number"}}, "required": ["s", "question", "answer", "kind", "proposition", "confidence"]}}},
    "required": ["interprets", "holdings", "conflict"]}


def select(per, nsc):
    by = collections.defaultdict(list)
    for l in open(os.path.join(OUT, "split_windows.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r["cues"] + r["splitcues"] == 0:
            continue
        by[r["key"]].append(r)
    chosen = []
    for key, rs in by.items():
        sc = sorted((r for r in rs if r["kind"] == 0), key=lambda r: -r["score"])[:nsc]
        circ = collections.defaultdict(list)
        for r in sorted((r for r in rs if r["kind"] != 0), key=lambda r: -r["score"]):
            circ[r["kind"]].append(r)
        pick = []
        while len(pick) < per and any(circ.values()):
            for c in sorted(circ, key=lambda c: -(circ[c][0]["score"] if circ[c] else -99)):
                if circ[c] and len(pick) < per:
                    pick.append(circ[c].pop(0))
        chosen += sc + pick
    return chosen


def prep(nid, raw):
    return (nid, text.norm_text(raw))


def main():
    a = sys.argv[1:]
    per, nsc, threads = 45, 12, 40
    for flag in ("--per", "--scotus", "--threads"):
        if flag in a:
            i = a.index(flag); v = int(a[i + 1]); del a[i:i + 2]
            per, nsc, threads = (v, nsc, threads) if flag == "--per" else (per, v, threads) if flag == "--scotus" else (per, nsc, v)
    subs = {}
    for l in open(os.path.join(OUT, "split_subsections.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        subs[f[1]] = (f[4], f[5])
    chosen = select(per, nsc)
    path = os.path.join(OUT, "raw_splits.jsonl")
    done = set()
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            r = json.loads(l)
            if "error" not in (r.get("out") or {}):
                done.add((r["key"], r["nid"]))
    chosen = [r for r in chosen if (r["key"], r["nid"]) not in done]
    print("todo", len(chosen), "done", len(done), flush=True)
    by_nid = collections.defaultdict(list)
    for r in chosen:
        by_nid[r["nid"]].append(r)
    lock = threading.Lock()
    sem = threading.Semaphore(threads * 4)

    with open(path, "a", encoding="utf-8", newline="\n") as fo, ThreadPoolExecutor(threads) as ex:
        def go(r, t):
            try:
                head, body = subs.get(r["key"], ("", ""))
                lines = "\n".join(f"[{i}] {core.show(t, a, z, 900)}" for i, (a, z) in enumerate(r["sents"]))
                prompt = (f"Subsection: {r['key']} — {head}\nText: {body[:900]}\n\nCourt: {CIRC[r['kind']]}"
                          f"{' Circuit' if r['kind'] else ''}, decided {r['date']}\n\nSentences:\n{lines}\n\nReturn JSON.")
                try:
                    out, usage = llm.call(prompt, SCHEMA, SYSTEM + (SCOTUS_EXTRA if r["kind"] == 0 else ""),
                                          max_tokens=1200, job="splits-extract")
                except Exception as e:
                    out, usage = {"error": str(e)[:200]}, {}
                rec = {k: r[k] for k in ("key", "nid", "kind", "date", "sha", "unpub", "score", "sents")}
                rec.update(out=out, model=usage.get("model", ""))
                with lock:
                    fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    fo.flush()
            finally:
                sem.release()

        for res in text.map_nodes(sorted(by_nid), prep, procs=3, chunk=3000):
            if res[0] == "__error__":
                continue
            nid, t = res
            for r in by_nid[nid]:
                sem.acquire()
                ex.submit(go, r, t)
    print("finished")


if __name__ == "__main__":
    main()
