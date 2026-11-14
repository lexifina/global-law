"""Compare bridge links with the order's own "Reported below" citation (listcite rows) and with caption rows."""
import json, collections, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
B = {}
for i, l in enumerate(open(os.path.join(HERE, "work", "bridge_links.tsv"), encoding="utf-8")):
    if i == 0:
        continue
    p = l.rstrip("\n").split("\t")
    B[int(p[0])] = (int(p[1]), int(p[2]), p[3])
truth = collections.defaultdict(set)
for l in open(os.path.join(HERE, "rows_listcite.jsonl")):
    r = json.loads(l)
    truth[r["by"]].add(r["target"])
c = collections.Counter()
for o, (t, nb, br) in B.items():
    if o in truth:
        c[t in truth[o]] += 1
print("vs reported-below truth: right", c[True], "wrong", c[False])
oh = {}
for l in open(os.path.join(C2, "round7/agents/orderhead/v2/rows.jsonl")):
    r = json.loads(l)
    oh[r["by"]] = (r["target"], r["rule"], r["kind"])
c2 = collections.Counter()
for o, (t, nb, br) in B.items():
    if o in oh:
        tt, ru, k = oh[o]
        c2[(ru, t == tt)] += 1
print("vs orderHead v2 rows", sorted(c2.items()))
print("orderHead v2 orders with a bridge", sum(1 for o in oh if o in B), "of", len(oh),
      "; GVR", sum(1 for o, v in oh.items() if v[2] == "vacated" and o in B), "of",
      sum(1 for v in oh.values() if v[2] == "vacated"))
