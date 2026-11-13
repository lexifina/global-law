"""Step 3b: gpt-5.4-mini reads each candidate (node, family): does the Court decide the family question here, which
holding states it, the outcome (yes = pi), the vocabulary factors present in the facts, and which of them the Court gave
as its reason. Resumable. -> factors_work/extract.jsonl"""
import json, os, sys, threading
from concurrent.futures import ThreadPoolExecutor
from common import llm, WORK, FAMILIES
SCHEMA = {"type": "object", "properties": {
    "decides": {"type": "boolean"}, "holding_id": {"type": "string"},
    "outcome": {"type": "string", "enum": ["yes", "no", "unclear"]},
    "factors": {"type": "array", "items": {"type": "object", "properties": {
        "id": {"type": "integer"}, "in_reason": {"type": "boolean"}, "evidence": {"type": "string"}},
        "required": ["id", "in_reason", "evidence"]}},
    "confidence": {"type": "number"}}, "required": ["decides", "holding_id", "outcome", "factors", "confidence"]}
PROMPT = """You read a US Supreme Court opinion for factor-based (Horty / HYPO-style) case analysis.

Issue family: {scope}
Question (yes = "pi" side: {pi}; no = "delta" side: {delta}):
  {question}

Factor vocabulary (id, side, name: definition):
{vocab}

Holdings our extractor found in this decision that may concern this family (id: proposition):
{holds}

Opinion excerpt (the Court's opinion; "[...]" marks omitted text):
<<<
{text}
>>>

Answer:
- decides: true only if the Court itself decides the question above for the parties in THIS case (applies it to these
  facts and reaches an answer on it). False if the family is only mentioned, the case turns on another question, or the
  Court only states a general rule without applying it.
- holding_id: the listed holding id that best states the Court's answer to the question ("" if none fits).
- outcome: "yes" or "no" = the Court's answer to the question as phrased above (mind the polarity); "unclear" if mixed.
- factors: every vocabulary factor PRESENT in this case's facts as the Court describes them (use only the ids above; do
  not include factors that are absent). in_reason = true only for factors the Court expressly relies on as a reason for
  its answer (a reason factor must favour the side that won). evidence = a short phrase (<= 20 words) from the excerpt.
- confidence: 0..1 that decides/outcome are right.
"""
lock = threading.Lock()

def vocab_text(v, fam):
    base = FAMILIES[fam][0] * 100
    return "\n".join(f"  {base + i + 1} ({f['side']}) {f['name']}: {f['definition']}" for i, f in enumerate(v["factors"]))

def main():
    vocab = json.load(open(os.path.join(WORK, "vocab.json"), encoding="utf-8"))
    cands = {(c["node"], c["family"]): c for c in map(json.loads, open(os.path.join(WORK, "cands.jsonl"), encoding="utf-8"))}
    exs = [json.loads(l) for l in open(os.path.join(WORK, "excerpts.jsonl"), encoding="utf-8")]
    outp = os.path.join(WORK, "extract.jsonl")
    done = set()
    if os.path.exists(outp):
        for l in open(outp, encoding="utf-8"):
            try:
                j = json.loads(l); done.add((j["node"], j["family"]))
            except json.JSONDecodeError:
                pass
    lim = int(sys.argv[1]) if sys.argv[1:] else 10 ** 9
    todo = [e for e in exs if (e["node"], e["family"]) not in done and e["family"] in vocab][:lim]
    print("todo", len(todo), flush=True)
    fo = open(outp, "a", encoding="utf-8", newline="\n")
    def one(e):
        fam = e["family"]; v = vocab[fam]; c = cands[(e["node"], fam)]
        holds = "\n".join(f"  {h['id']}: {h['prop']}" for h in c["holdings"][:8])
        p = PROMPT.format(scope=FAMILIES[fam][1], pi=v["pi_side"], delta=v["delta_side"], question=v["question"],
                          vocab=vocab_text(v, fam), holds=holds, text=e["excerpt"])
        try:
            r, u = llm.call(p, SCHEMA, model="gpt-5.4-mini", max_tokens=2500, job="factor_extract")
        except Exception as ex:
            r, u = {"error": repr(ex)[:200]}, {}
        rec = {"node": e["node"], "family": fam, "out": r, "model": u.get("model")}
        with lock:
            fo.write(json.dumps(rec) + "\n"); fo.flush()
    with ThreadPoolExecutor(48) as ex:
        list(ex.map(one, todo))
    print("done")
main()
