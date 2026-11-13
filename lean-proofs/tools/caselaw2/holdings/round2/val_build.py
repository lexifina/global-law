"""Blind validation sets (judges see the texts and the claim, not the reader, its confidence or which stream).
 A: every staged Supreme Court resolution link + decoys (answer flipped).
 B: a stratified random sample of new split questions (pairs) + decoys (the T passage of another pair).
 -> work/val/A_XX.md, B_XX.md, key.json"""
import os, json, random, collections
import common as C
import text
W = os.path.join(C.PRIV, "work")
d = json.load(open(os.path.join(W, "staged.json"), encoding="utf-8"))
rows = d["rows"]
rnd = random.Random(20261112)
nodes = {r["node"] for r in rows}
raw = text.fetch(nodes)
T = {n: text.norm_text(b) for n, b in raw.items()}


def passage(r, pad=1300):
    t = T[r["node"]]
    a, z = r["start"], r["end"]
    return (text.quote_of(t, max(0, a - pad), a) + " >>>" + text.quote_of(t, a, z) + "<<< " + text.quote_of(t, z, min(len(t), z + pad))).strip()


iss = C.load_issues()
H = C.load_holdings(pred=lambda f: f[2] in {r["issue"] for r in rows if r["stream"] == "res"} and f[4] in ("yes", "no"))
side = collections.defaultdict(lambda: {"yes": [], "no": []})
for f in H:
    if not f[0].split(".")[-1].startswith("r"):
        side[f[2]][f[4]].append((-float(f[13]), f[3]))
key = {}
A = []
res = [r for r in rows if r["stream"] == "res"]
for r in res:
    A.append(("res", r, r["answer"], False))
for r in rnd.sample(res, 8):
    A.append(("res", r, "no" if r["answer"] == "yes" else "yes", True))
rnd.shuffle(A)
blocksA = []
for i, (_, r, ans, decoy) in enumerate(A):
    vid = "A%03d" % i
    key[vid] = {"stream": "res", "hid": r["hid"], "pid": r["pid"], "decoy": decoy, "conf": r["conf"]}
    y = sorted(side[r["issue"]]["yes"])[:1]
    n = sorted(side[r["issue"]]["no"])[:1]
    blocksA.append("\n".join([
        "## Item %s" % vid,
        "QUESTION (%s): %s" % (r["usc"], r["question"]),
        "A court of appeals answering YES held: %s" % (y[0][1] if y else "-"),
        "A court of appeals answering NO held: %s" % (n[0][1] if n else "-"),
        "SUPREME COURT DECISION: %s, %s (%s)" % (r["name"], r["cite"], r["date"]),
        "PASSAGE from the opinion of the Court (the marked sentence is between >>> and <<<):",
        passage(r),
        "CLAIM: this decision decides the QUESTION; the Supreme Court's answer to the QUESTION as worded is \"%s\"; the marked sentence states that holding." % ans.upper()]))
# B: pairs
pairs = collections.OrderedDict()
for r in rows:
    if r["stream"] == "xc":
        pairs.setdefault(r["issue"], {})
by_issue = collections.defaultdict(list)
for r in rows:
    if r["stream"] == "xc":
        by_issue[r["issue"]].append(r)
plist = []
for k, rs in by_issue.items():
    b = next(x for x in rs if x["side"] == "B")
    for t in rs:
        if t["side"] == "T":
            plist.append((b, t))
lo = [p for p in plist if p[1]["conf"] < 0.7]
hi = [p for p in plist if p[1]["conf"] >= 0.7]
n_lo = round(42 * len(lo) / len(plist))
samp = rnd.sample(lo, n_lo) + rnd.sample(hi, 42 - n_lo)
B = [(b, t, False) for b, t in samp]
others = [p for p in plist if p not in samp]
for (b, t) in rnd.sample(samp, 6):
    o = rnd.choice([p for p in others if p[1]["usc"].split(":")[0] != t["usc"].split(":")[0]])
    fake = dict(o[1]); fake["answer"] = t["answer"]
    B.append((b, fake, True))
rnd.shuffle(B)
blocksB = []
for i, (b, t, decoy) in enumerate(B):
    vid = "B%03d" % i
    key[vid] = {"stream": "xc", "issue": b["issue"], "hid_b": b["hid"], "hid_t": t["hid"], "decoy": decoy, "conf": t["conf"]}
    blocksB.append("\n".join([
        "## Item %s" % vid,
        "QUESTION (%s): %s" % (b["usc"], b["question"]),
        "DECISION 1: %s, %s (Cir. %s, %s)" % (b["name"], b["cite"], b["circ"], b["date"]),
        "PASSAGE 1 (marked sentence between >>> and <<<):",
        passage(b, 1100),
        "CLAIM 1: the court in DECISION 1 holds, as its own holding, that the answer to the QUESTION is \"%s\"." % b["answer"].upper(),
        "DECISION 2: %s, %s (Cir. %s, %s)" % (t["name"], t["cite"], t["circ"], t["date"]),
        "PASSAGE 2 (marked sentence between >>> and <<<):",
        passage(t, 1100),
        "CLAIM 2: the court in DECISION 2 holds, as its own holding, that the answer to the QUESTION is \"%s\"." % t["answer"].upper()]))
od = os.path.join(W, "val"); os.makedirs(od, exist_ok=True)
json.dump(key, open(os.path.join(od, "key.json"), "w"), indent=0)
def dump(prefix, blocks, nb):
    per = (len(blocks) + nb - 1) // nb
    for i in range(nb):
        fn = os.path.join(od, "%s_%02d.md" % (prefix, i))
        open(fn, "w", encoding="utf-8", newline="\n").write("\n\n".join(blocks[i * per:(i + 1) * per]) + "\n")
        print(fn, os.path.getsize(fn), len(blocks[i * per:(i + 1) * per]))
dump("A", blocksA, 3); dump("B", blocksB, 4)
print("A items", len(A), "B items", len(B), "pairs total", len(plist), "lo", len(lo), "hi", len(hi))
