"""scdb8: show the round-8 rows behind h0 cases that flipped (diagnosis; reads the h0 cases file and a flips tsv).

    python -X utf8 lost8.py <flips.tsv> <delta history_delta.tsv> [change ...]
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402


def main():
    flips, delta = sys.argv[1], sys.argv[2]
    want = set(sys.argv[3:]) or {"lost", "model changed"}
    cases = {x["caseId"]: x for x in csv.DictReader(open(os.path.join(C2, "round8", "results", "v3", "bench",
                                                                         "scdb_disposition.h0.cases.tsv"), encoding="utf-8"), delimiter="\t")}
    rows = {}
    anc = {}
    for l in open(delta, encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        rows.setdefault(p[2], []).append(p)
    ap = os.path.join(os.path.dirname(delta), "history_anchor_delta.tsv")
    for l in open(ap, encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        anc[p[0]] = p[3] if len(p) > 3 else ""
    F = L.Facts()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for x in csv.DictReader(open(flips, encoding="utf-8"), delimiter="\t"):
        if x["key"] != "scdb_disposition" or x["change"] not in want:
            continue
        c = cases[x["case"]]
        print("=" * 100)
        print(x["case"], x["class"], c["caseDisposition"], x["a_model"], "->", x["b_model"], "| SC", c["sc_node"],
              c["caseName"][:60], "| below", c["below"], c["below_name"][:50])
        for p in rows.get(c["sc_node"], []):
            print("  ROW", p[0], "target", p[1], F.court_name(F.court[int(p[1])])[:40], p[4], p[5], p[12])
            print("     disp:", p[9][:300])
            print("     anchor:", anc.get(p[0], "")[:300])


if __name__ == "__main__":
    main()
