"""diagnosis: candidates of given order-list nodes (C8 domain) with dates, full marks, JUDG flags, heads."""
import os, pickle, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c8_12 as X
recs = pickle.load(open(sys.argv[1], "rb"))
F = X.L.Facts()
extra = {int(x.split("=")[1]) for x in sys.argv[2:] if "=" in x}
for lid in [x for x in sys.argv[2:] if "=" not in x]:
    n, rec, d, dk, title = recs[lid]
    X.texts(list(rec["T"]) + list(extra))
    X.R.orders()[n] = {"docket": dk, "date": d}
    t = X.pick(rec, "C8fj", n)
    te = X.cap10.term_end(n)
    print("==", lid, d, dk, title[:70], "te", te, "pick", t)
    for c in sorted(set(rec["T"]) | extra, key=lambda c: int(F.date[c])):
        if c not in rec["T"] and int(F.court[c]) != rec["T"][next(iter(rec["T"]))]["court"]:
            continue
        r = rec["T"].get(c, {})
        tx = X._TX.get(c, "")
        j = tx.find("## Majority")
        print("   ", c, int(F.date[c]), "full" if r.get("full") else "----", "NJ" if X.not_judgment(c) else "  ",
              "cite" if X.has_cite(c) else "    ", "cand" if c in rec["T"] else "XTRA", len(tx), "|", X.R.title(c)[:55], "|",
              re.sub(r"\s+", " ", tx[j:j + 160] if j >= 0 else tx[:160]))
