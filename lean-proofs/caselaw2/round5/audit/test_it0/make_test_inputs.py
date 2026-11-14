"""Inputs of the end-to-end test of the audit tools on stage it0_claims (a flow test, not an audit result).

    python round5/audit/test_it0/make_test_inputs.py

Writes, next to this file:
  strata.tsv     the 38 rows of class `recognised` (stratum recognised) + 40 random `selfAnnounced` rows
                 (stratum selfAnnounced-control), from round5/out/it0_claims/classes.tsv
  decoys.jsonl   16 SYNTHETIC decoys, wrong by construction (the real audits get reader answers judged not to be
                 statements from the lead):
                   10 x  a selfAnnounced row's own passage with the X of an unrelated row      (wrong X)
                    6 x  an atRiskWitness row's passage (speaker W) with the Y of another row  (wrong Y)
                 none of the rows used is in strata.tsv.
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R5 = os.path.dirname(os.path.dirname(HERE))
STAGE = os.path.join(R5, "stage", "it0_claims")
OUT = os.path.join(R5, "out", "it0_claims")


def main():
    rnd = random.Random(5)
    cls = {}
    with open(os.path.join(OUT, "classes.tsv"), encoding="utf-8", newline="") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            cls.setdefault(p[1], []).append(p[0])
    rec = sorted(cls["recognised"])
    sa = sorted(cls["selfAnnounced"])
    rnd.shuffle(sa)
    control, spare = sa[:40], sa[40:60]
    wit = {}
    with open(os.path.join(STAGE, "treatment_witness.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            wit[p[0]] = int(p[1])
    arw = sorted(t for t in cls.get("atRiskWitness", []) if t in wit)  # old-format implicit rows have no witness
    rnd.shuffle(arw)
    arw = arw[:12]
    with open(os.path.join(HERE, "strata.tsv"), "w", encoding="utf-8", newline="\n") as f:
        for t in rec:
            f.write("%s\trecognised\n" % t)
        for t in sorted(control):
            f.write("%s\tselfAnnounced-control\n" % t)
    want = set(spare) | set(arw)
    rows = {}
    with open(os.path.join(STAGE, "treatments.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            i = line.find("\t")
            if line[:i] in want:
                p = line.rstrip("\n").split("\t")
                rows[p[0]] = p
    dec = []
    for k in range(10):  # wrong X: passage of row a, target of row b
        a, b = rows[spare[k]], rows[spare[k + 10]]
        dec.append({"id": "wrongX%02d" % k, "speaker": int(a[1]), "x": int(b[2]), "y": None, "start": int(a[9]),
                    "end": int(a[10]), "why": "synthetic: X taken from %s" % b[0]})
    for k in range(6):  # wrong Y: witness passage of row a, by-decision of row b
        a, b = rows[arw[k]], rows[arw[k + 6]]
        dec.append({"id": "wrongY%02d" % k, "speaker": wit[a[0]], "x": int(a[2]), "y": int(b[1]),
                    "start": int(a[9]), "end": int(a[10]), "why": "synthetic: Y taken from %s" % b[0]})
    with open(os.path.join(HERE, "decoys.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for d in dec:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print("strata.tsv: %d recognised + %d selfAnnounced-control; decoys.jsonl: %d" % (len(rec), len(control), len(dec)))


if __name__ == "__main__":
    sys.exit(main())
