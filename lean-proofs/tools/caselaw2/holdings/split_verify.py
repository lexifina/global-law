"""Second reading of every split holding on an issue that two or more courts of appeals (or the Supreme Court) answered:
gpt-6.1-sol reads the quoted sentence in its +-400-character window against the canonical question and says whether it
is this court's own holding on that question, and the answer. assemble.py then drops rows the verifier rejects and
takes the verifier's answer.

    python split_verify.py [--model gpt-6.1-sol] [--threads 80]
reads data/holdings.tsv, issues.tsv, holdings_cert_text.tsv, raw_splits.jsonl (court of each node);
writes data/holdings_work/split_verify.jsonl: {hid, own_holding, answer, confidence, model}
"""
import collections, json, os, sys, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm, text

DATA = os.path.join(text.WORK, "caselaw-lean-2", "data")
OUT = os.path.join(DATA, "holdings_work")
CIRC = {0: "the US Supreme Court", 1: "1st Cir.", 2: "2d Cir.", 3: "3d Cir.", 4: "4th Cir.", 5: "5th Cir.", 6: "6th Cir.",
        7: "7th Cir.", 8: "8th Cir.", 9: "9th Cir.", 10: "10th Cir.", 11: "11th Cir.", 12: "D.C. Cir.", 13: "Fed. Cir."}
SYSTEM = """You check one claimed holding of a US federal court on a yes/no statutory question.
You get the question and a passage of the court's opinion with one sentence marked <<< >>>.
own_holding: true only if the marked sentence (read with its context) is THIS court's own ruling that answers the question, as a holding (including an alternative holding). False if it recites a standard without deciding the question, describes another court's or the Supreme Court's view without adopting it here, states a party's argument, assumes without deciding, leaves the question open, or answers a materially different question.
answer: this court's answer to the question as asked: yes | no | not_decided.
confidence: 0-1."""
SCHEMA = {"type": "object", "properties": {"own_holding": {"type": "boolean"},
                                           "answer": {"type": "string", "enum": ["yes", "no", "not_decided"]},
                                           "confidence": {"type": "number"}}, "required": ["own_holding", "answer", "confidence"]}


def main():
    a = sys.argv[1:]
    model, threads = "gpt-6.1-sol", 80
    if "--model" in a:
        i = a.index("--model"); model = a[i + 1]; del a[i:i + 2]
    if "--threads" in a:
        i = a.index("--threads"); threads = int(a[i + 1]); del a[i:i + 2]
    kinds = {}
    for l in open(os.path.join(OUT, "raw_splits.jsonl"), encoding="utf-8"):
        try:
            r = json.loads(l)
        except json.JSONDecodeError:
            continue
        kinds[r["nid"]] = r["kind"]
    q = {}
    for l in open(os.path.join(DATA, "issues.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        if f[0].startswith("usc:"):
            q[f[0]] = f[4]
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(DATA, "holdings.tsv"), encoding="utf-8") if l.startswith("S")]
    courts = collections.defaultdict(set)
    for r in rows:
        courts[r[2]].add(kinds.get(int(r[1])))
    rows = [r for r in rows if len(courts[r[2]]) >= 2]
    win = {}
    need = {(r[6], str(max(0, int(r[7]) - 400))): (r[6], r[7], r[8]) for r in rows}
    for l in open(os.path.join(DATA, "holdings_cert_text.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t", 3)
        k = need.get((f[0], f[1]))
        if k:
            win[k] = f[3]
    path = os.path.join(OUT, "split_verify.jsonl")
    done = set()
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            try:
                done.add(json.loads(l)["hid"])
            except json.JSONDecodeError:
                pass
    todo = [r for r in rows if r[0] not in done]
    print("rows on multi-court issues", len(rows), "todo", len(todo), flush=True)
    lock = threading.Lock()
    with open(path, "a", encoding="utf-8", newline="\n") as fo:
        def go(r):
            w = win.get((r[6], r[7], r[8]))
            if w is None:
                return
            quote = r[9]
            i = w.find(quote)
            marked = w[:i] + "<<<" + quote + ">>>" + w[i + len(quote):] if i >= 0 else w
            prompt = f"Question: {q.get(r[2], '')}\nCourt: {CIRC.get(kinds.get(int(r[1])), '?')}\n\nPassage:\n{marked}\n\nReturn JSON."
            try:
                out, u = llm.call(prompt, SCHEMA, SYSTEM, model=model, max_tokens=3000, job="split-verify")
            except Exception as e:
                return
            if not out:
                return
            with lock:
                fo.write(json.dumps({"hid": r[0], **out, "model": u.get("model")}) + "\n")
                fo.flush()
        with ThreadPoolExecutor(threads) as ex:
            list(ex.map(go, todo))
    print("finished", flush=True)


if __name__ == "__main__":
    main()
