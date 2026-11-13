"""Step 4 of the split pipeline: per subsection, cluster the decisions' yes/no questions into canonical questions
(gpt-6.1-sol), with each item's polarity relative to the canonical question, so circuits line up on one issue_key.

    python splits_cluster.py [--model gpt-6.1-sol] [--threads 8]
reads raw_splits.jsonl; writes data/holdings_work/split_clusters.jsonl: {key, questions: [{q, label}], items: [{id, c, neg}],
    item_index: [[nid, hidx or -1 for a SCOTUS conflict question], ...]}
"""
import collections, json, os, sys, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm, text

OUT = os.path.join(text.WORK, "caselaw-lean-2", "data", "holdings_work")
SYSTEM = """You normalise legal questions about one US Code subsection so that courts' holdings can be compared for circuit splits.
You get numbered yes/no questions, each written by a different reader of a different decision. Group the questions that ask the SAME legal question (they would be answered by the same rule, even if worded differently or phrased as the negation).
Create one canonical yes/no question per group: general, about the statute, no party names or facts, at the level of generality at which courts disagree. Do not merge questions that are merely related (different elements, different predicate offences, different clauses).
For every item give c = its canonical question's index, and neg = true if the item's question is the NEGATION of the canonical question (so a "yes" to the item means "no" to the canonical question); otherwise false. Give each canonical question a short label (<= 60 chars).
Every item must be assigned; a question that matches no other is its own group."""
SCHEMA = {"type": "object", "properties": {
    "questions": {"type": "array", "items": {"type": "object", "properties": {"q": {"type": "string"}, "label": {"type": "string"}},
                                             "required": ["q", "label"]}},
    "items": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "integer"}, "c": {"type": "integer"},
                                                                          "neg": {"type": "boolean"}}, "required": ["id", "c", "neg"]}}},
    "required": ["questions", "items"]}


def load():
    by = collections.defaultdict(list)
    seen = set()
    for l in open(os.path.join(OUT, "raw_splits.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        o = r.get("out") or {}
        if "error" in o or (r["key"], r["nid"]) in seen:
            continue
        seen.add((r["key"], r["nid"]))
        if o.get("interprets"):
            for hi, h in enumerate(o.get("holdings") or []):
                if h.get("question"):
                    by[r["key"]].append((r["nid"], hi, h["question"]))
        if r["kind"] == 0 and o.get("resolves_conflict") and (o.get("conflict_question") or "").strip():
            by[r["key"]].append((r["nid"], -1, o["conflict_question"]))
    return by


def main():
    a = sys.argv[1:]
    model, threads = "gpt-6.1-sol", 8
    if "--model" in a:
        i = a.index("--model"); model = a[i + 1]; del a[i:i + 2]
    if "--threads" in a:
        i = a.index("--threads"); threads = int(a[i + 1]); del a[i:i + 2]
    subs = {l.split("\t")[1]: l.split("\t")[4] for l in open(os.path.join(OUT, "split_subsections.tsv"), encoding="utf-8")}
    by = load()
    path = os.environ.get("CLUSTER_OUT") or os.path.join(OUT, "split_clusters.jsonl")
    done = set()
    if os.path.exists(path):
        done = {json.loads(l)["key"] for l in open(path, encoding="utf-8")}
    lock = threading.Lock()
    reuse = os.environ.get("CLUSTER_REUSE")
    if reuse and os.path.exists(reuse):  # an earlier run on the same items: keep it
        with open(path, "a", encoding="utf-8", newline="\n") as fo:
            for l in open(reuse, encoding="utf-8"):
                c = json.loads(l)
                k = c["key"]
                if k not in done and k in by and [[n, h] for n, h, _ in by[k]] == c["item_index"]:
                    fo.write(l.rstrip("\n") + "\n")
                    done.add(k)
        print("reused", len(done), flush=True)
    todo = [k for k in by if k not in done and len(by[k]) >= 1]
    print("keys", len(todo), "items", sum(len(by[k]) for k in todo), flush=True)
    with open(path, "a", encoding="utf-8", newline="\n") as fo:
        def go(key):
            items = by[key]
            lines = "\n".join(f"[{i}] {q}" for i, (_, _, q) in enumerate(items))
            prompt = f"Subsection: {key} — {subs.get(key, '')}\n\nQuestions:\n{lines}\n\nReturn JSON."
            try:
                out, u = llm.call(prompt, SCHEMA, SYSTEM, model=model, max_tokens=16000, job="splits-cluster",
                                  est=len(prompt) // 3 + 4000)
            except Exception as e:
                print("error", key, e, flush=True)
                return
            if not out:
                print("bad json", key, flush=True)
                return
            rec = {"key": key, "model": u.get("model"), "questions": out.get("questions", []), "items": out.get("items", []),
                   "item_index": [[n, h] for n, h, _ in items], "item_q": [q for _, _, q in items]}
            with lock:
                fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fo.flush()
        with ThreadPoolExecutor(threads) as ex:
            list(ex.map(go, todo))
    print("finished")


if __name__ == "__main__":
    main()
