"""Diagnosis only (h0 misses of v9c, round9 shadow9 work/diag_h0.tsv): why rule C2 does not link a miss."""
import collections
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cap10  # noqa: E402

R, M, L = cap10.R, cap10.M, cap10.L
C2 = cap10.C2
cand = pickle.load(open(os.path.join(HERE, "work", "cap_cand.pkl"), "rb"))
F = L.Facts()
orders = R.orders()
c = collections.Counter()
ex = collections.defaultdict(list)
with open(os.path.join(C2, "round9/agents/shadow9/work/diag_h0.tsv"), encoding="utf-8") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        node, era, stage = int(p[0]), p[2], p[7].split("|")[0]
        ords = [int(x) for x in p[8].split(";") if x.strip().isdigit()]
        if era != "post2013" or stage not in ("no_signal", "cap_only_right", "cap_only_other"):
            continue
        why = None
        for o in ords:
            od = orders.get(o)
            if od is None:
                why = why or "order_not_in_memo"
                continue
            if od["kind"] not in ("vacated", "reversed"):
                why = "kind_" + od["kind"]
                continue
            ks = {k for k in od["courts"] if k is not None}
            if len(ks) != 1:
                why = "courts_%d" % len(ks)
                continue
            if R.one_caption(od, True) is None:
                why = "caption_%d" % len(od["caps"])
                continue
            rec = cand.get(o)
            if rec is None:
                why = "no_both_sides_candidate"
                continue
            T = rec["T"]
            if node not in T:
                why = "target_not_candidate(%d cands)" % len(T)
                continue
            if len(T) > 1:
                why = "several_candidates"
                continue
            if T[node]["sibs"]:
                why = "sibling_on_docket"
                continue
            why = "linked"
            break
        c[why] += 1
        ex[why].append((node, ords[:2]))
for k, v in c.most_common():
    print(v, k, ex[k][:4])
