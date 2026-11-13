"""Run one passage-classification task with Azure gpt-5.4-mini (US East 2), resumable, with a global token ledger.

    python llm_run.py <task> <in.jsonl> <out.jsonl> [--limit N] [--concurrency 32]

Tasks are defined in tasks.py (system prompt, JSON schema, user-message builder, row key).
The key is read by reader/llm.py from the environment and never printed. gpt-6-sol is refused by that client.
Ledger: hunt/work/usage.tsv (task, calls, prompt, completion, cached); the run stops when the ledger passes BUDGET.
"""
import asyncio, json, os, sys, time
import hcommon as C
import tasks as T
from llm import Client  # tools/caselaw2/reader/llm.py

BUDGET = 40_000_000
LEDGER = os.path.join(C.HWORK, "usage.tsv")


def spent():
    tot = 0
    if os.path.exists(LEDGER):
        for line in open(LEDGER, encoding="utf-8"):
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4 and p[1].isdigit():
                tot += int(p[2]) + int(p[3])
    return tot


async def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    task, inp, out = T.TASKS[a[0]], a[1], a[2]
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    conc = int(sys.argv[sys.argv.index("--concurrency") + 1]) if "--concurrency" in sys.argv else 32
    done = set()
    if os.path.exists(out):
        for line in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(line)["key"])
            except Exception:
                pass
    rows = [json.loads(l) for l in open(inp, encoding="utf-8")]
    todo = [r for r in rows if task["key"](r) not in done]
    if limit:
        todo = todo[:limit]
    start = spent()
    C.log(a[0], "rows", len(rows), "done", len(done), "todo", len(todo), "ledger", start)
    if start > BUDGET:
        raise SystemExit("token budget exhausted")
    cl = Client(model="gpt-5.4-mini", tpm=500_000, concurrency=conc)
    tok = {"calls": 0, "p": 0, "c": 0, "cached": 0}
    lock = asyncio.Lock()
    f = open(out, "a", encoding="utf-8", newline="\n")
    t0 = time.time()

    async def one(r):
        if start + tok["p"] + tok["c"] > BUDGET:
            return
        user = task["user"](r)
        try:
            content, u = await cl.call(task["system"], user, task["schema"], max_tokens=task.get("max_tokens", 1500),
                                       est_tokens=len(user) // 3 + 600, reasoning_effort=task.get("effort", "low"))
            ans = json.loads(content)
        except Exception as e:
            ans, u = {"error": str(e)[:200]}, {"prompt_tokens": 0, "completion_tokens": 0, "cached_tokens": 0,
                                               "model": "-"}
        async with lock:
            tok["calls"] += 1; tok["p"] += u["prompt_tokens"]; tok["c"] += u["completion_tokens"]
            tok["cached"] += u.get("cached_tokens", 0)
            f.write(json.dumps({"key": task["key"](r), "model": u.get("model"), "ans": ans}) + "\n")
            if tok["calls"] % 250 == 0:
                f.flush()
                C.log(a[0], tok, "%.0fs" % (time.time() - t0))

    await asyncio.gather(*(one(r) for r in todo))
    f.close()
    await cl.close()
    with open(LEDGER, "a", encoding="utf-8", newline="\n") as g:
        g.write("%s\t%d\t%d\t%d\t%d\n" % (a[0], tok["calls"], tok["p"], tok["c"], tok["cached"]))
    C.log("done", a[0], tok, "ledger now", spent())


if __name__ == "__main__":
    asyncio.run(main())
