"""Score the blind validation: precision with Wilson 95% intervals, decoys reported separately.
 -> work/val/scores.json, work/drop.json (holding ids / issue keys judged wrong)"""
import os, json, glob, collections
import common as C
W = os.path.join(C.PRIV, "work", "val")
key = json.load(open(os.path.join(W, "key.json")))
J = {}
for fn in glob.glob(os.path.join(W, "judged_*.jsonl")):
    for l in open(fn, encoding="utf-8"):
        if l.strip():
            r = json.loads(l); J[r["id"]] = r
def rate(k, n):
    return {"k": k, "n": n, "p": round(k / n, 3) if n else None, "wilson95": C.wilson(k, n)}
out = {}; drop = []
A = [(v, key[v], J[v]) for v in key if v.startswith("A") and v in J]
real = [x for x in A if not x[1]["decoy"]]; dec = [x for x in A if x[1]["decoy"]]
okA = lambda j: bool(j["decides"] and j["answer_ok"])
out["A_resolution_links"] = {"judged": len(real),
    "decides_and_answer": rate(sum(okA(j) for _, _, j in real), len(real)),
    "also_sentence_states_it": rate(sum(okA(j) and bool(j["sentence_ok"]) for _, _, j in real), len(real)),
    "conf_lt_0.7": rate(sum(okA(j) for _, k, j in real if k["conf"] < 0.7), sum(1 for _, k, _ in real if k["conf"] < 0.7)),
    "conf_ge_0.7": rate(sum(okA(j) for _, k, j in real if k["conf"] >= 0.7), sum(1 for _, k, _ in real if k["conf"] >= 0.7)),
    "decoys_rejected": rate(sum(not okA(j) for _, _, j in dec), len(dec))}
drop += [k["hid"] for _, k, j in real if not (okA(j) and j["sentence_ok"])]
B = [(v, key[v], J[v]) for v in key if v.startswith("B") and v in J]
real = [x for x in B if not x[1]["decoy"]]; dec = [x for x in B if x[1]["decoy"]]
g = lambda j: bool(j["genuine_split"])
out["B_new_split_questions"] = {"judged": len(real),
    "genuine_split": rate(sum(g(j) for _, _, j in real), len(real)),
    "same_question": rate(sum(bool(j["same_question"]) for _, _, j in real), len(real)),
    "both_claims_ok": rate(sum(bool(j["c1_ok"] and j["c2_ok"]) for _, _, j in real), len(real)),
    "conf_lt_0.7": rate(sum(g(j) for _, k, j in real if k["conf"] < 0.7), sum(1 for _, k, _ in real if k["conf"] < 0.7)),
    "conf_ge_0.7": rate(sum(g(j) for _, k, j in real if k["conf"] >= 0.7), sum(1 for _, k, _ in real if k["conf"] >= 0.7)),
    "decoys_rejected": rate(sum(not g(j) for _, _, j in dec), len(dec))}
drop += [k["hid_t"] for _, k, j in real if not g(j)]
json.dump(out, open(os.path.join(W, "scores.json"), "w"), indent=1)
json.dump(drop, open(os.path.join(C.PRIV, "work", "drop.json"), "w"))
print(json.dumps(out, indent=1)); print("drop", drop)
for v, k, j in A + B:
    if not k["decoy"] and j.get("note"): print(v, k.get("hid") or k.get("issue"), j["note"][:160])
