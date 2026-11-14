"""diagnosis reader packs (corpus text only): unlinked order-list nodes whose caption gives a full name (C8 domain
left unlinked). Items listed by local id on the command line; candidates = both-sides candidates, 12 latest before
the order. No key field is written into the pack."""
import os, pickle, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c8_12 as X
recs = pickle.load(open("work/c8_recs_r12sub.pkl", "rb"))
F = X.L.Facts()
out = sys.argv[1]
lids = sys.argv[2:]
L = []
for i, lid in enumerate(lids, 1):
    n, rec, d, dk, title = recs[lid]
    node_text = open(os.path.join(X.C2, "round12/data_orders/text", lid + ".txt"), encoding="utf-8").read()
    cands = sorted(rec["T"], key=lambda c: -int(F.date[c]))[:12]
    X.texts(cands)
    L.append("\n## Item %d\n\n### The order (Supreme Court order-list entry, %s)\n\n```\n%s\n```\n" % (i, d, node_text.strip()[:2500]))
    for j, c in enumerate(sorted(cands, key=lambda c: int(F.date[c])), 1):
        tx = X._TX.get(c, "")
        m = re.search(r'docket:\s*"([^"]*)"', tx[:1500])
        body = tx[tx.find("---", 3) + 3:] if tx.startswith("---") else tx
        L.append("#### Candidate %d.%d: node %d, %s, docket %s, decided %d\n\n```\n%s\n```\n" % (
            i, j, c, X.R.title(c)[:100], m.group(1) if m else "?", int(F.date[c]), re.sub(r"\s+", " ", body[:1400])))
open(out, "w", encoding="utf-8", newline="\n").write("".join(L))
print(out, len(lids))
