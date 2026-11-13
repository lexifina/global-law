"""Blind audit of the round-3 split pairs (no gold).

    python gs_val.py build [N=30] [DECOYS=12]  -> w/val/audit.md, w/val/key.json
    python gs_val.py score                     -> reads w/val/judged.jsonl, prints counts with Wilson 95%

A pair = two installed holdings of different circuits with opposite answers on one new question (one pair per
question, seeded sample). A decoy = holding 1 of a real pair, and as "holding 2" a holding recorded under a DIFFERENT
question on the SAME US Code section, shown with the first question and an opposite answer. The judge sees the question,
the two passages (certificate window, the quoted sentence marked) and the recorded answers; never the reader, the
confidence, the key, the proposition or gold.
"""
import collections, json, os, random, re, sys
from math import sqrt
HT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HT)
import text

W = os.path.join(text.WORK, "caselaw-lean-2", "work", "round3", "splits", "w")
CIRC = {1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth", 6: "Sixth", 7: "Seventh", 8: "Eighth", 9: "Ninth",
        10: "Tenth", 11: "Eleventh", 12: "D.C.", 13: "Federal"}


def wilson(k, n, z=1.96):
    if not n:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def passage(r):
    w0, w1, w = r["window"]
    a, z = r["start"] - w0, r["end"] - w0
    return w[:a] + " >>> " + w[a:z] + " <<< " + w[z:]


def sect(u):
    return re.sub(r"\(.*$", "", u)


def build():
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    nd = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    d = json.load(open(os.path.join(W, "installed_rows.json"), encoding="utf-8"))
    by = collections.defaultdict(list)
    for r in d["rows"]:
        by[r["issue"]].append(r)
    rnd = random.Random(33)
    pairs = []
    for k in sorted(by):
        ys = [r for r in by[k] if r["answer"] == "yes"]
        ns = [r for r in by[k] if r["answer"] == "no"]
        cand = [(y, x) for y in ys for x in ns if y["circ"] != x["circ"]]
        if cand:
            pairs.append((k,) + rnd.choice(cand))
    rnd.shuffle(pairs)
    real = pairs[:n]
    bysec = collections.defaultdict(list)
    for r in d["rows"]:
        bysec[sect(r["usc"])].append(r)
    decoys = []
    for k, y, x in pairs:
        if len(decoys) >= nd:
            break
        first = rnd.choice([y, x])
        others = [r for r in bysec[sect(first["usc"])] if r["issue"] != k and r["circ"] != first["circ"]
                  and r["node"] != first["node"]]
        if not others:
            continue
        o = dict(rnd.choice(others))
        o["answer"] = "no" if first["answer"] == "yes" else "yes"   # shown as the opposite answer to the first question
        decoys.append((k, first, o))
    items = [("real", p) for p in real] + [("decoy", p) for p in decoys]
    rnd.shuffle(items)
    os.makedirs(os.path.join(W, "val"), exist_ok=True)
    key = {}
    blocks = []
    for i, (kind, (k, h1, h2)) in enumerate(items):
        aid = "A%02d" % i
        if rnd.random() < 0.5:
            h1, h2 = h2, h1
        key[aid] = {"kind": kind, "issue": k, "h1": h1["hid"], "h2": h2["hid"]}
        q = by[k][0]["question"]
        blocks.append("\n".join([
            "## Item %s" % aid, "Question: %s" % q,
            "Court 1: %s Circuit, decided %d. Recorded answer: %s" % (CIRC[h1["circ"]], h1["date"], h1["answer"]),
            "Passage 1: %s" % passage(h1),
            "Court 2: %s Circuit, decided %d. Recorded answer: %s" % (CIRC[h2["circ"]], h2["date"], h2["answer"]),
            "Passage 2: %s" % passage(h2)]))
    json.dump(key, open(os.path.join(W, "val", "key.json"), "w", encoding="utf-8"), indent=1)
    with open(os.path.join(W, "val", "audit.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n\n".join(blocks) + "\n")
    print("pairs available", len(pairs), "real", len(real), "decoys", len(decoys))


def score():
    key = json.load(open(os.path.join(W, "val", "key.json"), encoding="utf-8"))
    res = collections.Counter()
    bad = []
    for l in open(os.path.join(W, "val", "judged.jsonl"), encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        r = json.loads(l)
        k = key.get(r.get("id"))
        if not k:
            continue
        g = bool(r.get("same_question")) and bool(r.get("answers_as_recorded")) and bool(r.get("both_holdings"))
        res[k["kind"]] += 1
        res[k["kind"] + "_genuine"] += g
        res[k["kind"] + "_same_question"] += bool(r.get("same_question"))
        res[k["kind"] + "_opposite"] += bool(r.get("same_question")) and bool(r.get("answers_as_recorded"))
        if (k["kind"] == "real") != g:
            bad.append((r["id"], k["kind"], k["issue"], k["h1"], k["h2"], r.get("note", "")))
    out = dict(res)
    for m in ("genuine", "same_question", "opposite"):
        out["real_%s_wilson" % m] = wilson(res["real_" + m], res["real"])
    out["decoys_rejected"] = res["decoy"] - res["decoy_genuine"]
    out["decoys_rejected_wilson"] = wilson(res["decoy"] - res["decoy_genuine"], res["decoy"])
    print(json.dumps(out, indent=1))
    json.dump({"scores": out, "failures": bad}, open(os.path.join(W, "val", "scores.json"), "w", encoding="utf-8"), indent=1)
    for b in bad:
        print("FAIL", b)


if __name__ == "__main__":
    {"build": build, "score": score}[sys.argv[1]]()
