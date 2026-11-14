"""fjc8: `oldCircuit` history claims (DESIGN8 section 6, D8-12), selected by rule from a history table.

    python -X utf8 oldcircuit.py HISTORY.tsv OUT_CLAIMS.tsv [--src fjc8:oldCircuit]

A row gets the claim when its acting decision is a federal court of appeals of circuit 5 dated before 1981-10-01 and
its target a federal district or bankruptcy court whose circuit (courts2) is 11, or acting circuit 8 before
1929-03-01 and target circuit 10. Kinds: every history kind (Lean checks authority only for status-changing rows).
Claim line: id TAB oldCircuit TAB src.
"""
import argparse, collections, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from diag import BO, L  # noqa: E402

NL = chr(10)
TRIPLES = ((5, 11, 19811001), (8, 10, 19290301))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("history")
    ap.add_argument("out")
    ap.add_argument("--src", default="fjc8:oldCircuit")
    a = ap.parse_args()
    BO.init()
    F, circ = BO.G["F"], BO.G["circ"]
    n = collections.Counter()
    with open(a.history, encoding="utf-8") as f, open(a.out, "w", encoding="utf-8", newline=NL) as fo:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) < 13:
                continue
            try:
                t, by = int(p[1]), int(p[2])
            except ValueError:
                continue
            bc, tc = int(F.court[by]), int(F.court[t])
            if F.system(bc) != 0 or F.system(tc) != 0:
                continue
            bd = int(F.date[by])
            bname, btier = BO.court_at(bc, bd)
            tname, ttier = BO.court_at(tc, int(F.date[t]))
            if btier != "A" or ttier not in ("T", "S"):
                continue
            tl = tname.lower()
            if "district court" not in tl and "bankruptcy" not in tl:
                continue
            for cb, ct, before in TRIPLES:
                if circ.get(bc) == cb and circ.get(tc) == ct and 0 < bd < before:
                    fo.write("\t".join((p[0], "oldCircuit", a.src)) + NL)
                    n[(cb, ct, p[4])] += 1
                    break
    for k, v in sorted(n.items()):
        print(v, *k)
    print("claims", sum(n.values()))


if __name__ == "__main__":
    main()
