"""Step 6: gpt-6.1-sol reads a sample of conflicting pairs (up to 12 per family) and says why they conflict.
-> factors_work/conflict_kinds.jsonl"""
import collections, json, os, random
from concurrent.futures import ThreadPoolExecutor
from common import llm, W, WORK, FAMILIES
from verify2 import SUBS, SIDX
vocab = {s["key"]: s for s in SUBS}
fname = {}
for s in SUBS:
    for i, f in enumerate(s["factors"]):
        fname[SIDX[s["key"]] * 100 + i + 1] = f"{f['name']} ({f['side']})"
props = {}
for l in open(os.path.join(W, "holdings.tsv"), encoding="utf-8"):
    if l.startswith("H"):
        r = l.split("\t", 5)
        props[r[0]] = r[3]
quotes = collections.defaultdict(dict)
for l in open(os.path.join(WORK, "factor_quotes.tsv"), encoding="utf-8"):
    h, f, r, q = l.rstrip("\n").split("\t"); quotes[h][int(f)] = q
cases = {l.split("\t")[0]: l.rstrip("\n").split("\t") for l in open(os.path.join(W, "factor_cases.tsv"), encoding="utf-8")}
fac = collections.defaultdict(list)
for l in open(os.path.join(W, "factors.tsv"), encoding="utf-8"):
    h, f, s, r = l.rstrip("\n").split("\t"); fac[h].append((int(f), r == "1"))
SCHEMA = {"type": "object", "properties": {"kind": {"type": "string", "enum": [
    "extraction", "coarseVocabulary", "differentQuestion", "doctrinalChange", "genuineTension"]},
    "why": {"type": "string"}}, "required": ["kind", "why"]}
P = """Two US Supreme Court cases in the issue family "{fam}" conflict under Horty's reason model of precedent: they have
opposite outcomes on the question "{q}", and each case's stated reason factors are all present in the other case's facts,
so the derived priority ordering orders the two reasons both ways.

{a}

{b}

Why do they conflict? Pick one:
- extraction: a listed factor, reason or outcome looks wrong for that case (our extraction error);
- coarseVocabulary: both readings are right, but the cases differ on a fact the vocabulary does not capture, so a finer
  factor would distinguish them;
- differentQuestion: the cases actually decide different legal questions inside the family (e.g. remedy vs merits,
  different statute or doctrine), so they do not belong in one case base;
- doctrinalChange: the later case changed, abandoned or overruled the earlier approach;
- genuineTension: same question, same relevant facts, opposite results with no change of doctrine.
Give a one-sentence reason."""
def desc(hid):
    c = cases[hid]; ev = quotes[hid]
    fl = "\n".join(f"   - {fname[f]}{' [REASON]' if r else ''}: \"{ev.get(f, '')}\"" for f, r in fac[hid])
    return (f"Case {hid} (decided {c[5][:4]}), outcome {c[4]}. Holding: {props.get(hid, '')}\n  Factors present:\n{fl}")
pairs = [json.loads(l) for l in open(os.path.join(WORK, "conflicts.jsonl"), encoding="utf-8")]
by = collections.defaultdict(list)
for p in pairs:
    if any(r for _, r in fac[p["a"]]) and any(r for _, r in fac[p["b"]]):  # both cases state a reason
        by[p["family"]].append(p)
samp = []
for fam, ps in by.items():
    random.Random(3).shuffle(ps); samp += ps[:12]
def one(p):
    q = vocab[p["family"]]["question"]
    r, u = llm.call(P.format(fam=p["family"], q=q, a=desc(p["a"]), b=desc(p["b"])), SCHEMA, model="gpt-6.1-sol",
                    max_tokens=3000, job="factor_conflicts2", reasoning="low")
    return {**p, **(r or {"kind": "failed", "why": ""})}
with ThreadPoolExecutor(24) as ex:
    res = list(ex.map(one, samp))
with open(os.path.join(WORK, "conflict_kinds2.jsonl"), "w", encoding="utf-8", newline="\n") as f:
    [f.write(json.dumps(r) + "\n") for r in res]
print(collections.Counter(r["kind"] for r in res))
for fam in sorted(by):
    print(fam, collections.Counter(r["kind"] for r in res if r["family"] == fam))
