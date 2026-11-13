"""Marks narrowest-ground rows for fragmented Supreme Court decisions (no single rationale joined by a majority).

    python marks.py [--model gpt-6.1-sol]
reads raw_scotus.jsonl (form == plurality, plus decisions2.tsv form == plurality when the courts agent has written it),
writes data/holdings_work/raw_marks.jsonl: {nid, out: {majority_issues: [...], marks: [{issue, author, proposition, basis}]}}
"""
import json, os, re, sys, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core, llm, text

OUT = os.path.join(text.WORK, "caselaw-lean-2", "data", "holdings_work")
D2 = os.path.join(text.WORK, "caselaw-lean-2", "data", "decisions2.tsv")
SYSTEM = """You apply the Marks rule (Marks v. United States, 430 U.S. 188, 193 (1977)) to a fragmented US Supreme Court decision: "When a fragmented Court decides a case and no single rationale explaining the result enjoys the assent of five Justices, the holding of the Court may be viewed as that position taken by those Members who concurred in the judgments on the narrowest grounds."
You get the opening of each opinion (author, joins, which Parts are the opinion of the Court) and key sentences from each, plus the holdings already read from the lead opinion, each with an issue key.
1. majority_issues: issue keys whose holding is in a Part that is the opinion of the Court (joined by a majority), so no Marks analysis is needed.
2. For each issue the judgment depends on that lacks a majority rationale, give: issue (an issue key from the list, or "new:<short label>"), author (surname of the Justice whose opinion concurring in the judgment rests on the narrowest grounds — the plurality author if the plurality's ground is the narrowest), proposition (the narrowest-ground holding, <= 300 chars), basis (one sentence: why it is the narrowest, e.g. a logical subset of the other concurring rationales), and logical_subset (true if that rationale is a logical subset of every other opinion concurring in the judgment; false if the opinions share no common denominator and only the result binds).
If the decision in fact has a majority opinion on every issue, return marks = []."""
SCHEMA = {"type": "object", "properties": {
    "majority_issues": {"type": "array", "items": {"type": "string"}},
    "marks": {"type": "array", "items": {"type": "object", "properties": {
        "issue": {"type": "string"}, "author": {"type": "string"}, "proposition": {"type": "string"}, "basis": {"type": "string"},
        "logical_subset": {"type": "boolean"}}, "required": ["issue", "author", "proposition", "basis", "logical_subset"]}}},
    "required": ["majority_issues", "marks"]}


def opinions(t):
    out = []
    for name, b, e in core.sections(t):
        n = name.lower()
        if n.startswith(("head matter", "cap head matter")):
            continue
        sents = core.split_sentences(t, b, e)
        strong = [s for s in sents if core.STRONG.search(t[s[0]:s[1]]) or re.search(r"(?i)narrow|concur in the judgment|would hold", t[s[0]:s[1]])]
        out.append((name, core.show(t, b, min(e, b + 700), 700), [core.show(t, a, z, 400) for a, z in strong[:7]]))
    return out


def main():
    a = sys.argv[1:]
    model = "gpt-6.1-sol"
    if "--model" in a:
        i = a.index("--model"); model = a[i + 1]; del a[i:i + 2]
    hold = {}
    allh = {}
    for g in ("scotus", "scotus_mini", "scotus_luna", "scotus_plur"):
        p = os.path.join(OUT, f"raw_{g}.jsonl")
        if not os.path.exists(p):
            continue
        for l in open(p, encoding="utf-8"):
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            if "error" not in (r.get("out") or {}):
                allh[r["nid"]] = (r.get("out") or {}).get("holdings") or []
                if r.get("form") == "plurality":
                    hold[r["nid"]] = allh[r["nid"]]
    scotus_done = set()
    for g in ("scotus", "scotus_mini", "scotus_luna", "scotus_plur"):
        p = os.path.join(OUT, f"raw_{g}.jsonl")
        if os.path.exists(p):
            for l in open(p, encoding="utf-8"):
                try:
                    scotus_done.add(json.loads(l)["nid"])
                except json.JSONDecodeError:
                    pass
    # head-matter / opinion cues from the full scan (scan_scotus.py), which reads the syllabus line naming the opinions
    for l in open(os.path.join(OUT, "scotus_scan.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        if f[5] == "plurality" and f[6] != "-" and not f[6].lower().startswith("plurality opinion") and int(f[0]) in scotus_done:
            hold.setdefault(int(f[0]), [])
    if os.path.exists(D2):
        for l in open(D2, encoding="utf-8"):
            f = l.rstrip("\n").split("\t")
            if len(f) > 6 and f[6] == "plurality" and f[1] == "2906" and int(f[0]) in scotus_done:
                hold.setdefault(int(f[0]), [])
    for n in hold:
        if not hold[n] and n in allh:
            hold[n] = allh[n]
    path = os.path.join(OUT, "raw_marks.jsonl")
    done = {json.loads(l)["nid"] for l in open(path, encoding="utf-8")} if os.path.exists(path) else set()
    todo = [n for n in sorted(hold) if n not in done]
    print("plurality decisions", len(hold), "todo", len(todo), flush=True)
    texts = text.fetch(todo)
    lock = threading.Lock()
    with open(path, "a", encoding="utf-8", newline="\n") as fo:
        def go(nid):
            raw = texts.get(nid)
            if raw is None:
                return
            t = text.norm_text(raw)
            ops = opinions(t)
            hl = "\n".join(f"- h{i}: [{h['issue']}] {h['proposition']}" for i, h in enumerate(hold[nid]))
            body = "\n\n".join(f"### {n}\nOpening: {op}\nKey sentences:\n" + "\n".join("  - " + s for s in ss) for n, op, ss in ops)
            prompt = f"Case: {core.front(t, 'parties')[:200]} ({core.front(t, 'decided')})\n\nLead-opinion holdings (issue keys h0, h1, ...):\n{hl or '(none read)'}\n\nOpinions:\n{body[:24000]}\n\nReturn JSON."
            try:
                out, u = llm.call(prompt, SCHEMA, SYSTEM, model=model, max_tokens=6000, job="marks")
            except Exception as e:
                print("error", nid, e, flush=True)
                return
            with lock:
                fo.write(json.dumps({"nid": nid, "model": u.get("model"), "out": out}, ensure_ascii=False) + "\n")
                fo.flush()
        with ThreadPoolExecutor(32) as ex:
            list(ex.map(go, todo))
    print("finished")


if __name__ == "__main__":
    main()
