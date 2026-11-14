"""Diagnosis only (h0 per-case file of v9c via round9 shadow9 work/diag_h0.tsv): cap10 rule links on h0 misses."""
import collections
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cap10  # noqa: E402

C2 = cap10.C2
cand = pickle.load(open(os.path.join(HERE, "work", "cap_cand.pkl"), "rb"))
miss = []
with open(os.path.join(C2, "round9/agents/shadow9/work/diag_h0.tsv"), encoding="utf-8") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        miss.append((int(p[0]), int(p[1]), p[2], p[7], [int(x) for x in p[8].split(";") if x.strip().isdigit()]))
for rule in cap10.RULES:
    c = collections.Counter()
    for node, od, era, stage, ords in miss:
        got = set()
        for o in ords:
            if o in cand:
                t = cap10.pick(cand[o], rule, o)
                if t is not None:
                    got.add(t)
        if not got:
            continue
        k = "right" if node in got else "wrong"
        c[k] += 1
        c[k + "_" + era] += 1
        c[k + "_" + stage.split("|")[0]] += 1
    print(rule, dict(sorted(c.items())))
