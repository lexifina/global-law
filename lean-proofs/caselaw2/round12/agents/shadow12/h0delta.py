"""h0-only: per-case model class v11d vs a round-12 variant (shadow_docket.h0.cases.tsv), by class / sc_in_corpus /
year of order. python -X utf8 h0delta.py <variant>"""
import collections, os, sys
C2 = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
def rd(p):
    out = {}
    with open(p, encoding="utf-8") as f:
        h = f.readline().rstrip("\n").split("\t")
        for l in f:
            r = dict(zip(h, l.rstrip("\n").split("\t"))); out[r["node"]] = r
    return out
a = rd(os.path.join(C2, "round11/results/v11d/bench/shadow_docket.h0.cases.tsv"))
b = rd(os.path.join(C2, "round12/results", sys.argv[1], "bench/shadow_docket.h0.cases.tsv"))
c = collections.Counter()
for n, r in a.items():
    s = b[n]
    if r["model_class"] != s["model_class"]:
        c[(r["class"], r["sc_in_corpus"], r["order_date"][:4], r["model_class"] + "->" + s["model_class"])] += 1
for k, v in sorted(c.items()): print(v, *k)
miss = collections.Counter()
for n, s in b.items():
    if s["class"] in ("NEG", "PART") and not s["model_class"].startswith("NEG"):
        miss[(s["sc_in_corpus"], s["order_date"][:4])] += 1
print("remaining NEG/PART not NEG*: by (in corpus, year):", sorted(miss.items()))
