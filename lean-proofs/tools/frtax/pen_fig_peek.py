import json, random, re, sys
F = [json.loads(l) for l in open("data/pen/court_figures.jsonl")]
kind = sys.argv[1]; n = int(sys.argv[2]); seed = int(sys.argv[3])
S = [f for f in F if f["kind"] == kind]
def pairs(f):
    out = []
    for R in f["rates"]:
        for x in f["amounts"]:
            for y in f["amounts"]:
                if x > 0 and y > 0 and x != y and abs(y - R / 100 * x) <= 1: out.append((R, x, y))
    return out
if kind == "majo":
    P = [f for f in S if pairs(f)]
    print(len(S), "majo sentences;", len(P), "with a consistent (base, rate, amount) pair")
random.seed(seed)
for f in random.sample(S, n):
    print("--", f["court"][:25], f["date"], f["number"], f.get("rates"), f.get("irate"), f.get("period"), "PAIRS", pairs(f) if kind == "majo" else "", "|", f["sentence"][:700])
