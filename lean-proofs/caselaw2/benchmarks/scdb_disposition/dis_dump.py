#!/usr/bin/env python3
"""Dump a fixed random sample of disagreements for reading (DISAGREEMENTS.md).

python -I dis_dump.py --label round6 [--data <stage dir>] [--seed 13] > work/dis_round6.txt
Sample: 16 NEG->GOOD/other-clean, 4 NEG->UNK_HIST, 8 CLEAN->NEG_HIST, 2 PART->clean (fewer if not available).
For each: SCDB row, the citation context of the below decision in our SC text, the end of the SC opinion section
(disposition), the model status, and every history.tsv row targeting the below decision (kind, by, quote).
"""
import argparse
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import link as L  # noqa: E402
import ctx as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--data")
    ap.add_argument("--seed", type=int, default=13)
    a = ap.parse_args()
    data = a.data or L.benchlib.BUILDS[a.label][1]
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cases = list(C.rows(os.path.join(HERE, "results", "%s.cases.tsv" % a.label)))
    rnd = random.Random(a.seed)
    pick = []
    for cond, k in ((lambda c: c["class"] == "NEG" and c["mclass"] != "NEG_HIST" and c["mclass"] != "UNK_HIST", 16),
                    (lambda c: c["class"] == "NEG" and c["mclass"] == "UNK_HIST", 4),
                    (lambda c: c["class"] == "CLEAN" and c["mclass"] == "NEG_HIST", 8),
                    (lambda c: c["class"] == "PART" and c["agree"] == "0", 2)):
        pool = sorted((c for c in cases if cond(c)), key=lambda c: c["caseId"])
        rnd.shuffle(pool)
        pick += pool[:k]
    want = {c["below"] for c in pick}
    hist = {}
    with open(os.path.join(data, "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[1] in want:
                hist.setdefault(p[1], []).append(p)
    lk = {r["caseId"]: r for r in C.rows(os.path.join(HERE, "links.tsv"))}
    ns = [int(c["sc_node"]) for c in pick] + [int(c["below"]) for c in pick]
    nr = C.node_rows(ns)
    for i, c in enumerate(pick, 1):
        sn, b = int(c["sc_node"]), int(c["below"])
        print("=" * 100)
        print("#%d %s | %s | disp %s %s/%s | model %s %s path=%s actor=%s | hist_by_sc=%s" % (
            i, c["caseId"], c["caseName"], c["caseDisposition"], c["class"], c["sub"], c["mclass"], c["status"],
            c["path"], c["actor"], c["hist_by_sc"]))
        print("  SC %d %s %s | BELOW %d %s %s %s | %s" % (sn, nr[sn][4], nr[sn][5].split("|")[0], b, nr[b][1],
                                                       nr[b][4], nr[b][5][:50], nr[b][6]))
        print("  link:", lk[c["caseId"]]["method"], lk[c["caseId"]]["below_court_name"])
        tx = L.fetch("supreme-court", [(sn, nr[sn][2])])[sn]
        head, opening = L.region(tx)
        keys = set()
        for cc in nr[b][5].split("|"):
            keys.update(L.cite_keys(cc))
        for where, t in (("head", head), ("open", opening)):
            for m in L.r6cite.finditer(t):
                if set(L.r6cite.keys(m)) & keys:
                    print("  [%s] ...%s..." % (where, re.sub(r"\s+", " ", t[max(0, m.start() - 260):m.end() + 80])))
        body = tx
        if body.startswith("---"):
            body = body[body.find("\n---", 3) + 4:]
        secs = re.split(r"^## .+$", body, flags=re.M)
        first_op = secs[2] if len(secs) > 2 else body
        print("  [end of first opinion section] ...%s" % re.sub(r"\s+", " ", first_op[-450:]))
        print("  [total text chars %d; sections %d]" % (len(tx), len(secs) - 1))
        for p in hist.get(c["below"], []):
            print("  HIST %s by=%s date=%s kind=%s scope=%s src=%s quote=%s" % (p[0], p[2], p[3], p[4], p[5],
                                                                             p[-1], p[9][:200]))


if __name__ == "__main__":
    main()
