"""b4sc: the round-6 frozen history rows (round6/history/stage/final2/history.tsv) as linker-style rows.

    python -X utf8 final2_rows.py   -> work/final2_hist.jsonl (every row: by, target, kind, scope, rule = src)
                                       work/final2_by.json   (acting nodes that already have a review-kind row)
Used as the proxy baseline (score_rows.py) and to skip acting decisions that are already linked. No answer key.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
HIST = os.path.join(C2, "round6", "history", "stage", "final2", "history.tsv")
REVIEW = {"reversed", "vacated", "affirmed", "modified", "reviewDismissed", "remanded"}


def main():
    os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
    by = {}
    n = 0
    with open(HIST, encoding="utf-8") as f, \
            open(os.path.join(HERE, "work", "final2_hist.jsonl"), "w", encoding="utf-8", newline="\n") as o:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 13:
                continue
            t, b, kind, scope, src = int(p[1]), int(p[2]), p[4], p[5], p[12]
            o.write(json.dumps({"rule": "final2:" + src.split(":")[0], "by": b, "target": t, "kind": kind,
                                "scope": scope}) + "\n")
            n += 1
            if kind in REVIEW:
                by.setdefault(str(b), []).append(t)
    json.dump(by, open(os.path.join(HERE, "work", "final2_by.json"), "w"))
    print("rows", n, "acting nodes with a review row", len(by))


if __name__ == "__main__":
    main()
