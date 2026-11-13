"""Blind validation sets and scoring.

    python validate.py sample      -> holdings_work/val/holdings_<k>.md (4 files x 30 holdings) and clusters_<k>.md (2 x 30 pairs),
                                      plus the keys (val/key_*.json, never shown to judges)
    python validate.py score       -> reads val/judged_*.jsonl, prints precision with Wilson 95% intervals -> val/scores.json
Judges see the decision's words around the quoted sentence and the proposition; not the model, confidence or group.
"""
import collections, json, math, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text

DATA = os.path.join(text.WORK, "caselaw-lean-2", "data")
VAL = os.path.join(DATA, "holdings_work", "val")
CIRC = {1: "1st", 2: "2d", 3: "3d", 4: "4th", 5: "5th", 6: "6th", 7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th",
        12: "D.C.", 13: "Fed."}


def wilson(k, n, z=1.96):
    if not n:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def window(t, a, z, w=900):
    s = max(0, a - w)
    e = min(len(t), z + w)
    return re.sub(r"\s+", " ", t[s:a]) + " <<<" + re.sub(r"\s+", " ", t[a:z]) + ">>> " + re.sub(r"\s+", " ", t[z:e])


def sample(only_clusters=False, tag=""):
    os.makedirs(VAL, exist_ok=True)
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(DATA, "holdings.tsv"), encoding="utf-8")]
    scn = set(int(l) for l in open(os.path.join(DATA, "holdings_work", "scotus_nids.tsv")))
    groups = {"scotus": [r for r in rows if r[0].startswith("H") and int(r[1]) in scn],
              "treat": [r for r in rows if r[0].startswith("H") and int(r[1]) not in scn],
              "split": [r for r in rows if r[0].startswith("S")]}
    rnd = random.Random(20261112)
    if only_clusters:
        rnd = random.Random(20261113)
        return _clusters(rows, rnd, tag)
    pick = rnd.sample(groups["scotus"], 24) + rnd.sample(groups["treat"], 24) + rnd.sample(groups["split"], 12)
    rnd.shuffle(pick)
    issues = {l.split("\t")[0]: l.rstrip("\n").split("\t") for l in open(os.path.join(DATA, "issues.tsv"), encoding="utf-8")}
    texts = text.fetch(sorted({int(r[1]) for r in pick}))
    key = []
    for k in range(2):
        part = pick[k * 30:(k + 1) * 30]
        with open(os.path.join(VAL, f"holdings_{k}.md"), "w", encoding="utf-8", newline="\n") as f:
            for i, r in enumerate(part):
                t = text.norm_text(texts[int(r[1])])
                iid = f"h{k}-{i}"
                q = issues[r[2]][4] if r[2].startswith("usc:") else "-"
                f.write(f"## {iid}\nIssue: {issues[r[2]][1]}\n" + (f"Question: {q}\nAnswer claimed: {r[4]}\n" if q != "-" else "") +
                        f"Proposition claimed: {r[3]}\nText (the quoted sentence is between <<< >>>):\n{window(t, int(r[7]), int(r[8]))}\n\n")
                key.append({"id": iid, "hid": r[0], "group": "scotus" if r in groups["scotus"] else "split" if r[0].startswith("S") else "treat"})
    json.dump(key, open(os.path.join(VAL, "key_holdings.json"), "w"), indent=0)
    _clusters(rows, rnd, tag)


def _clusters(rows, rnd, tag):
    # clusters: one yes and one no holding from different circuits on the same issue
    cand = [l.rstrip("\n").split("\t") for l in open(os.path.join(DATA, "holdings_work", "split_candidates.tsv"), encoding="utf-8")]
    byid = {r[0]: r for r in rows}
    kinds = {}
    for l in open(os.path.join(DATA, "holdings_work", "raw_splits.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        kinds[r["nid"]] = r["kind"]
    pk = rnd.sample(cand, min(30, len(cand)))
    texts = text.fetch(sorted({int(byid[c[i]][1]) for c in pk for i in (9, 10)}))
    ck = []
    for k in range(1):
        with open(os.path.join(VAL, f"clusters{tag}_{k}.md"), "w", encoding="utf-8", newline="\n") as f:
            for i, c in enumerate(pk[k * 30:(k + 1) * 30]):
                cid = f"c{tag}{k}-{i}"
                ya, na = byid[c[9]], byid[c[10]]
                ty, tn = text.norm_text(texts[int(ya[1])]), text.norm_text(texts[int(na[1])])
                f.write(f"## {cid}\nStatute: {c[1]}\nCanonical question: {c[2]}\n\n"
                        f"### Decision A ({CIRC.get(kinds.get(int(ya[1])), '?')} Cir.), said to answer YES\n{window(ty, int(ya[7]), int(ya[8]), 700)}\n\n"
                        f"### Decision B ({CIRC.get(kinds.get(int(na[1])), '?')} Cir.), said to answer NO\n{window(tn, int(na[7]), int(na[8]), 700)}\n\n")
                ck.append({"id": cid, "issue": c[0], "yes": c[9], "no": c[10]})
    json.dump(ck, open(os.path.join(VAL, f"key_clusters{tag}.json"), "w"), indent=0)
    print("clusters", len(ck))


def score():
    out = {}
    hk = {k["id"]: k for k in json.load(open(os.path.join(VAL, "key_holdings.json")))}
    j = {}
    for fn in os.listdir(VAL):
        if fn.startswith("judged_") and fn.endswith(".jsonl"):
            for l in open(os.path.join(VAL, fn), encoding="utf-8"):
                l = l.strip()
                if l:
                    r = json.loads(l)
                    j[r["id"]] = r
    hs = [(hk[i], j[i]) for i in hk if i in j]
    def agg(items, f):
        k = sum(1 for _, r in items if f(r))
        return {"n": len(items), "ok": k, "precision": round(k / len(items), 3) if items else None, "wilson95": wilson(k, len(items))}
    out["holdings_all"] = agg(hs, lambda r: r["is_holding"] and r["faithful"])
    out["holdings_is_holding"] = agg(hs, lambda r: r["is_holding"])
    out["holdings_faithful"] = agg(hs, lambda r: r["faithful"])
    for g in ("scotus", "treat", "split"):
        out[f"holdings_{g}"] = agg([x for x in hs if x[0]["group"] == g], lambda r: r["is_holding"] and r["faithful"])
    sp = [x for x in hs if x[0]["group"] == "split"]
    out["split_answer_correct"] = agg([x for x in sp if "answer_correct" in x[1]], lambda r: r.get("answer_correct"))
    for tag in ("", "_v"):
        kp = os.path.join(VAL, f"key_clusters{tag}.json")
        if not os.path.exists(kp):
            continue
        ck = {k["id"]: k for k in json.load(open(kp))}
        cs = [(ck[i], j[i]) for i in ck if i in j]
        name = "clusters_before_verify" if tag == "" else "clusters_after_verify"
        out[name + "_same_question"] = agg(cs, lambda r: r["same_question"])
        out[name + "_opposite"] = agg(cs, lambda r: r["same_question"] and r["opposite"])
        out[name + "_genuine_split"] = agg(cs, lambda r: r["same_question"] and r["opposite"] and r["both_holdings"])
    json.dump(out, open(os.path.join(VAL, "scores.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "clusters":
        sample(True, sys.argv[2])
    else:
        {"sample": sample, "score": score}[sys.argv[1]]()
