"""diagnosis print of C8f picks vs non-key truths (corpus orders only)."""
import os, sys, pickle, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import c8_12 as X
C2 = X.C2
sys.path.insert(0, os.path.join(C2, "round9", "agents", "shadow9"))
import agree as A
tr = A.truths()
cand = pickle.load(open(os.path.join(C2, "round10/agents/shadow10/work/cap_cand.pkl"), "rb"))
F = X.L.Facts()
X.texts({t for r in cand.values() if r.get("has_full") for t in r["T"] if r["T"][t].get("full")})
for o, rec in cand.items():
    t = X.pick(rec, sys.argv[1] if len(sys.argv)>1 else "C8fj1", o)
    if t is None or X.cap10.pick(rec, "C6_fullname_unique_nosib") is not None or o not in tr:
        continue
    ok = t in tr[o]
    if ok and len(sys.argv) < 3: continue
    oo = X.R.orders()[o]
    print("==", "RIGHT" if ok else "WRONG", o, oo["date"], oo.get("docket"), "|", (X.R.one_caption(oo, True) or "")[:80], "te", X.cap10.term_end(o))
    X.texts(list(rec["T"]) + list(tr[o]))
    for c in sorted(set(rec["T"]) | tr[o], key=lambda n: int(F.date[n])):
        r = rec["T"].get(c, {})
        tx = re.sub(r"\s+", " ", X._TX.get(c, ""))
        print("   ", c, int(F.date[c]), "full" if r.get("full") else "    ", "PICK" if c == t else "    ", "TRUTH" if c in tr[o] else "     ", "cand" if c in rec["T"] else "NOTC", len(X._TX.get(c, "")), "|", X.R.title(c)[:60], "|", tx[:150])
