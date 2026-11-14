"""Diagnosis only (h0 misses): the several-candidates cases of C2 -- caption tokens, candidate titles, dates."""
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
orders = R.orders()
stat = collections.Counter()
shown = 0
with open(os.path.join(C2, "round9/agents/shadow9/work/diag_h0.tsv"), encoding="utf-8") as f:
    next(f)
    for line in f:
        p = line.rstrip("\n").split("\t")
        node, era, stage = int(p[0]), p[2], p[7].split("|")[0]
        ords = [int(x) for x in p[8].split(";") if x.strip().isdigit()]
        if era != "post2013":
            continue
        for o in ords:
            rec = cand.get(o)
            if not rec or node not in rec["T"] or len(rec["T"]) < 2:
                continue
            T = rec["T"]
            cap = R.one_caption(orders[o], True)
            octoks = M.toks(cap)
            sc = {t: len(octoks & M.toks(R.title(t))) for t in T}
            latest = max(T, key=lambda t: (T[t]["date"], t))
            best = max(sc.values())
            topn = [t for t in T if sc[t] == best]
            stat["n"] += 1
            stat["target_latest"] += latest == node
            stat["target_maxtok_unique"] += topn == [node]
            stat["maxtok_unique_other"] += len(topn) == 1 and topn != [node]
            if shown < 12:
                shown += 1
                print("=" * 80)
                print(o, orders[o]["date"], cap, sorted(octoks))
                for t in sorted(T, key=lambda t: T[t]["date"]):
                    print("  %s %d %4dd tok%d sibs%d %s" % ("*" if t == node else " ", T[t]["date"], T[t]["days"], sc[t],
                                                           len(T[t]["sibs"]), R.title(t)[:110]))
print(dict(stat))
