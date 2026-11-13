"""Third stage: the model reads each candidate that passed the cheap filters.

    python -X utf8 classify.py --stage <name> [--model gpt-5.4-mini] [--ids FILE] [--repos r1,r2] [--tpm N] [--limit N]

Reads data/reader_work/res/<repo>.items.jsonl.gz (or only the ids listed in --ids), sends batches of up to 5 items to
Azure OpenAI (json_schema output), and appends one result per item to data/reader_work/llm/<stage>.<model>.jsonl
(resumable: ids already there are skipped). Token usage and cost go to data/reader_usage.json (per stage and model)
and data/reader_work/llm/calls.jsonl (per call).

The model must pick targets from the resolved candidate list; it never names a case itself.
"""
import argparse, asyncio, glob, gzip, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, WORK  # noqa: E402
import llm  # noqa: E402

KINDS = ["overruled", "disapproved", "recededFrom", "abrogated", "supersededByEnactment", "limited", "questioned",
         "criticized", "declinedToFollow", "distinguished", "followed", "none"]
SYSTEM = """You audit US court opinions for one fact: whether the DECIDING court, in its own voice in this opinion, \
performs or declares a treatment of an earlier judicial decision. You get ITEMS. Each item has the deciding decision, \
a numbered list of CANDIDATE earlier decisions (resolved from citations or case names near the sentence), a WINDOW of \
the opinion text, and the FOCUS sentence inside the window.

For each item answer:
- own_act: true only if, in the FOCUS sentence, the deciding court itself acts now on an earlier decision, e.g. "we \
overrule X", "X is hereby overruled", "X is disapproved", "we recede from X", "to the extent X holds otherwise, it is \
overruled", "X should be and is overruled", "we abrogate X", "X has been superseded by statute" stated as this court's \
own conclusion about X, "we decline to follow X", "we limit X to its facts", "we question the continued validity of X", \
"X is no longer good law" declared by this court as its holding.
  own_act is FALSE when the sentence: reports another court's act or earlier history ("X, overruled by Y", "abrogated \
by Y", "superseded by statute as stated in Y", "X was overruled in Y", "in Y we overruled X", "(overruling X)"); states \
a party's argument or request; refuses or declines to overrule; is conditional, hypothetical or about the power to \
overrule in general; quotes another opinion; is spoken by a dissent or concurrence; concerns a procedural ruling \
(objection, motion, exception, assignment/point of error "overruled"); or uses the verb about a statute, rule, \
contract, doctrine or the trial court's ruling in this same case rather than an earlier judicial decision. It is \
also FALSE when the act is negated ("X should not be limited to its facts", "X is not overruled"); when the sentence \
describes what this court or another body said in an earlier decision ("in Malekos we indicated the rule was no \
longer valid", "the Board stated that X may no longer be followed", "as we noted in Y, X was superseded"); or when it \
is a general observation about how courts treat X ("X is increasingly limited to its facts", "X raises doubts", \
"X has been criticized").
- kind: the treatment named by the verb: overruled (also repudiated/abandoned/"no longer good law", and "X will no \
longer be followed" / "we will no longer follow X" when X is this court's own precedent or one it has power over), \
disapproved, recededFrom, abrogated, supersededByEnactment (a statute, rule or \
constitutional amendment displaced the decision), limited, questioned, criticized, declinedToFollow, distinguished, \
followed; "none" if own_act is false.
- targets: ids (T1, T2, ...) of the candidates whose holding, rule or dictum is the object of the act (the case being \
overruled, disapproved, limited, not followed ...). Never a decision cited as the authority for the new rule, nor one \
named only as the case the treated rule conflicts with. Only ids from the list. If the treated decision is not in the \
list, or you cannot tell which it is, return []. Several ids if the sentence treats several decisions.
- scope: "all" (no limiting language), "issues" (the sentence itself names the point the act is limited to: give \
1-3 short issue labels in `issues`, e.g. "parole supervision duty"), "partialUnknown" ("to the extent that X conflicts \
with this opinion", "insofar as inconsistent", "in part", "any language to the contrary", without naming the point), \
"otherGrounds" (the court says it treats X on a point other than the one X is cited for).
- temporal: "unknown" unless the opinion says how the change applies in time: "prospective" (applies only from a date \
or to cases after this decision, possibly including the parties), "pureProspective" (not even to the present \
parties), "retroactive" (expressly applies to pending/past cases). Use the PROSPECTIVITY sentences when given and they \
concern this treatment. prospective_from: "" or "thisDecision" or a date yyyymmdd stated in the text.
- quote: if own_act is true, copy EXACTLY (character for character) one contiguous span of the WINDOW, at most 400 \
characters, that contains the treatment verb and, if they are in the same sentence, the target's name or citation. \
Otherwise "".
- confidence: 0 to 1, your probability that own_act, kind and targets are all right."""

SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["results"],
    "properties": {"results": {"type": "array", "items": {
        "type": "object", "additionalProperties": False,
        "required": ["id", "own_act", "kind", "targets", "scope", "issues", "temporal", "prospective_from", "quote",
                     "confidence"],
        "properties": {
            "id": {"type": "string"}, "own_act": {"type": "boolean"}, "kind": {"type": "string", "enum": KINDS},
            "targets": {"type": "array", "items": {"type": "string"}},
            "scope": {"type": "string", "enum": ["all", "issues", "partialUnknown", "otherGrounds"]},
            "issues": {"type": "array", "items": {"type": "string"}},
            "temporal": {"type": "string", "enum": ["unknown", "prospective", "pureProspective", "retroactive"]},
            "prospective_from": {"type": "string"}, "quote": {"type": "string"},
            "confidence": {"type": "number"}}}}}}


def render(it):
    lw = it["w"][it["lw0"] - it["w0"]:it["lw1"] - it["w0"]]
    focus = it["w"][it["s0"] - it["w0"]:it["s1"] - it["w0"]]
    part = it["part"].rstrip("~")
    lines = [f"### ITEM {it['id']}",
             f"DECIDING: {it['by']['name']} ({it['by']['court']}, {it['by']['year']}); opinion part: {part}",
             "CANDIDATES:"]
    for k, t in enumerate(it["targets"]):
        lines.append(f"  T{k + 1}: {t['name']} - {t['court']}, {t['year']} - {t['cite']} [{t['ev']}]")
    lines.append("WINDOW:\n" + lw)
    lines.append("FOCUS:\n" + focus)
    pros = [p for p in it.get("pros", []) if not (it["lw0"] <= p[0] < it["lw1"])][:2]
    if pros:
        lines.append("PROSPECTIVITY (other sentences of this opinion):")
        for p in pros:
            lines.append("  - " + p[2][:300])
    return "\n".join(lines)


def load_items(repos=None, ids=None):
    files = sorted(glob.glob(os.path.join(WORK, "res", "*.items.jsonl.gz")))
    for f in files:
        repo = os.path.basename(f)[:-len(".items.jsonl.gz")]
        if repos and repo not in repos:
            continue
        for line in gzip.open(f, "rt", encoding="utf-8"):
            it = json.loads(line)
            if ids is not None and it["id"] not in ids:
                continue
            it["repo"] = repo
            yield it


