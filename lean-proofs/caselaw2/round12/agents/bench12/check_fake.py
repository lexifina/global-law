"""Recompute fjc_idb_unpub metrics independently from the fake's expected classes and compare. python -I check_fake.py <bench dir> <fake dir> <results dir>"""
import csv, json, os, sys
B, F, R = sys.argv[1:4]
exp = dict(l.rstrip("\n").split("\t") for l in open(os.path.join(F, "expected.tsv"), encoding="utf-8"))
U = list(csv.DictReader(open(os.path.join(B, "key_nodes.tsv"), encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
K = list(csv.DictReader(open(os.path.join(B, "key.tsv"), encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
CLEAN = {"GOOD", "NEG_OTHER", "UNK_OTHER"}
def met(us):
    neg = [exp[u["dist_node"]] for u in us if u["class"] == "NEG"]
    part = [exp[u["dist_node"]] for u in us if u["class"] == "PART"]
    cl = [exp[u["dist_node"]] for u in us if u["class"] == "CLEAN"]
    mn = [u["class"] for u in us if exp[u["dist_node"]] == "NEG_HIST"]
    return {"recall": (sum(m == "NEG_HIST" for m in neg), len(neg)),
            "recall_lenient": (sum(m in ("NEG_HIST", "UNK_HIST") for m in neg), len(neg)),
            "precision": (sum(c == "NEG" for c in mn), len(mn)),
            "precision_lenient": (sum(c in ("NEG", "PART") for c in mn), len(mn)),
            "clean": (sum(m in CLEAN for m in cl), len(cl)),
            "part": (sum(m in ("NEG_HIST", "UNK_HIST") for m in part), len(part))}
fail = 0
for sp in ("h0", "h1", "all"):
    us = [u for u in U if sp == "all" or u["half"] == sp]
    ks = [k for k in K if sp == "all" or k["half"] == sp]
    want = {k: v for k, v in met([u for u in us if u["reviewed"] == "1"]).items()}
    want.update({k + "_all": v for k, v in met(us).items()})
    want["link_rate"] = (sum(k["status"] == "linked" for k in ks), len(ks))
    got = json.load(open(os.path.join(R, "fake.%s.json" % sp), encoding="utf-8"))
    for k, v in want.items():
        g = got["metrics"][k]
        if (g["k"], g["n"]) != v:
            fail += 1; print("FAIL", sp, k, (g["k"], g["n"]), v)
    print(sp, "checked", len(want), "metrics; n_items", got["link"]["n_items"], "linked", got["link"]["linked"])
cases = list(csv.DictReader(open(os.path.join(R, "fake.cases.tsv"), encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
bad = [c for c in cases if c["mclass"] != exp[c["dist_node"]]]
fail += len(bad)
assert len(cases) == len(U)
assert not any(int(c["dist_node"]) >= 9000000 for c in cases)
print("case rows", len(cases), "mismatches", len(bad))
print("FAILURES", fail)
sys.exit(1 if fail else 0)
