"""Issue-level holdings of decisions, from the court's own opinion text, by gpt-5.4-mini choosing among numbered candidate
sentences (so every quote is an exact span of the decision text, cut by us, never typed by the model).

    python extract_holdings.py <group> <nids-file> [--k 14] [--threads 48] [--limit N]
writes data/holdings_work/raw_<group>.jsonl (one line per decision; resumable: decisions already there are skipped).
"""
import json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core, llm, text

W = text.WORK
OUT = os.path.join(W, "caselaw-lean-2", "data", "holdings_work")
K = 14

SYSTEM = """You read the opinion of a US court and list its HOLDINGS: the legal propositions this court itself decides and that are necessary to (or an alternative ground for) its judgment, one per distinct issue.
You get numbered sentences cut from the court's own opinion (tag C = candidate, F = context about the question presented). Choose holdings only from C sentences.
Not holdings: dicta and asides; propositions assumed without deciding; what a party argued; what a lower court or another case held (unless this court adopts it as its own ruling in that sentence); questions left open; bare dispositions ("Affirmed."); a sentence that only overrules or disapproves an earlier case without stating the rule.
A fact-bound conclusion (e.g. "the evidence was sufficient") is a holding of kind "application" only if no sentence states the rule for that issue.
For each holding give:
- s: the id of the one sentence that states it most directly;
- issue: a short label of the legal question (<= 80 chars);
- proposition: the holding as a standalone general rule, faithful to the sentence, no case-specific names unless essential (<= 300 chars);
- kind: holding | alternative | application;
- law: federal-statute | federal-constitution | federal-rule | federal-common-law | state-statute | state-constitution | state-common-law | procedure | other;
- usc: the US Code subsection it construes as "title:section(sub)" (e.g. "18:924(c)") or "";
- confidence: 0-1 that this is a holding (not dicta) and the proposition is faithful.
At most 6 holdings; return {"holdings": []} if none of the sentences states a holding."""

SCHEMA = {"type": "object", "properties": {"holdings": {"type": "array", "items": {"type": "object", "properties": {
    "s": {"type": "integer"}, "issue": {"type": "string"}, "proposition": {"type": "string"},
    "kind": {"type": "string", "enum": ["holding", "alternative", "application"]}, "law": {"type": "string"},
    "usc": {"type": "string"}, "confidence": {"type": "number"}},
    "required": ["s", "issue", "proposition", "kind", "law", "usc", "confidence"]}}}, "required": ["holdings"]}


def meta_maps():
    cn = {}
    for l in open(os.path.join(W, "lean-in-v3", "courts_named.tsv"), encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        cn[int(f[0])] = (f[1], int(f[4]), f[5])
    return cn


def prep(nid, raw):
    t = text.norm_text(raw)
    parts, form = core.court_parts(t)
    if sum(e - b for b, e, _ in parts) < 600:
        return (nid, None)
    k = int(os.environ.get("HOLD_K", K))
    c = core.candidates(t, parts, k=k)
    if not c:
        return (nid, None)
    return (nid, {"sha": text.text_sha(raw), "form": form, "name": core.front(t, "parties")[:160],
                  "cands": [[i, a, z, part, tag, core.show(t, a, z)] for i, a, z, part, tag in c]})


def run_one(nid, info, meta, group, fo, lock):
    lines = "\n".join(f"[{i}] ({tag}) {s}" for i, a, z, part, tag, s in info["cands"])
    prompt = (f"Court: {meta[0]}\nDate: {meta[1]}\nCase: {meta[2]}\nForm: {info['form']}\n\nSentences:\n{lines}\n\n"
              "Return JSON {\"holdings\": [...]}.")
    try:
        out, usage = llm.call(prompt, SCHEMA, SYSTEM, max_tokens=int(os.environ.get("HOLD_MAXTOK", 1500)), job=f"holdings-{group}",
                              model=os.environ.get("HOLD_MODEL", "gpt-5.4-mini"))
    except Exception as e:
        out, usage = {"error": str(e)[:200]}, {}
    rec = {"nid": nid, "group": group, "sha": info["sha"], "form": info["form"], "cands": [c[:5] for c in info["cands"]],
           "out": out, "model": usage.get("model", "")}
    with lock:
        fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
        fo.flush()


def main():
    a = sys.argv[1:]
    threads, limit = 48, 0
    if "--threads" in a:
        i = a.index("--threads"); threads = int(a[i + 1]); del a[i:i + 2]
    if "--limit" in a:
        i = a.index("--limit"); limit = int(a[i + 1]); del a[i:i + 2]
    group, nfile = a
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"raw_{group}.jsonl")
    done = set()
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            try:
                r = json.loads(l)
                if "error" not in (r.get("out") or {}):
                    done.add(r["nid"])
            except json.JSONDecodeError:
                pass
    nids = [int(l.split("\t")[0]) for l in open(nfile, encoding="utf-8") if l.strip()]
    nids = [n for n in nids if n not in done]
    if limit:
        nids = nids[:limit]
    print(group, "todo", len(nids), "done", len(done), flush=True)
    cn = meta_maps()
    court = {}
    want = set(nids)
    for l in open(os.path.join(W, "lean-in-v3", "decisions.tsv"), encoding="utf-8"):
        x, c, d = l.rstrip("\n").split("\t")
        x = int(x)
        if x in want:
            court[x] = (int(c), int(d))
    paths = text.node_paths(nids)
    names = {}
    for l in open(text.NODES, encoding="utf-8"):
        f = l.split("\t", 7)
        n = int(f[0])
        if n in want:
            names[n] = f[6]
    lock = threading.Lock()
    sem = threading.Semaphore(threads * 4)
    skipped = n_sub = 0
    with open(path, "a", encoding="utf-8", newline="\n") as fo, ThreadPoolExecutor(threads) as ex:
        def go(nid, info, meta):
            try:
                run_one(nid, info, meta, group, fo, lock)
            finally:
                sem.release()
        for r in text.map_nodes(nids, prep, procs=4, chunk=2000, paths=paths):
            if r[0] == "__error__":
                continue
            nid, info = r
            if info is None:
                skipped += 1
                with lock:
                    fo.write(json.dumps({"nid": nid, "group": group, "out": {"holdings": []}, "skip": "no opinion text"}) + "\n")
                continue
            c, d = court.get(nid, (3160, 0))
            meta = (cn.get(c, ("unknown court",))[0], d, names.get(nid, info["name"]))
            sem.acquire()
            ex.submit(go, nid, info, meta)
            n_sub += 1
            if n_sub % 1000 == 0:
                print(time.strftime("%H:%M:%S"), "submitted", n_sub, "skipped", skipped, flush=True)
    print("finished", n_sub, "skipped", skipped, flush=True)


if __name__ == "__main__":
    main()