class Usage:
    def __init__(self, stage, model):
        self.path = os.path.join(DATA, "reader_usage.json")
        self.stage, self.model = stage, model
        self.calls_f = open(os.path.join(WORK, "llm", "calls.jsonl"), "a", encoding="utf-8", newline="\n")
        self.acc = {"calls": 0, "prompt_tokens": 0, "cached_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0,
                    "cost_usd": 0.0, "items": 0}
        self.last_flush = time.time()

    def add(self, usage, n_items):
        for k in ("prompt_tokens", "cached_tokens", "completion_tokens", "reasoning_tokens"):
            self.acc[k] += usage.get(k, 0)
        self.acc["calls"] += 1
        self.acc["items"] += n_items
        self.acc["cost_usd"] += llm.cost(usage["model"], usage)
        self.calls_f.write(json.dumps({"t": int(time.time()), "stage": self.stage, **usage, "items": n_items}) + "\n")
        if time.time() - self.last_flush > 30:
            self.flush()

    def flush(self):
        self.calls_f.flush()
        try:
            allu = json.load(open(self.path, encoding="utf-8"))
        except Exception:
            allu = {}
        key = f"{self.stage}|{self.model}"
        prev = allu.get("_session_base", {}).get(key)
        base = allu.setdefault("_session_base", {})
        if key not in base or prev is None:
            base[key] = allu.get("stages", {}).get(key, {k: 0 for k in self.acc})
        b = base[key]
        allu.setdefault("stages", {})[key] = {k: (b.get(k, 0) + v) for k, v in self.acc.items()}
        tot = {"prompt_tokens": 0, "completion_tokens": 0, "cached_tokens": 0, "cost_usd": 0.0}
        for k, v in allu["stages"].items():
            for x in tot:
                tot[x] += v.get(x, 0)
        tot["total_tokens"] = tot["prompt_tokens"] + tot["completion_tokens"]
        allu["total"] = tot
        allu["prices_usd_per_1M"] = llm.PRICES
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(allu, f, indent=1)
        os.replace(tmp, self.path)
        self.last_flush = time.time()

    def close(self):
        self.flush()
        allu = json.load(open(self.path, encoding="utf-8"))
        allu.get("_session_base", {}).pop(f"{self.stage}|{self.model}", None)
        with open(self.path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(allu, f, indent=1)


async def run(args):
    os.makedirs(os.path.join(WORK, "llm"), exist_ok=True)
    out_path = os.path.join(WORK, "llm", f"{args.stage}.{args.model}.jsonl")
    done = set()
    if os.path.exists(out_path):
        for line in open(out_path, encoding="utf-8"):
            try:
                done.add(json.loads(line)["id"])
            except Exception:
                pass
    ids = None
    if args.ids:
        ids = set(x.strip().split("\t")[0] for x in open(args.ids, encoding="utf-8") if x.strip())
    repos = set(args.repos.split(",")) if args.repos else None
    client = llm.Client(args.model, tpm=args.tpm, concurrency=args.conc)
    usage = Usage(args.stage, args.model)
    fo = open(out_path, "a", encoding="utf-8", newline="\n")
    q = asyncio.Queue(maxsize=args.conc * 4)
    stats = {"items": 0, "fail": 0}

    async def worker():
        while True:
            batch = await q.get()
            if batch is None:
                q.task_done()
                return
            user = "\n\n".join(render(it) for it in batch)
            est = (len(SYSTEM) + len(user)) // 3 + 300 * len(batch)
            try:
                content, u = await client.call(SYSTEM, user, SCHEMA, max_tokens=2500 + 600 * len(batch),
                                               est_tokens=est, reasoning_effort=args.effort)
                got = json.loads(content).get("results", [])
                res = {str(r.get("id", "")).strip(): r for r in got}
                usage.add(u, len(batch))
                missing = [it for it in batch if it["id"] not in res]
                if missing and len(got) == len(batch) and not any(it["id"] in res for it in batch):
                    res = {it["id"]: r for it, r in zip(batch, got)}  # ids mangled but order kept
                    missing = []
                if missing and len(batch) > 1:
                    stats["retried"] = stats.get("retried", 0) + len(missing)
                    for it in missing:
                        q.put_nowait([it]) if not q.full() else await q.put([it])
                    batch = [it for it in batch if it["id"] in res]
                for it in batch:
                    r = res.get(it["id"])
                    rec = {"id": it["id"], "repo": it["repo"], "model": u["model"], "r": r}
                    fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    stats["items"] += 1
                fo.flush()
            except Exception as e:
                stats["fail"] += 1
                print("batch failed:", str(e)[:200], flush=True)
            q.task_done()

    workers = [asyncio.create_task(worker()) for _ in range(args.conc)]
    batch = []
    n = 0
    t0 = time.time()
    for it in load_items(repos, ids):
        if it["id"] in done:
            continue
        batch.append(it)
        n += 1
        if len(batch) >= args.batch:
            await q.put(batch)
            batch = []
        if args.limit and n >= args.limit:
            break
        if n % 5000 == 0:
            print(time.strftime("%H:%M:%S"), "queued", n, "done", stats["items"], "429s", client.n429,
                  f"${usage.acc['cost_usd']:.2f}", flush=True)
    if batch:
        await q.put(batch)
    await q.join()
    for _ in workers:
        await q.put(None)
    await asyncio.gather(*workers)
    usage.close()
    await client.close()
    fo.close()
    print(time.strftime("%H:%M:%S"), "finished", stats, "429s", client.n429, f"{time.time() - t0:.0f}s",
          json.dumps(usage.acc), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--model", default="gpt-5.4-mini")
    ap.add_argument("--ids")
    ap.add_argument("--repos")
    ap.add_argument("--tpm", type=int, default=550_000)
    ap.add_argument("--conc", type=int, default=48)
    ap.add_argument("--batch", type=int, default=5)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--effort", default="low")
    asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    main()
