"""v2 step 2: gpt-6.1-sol re-reads every v1-accepted case: picks the sub-family (or none), decides/outcome, and for EVERY
factor of that sub-family an explicit present/absent with a supporting quote and the reason flag. Resumable.
-> factors_work/verify2.jsonl"""
import json, os, sys, threading
from concurrent.futures import ThreadPoolExecutor
from common import llm, W, WORK, FAMILIES
V2 = json.load(open(os.path.join(WORK, "vocab2.json"), encoding="utf-8"))
SUBS = [s for fam in FAMILIES for s in V2[fam]]  # global order -> sub-family index 1..N
SIDX = {s["key"]: i + 1 for i, s in enumerate(SUBS)}
SCHEMA = {"type": "object", "properties": {
    "subfamily": {"type": "string"}, "decides": {"type": "boolean"},
    "outcome": {"type": "string", "enum": ["yes", "no", "unclear"]},
    "factors": {"type": "array", "items": {"type": "object", "properties": {
        "id": {"type": "integer"}, "present": {"type": "boolean"}, "quote": {"type": "string"},
        "in_reason": {"type": "boolean"}}, "required": ["id", "present", "quote", "in_reason"]}}},
    "required": ["subfamily", "decides", "outcome", "factors"]}
PROMPT = """You check a factor-based (Horty / HYPO-style) reading of a US Supreme Court opinion. Be strict.

Family: {scope}
Sub-families (each one legal question; "yes" = pi side, "no" = delta side) and their factor vocabularies:
{subs}

Opinion excerpt (the Court's opinion; "[...]" marks omitted text):
<<<
{text}
>>>

1. subfamily: the key of the ONE sub-family whose question the Court actually decides for these parties here, or "none"
   (the opinion decides none of them, or only mentions them).
2. decides: true if it decides that question; outcome: the Court's answer, "yes"/"no" with the polarity as phrased
   ("unclear" if mixed).
3. factors: one entry for EVERY factor id of the chosen sub-family (none if subfamily is "none"):
   - present: true only if the fact situation, as the Court describes it in the excerpt, plainly has that feature per its
     definition. When in doubt, false. Do not stretch a factor to fit by analogy.
   - quote: if present, copy VERBATIM a short span (5-40 words) from the excerpt that shows the fact - exact characters,
     no ellipses, no edits, within one paragraph; if absent, "".
   - in_reason: true only if present AND the Court expressly relies on this fact as a reason for its answer AND it
     favours the side that won. Otherwise false.
"""
def subs_text(fam):
    out = []
    for s in V2[fam]:
        base = SIDX[s["key"]] * 100
        out.append(f"[{s['key']}] {s['scope']}\n  Question: {s['question']}\n" +
                   "\n".join(f"    {base + i + 1} ({f['side']}) {f['name']}: {f['definition']}" for i, f in enumerate(s["factors"])))
    return "\n".join(out)
def main():
    acc = [l.rstrip("\n").split("\t") for l in open(os.path.join(W, "factor_cases.v1.tsv"), encoding="utf-8")]
    ex = {(j["node"], j["family"]): j["excerpt"] for j in map(json.loads, open(os.path.join(WORK, "excerpts.jsonl"), encoding="utf-8"))}
    outp = os.path.join(WORK, "verify2.jsonl")
    done = set()
    if os.path.exists(outp):
        for l in open(outp, encoding="utf-8"):
            try:
                j = json.loads(l)
                if j.get("out") and "error" not in j["out"]:
                    done.add((j["node"], j["family"]))
            except json.JSONDecodeError:
                pass
    lim = int(sys.argv[1]) if sys.argv[1:] else 10 ** 9
    todo = [a for a in acc if (int(a[1]), a[2]) not in done][:lim]
    print("todo", len(todo), flush=True)
    lock = threading.Lock(); fo = open(outp, "a", encoding="utf-8", newline="\n")
    def one(a):
        node, fam = int(a[1]), a[2]
        p = PROMPT.format(scope=FAMILIES[fam][1], subs=subs_text(fam), text=ex[(node, fam)])
        try:
            r, u = llm.call(p, SCHEMA, model="gpt-6.1-sol", max_tokens=6000, job="factor_verify2", reasoning="low")
        except Exception as e:
            r, u = {"error": repr(e)[:200]}, {}
        with lock:
            fo.write(json.dumps({"node": node, "family": fam, "v1_hid": a[0], "out": r, "model": u.get("model"), "usage": u}) + "\n"); fo.flush()
    with ThreadPoolExecutor(120) as exr:
        list(exr.map(one, todo))
    print("done", flush=True)
if __name__ == "__main__":
    main()
