"""diag step 2: the D test. Later statements "X was overruled by Y" for the 66 decisions.

(i)  data/treatment_witness.tsv + data/treatments.tsv  (ids tw:Y:X:start:W)
(ii) gold/reports_typed.tsv restricted to round5/tests/split/feed_ids.tsv
     kept rows: by_node in Yset, or target_node in Xset (to see notes whose by was not resolved)

Writes d_witness.tsv and d_notes.tsv under round5/diag/ and prints a summary. W's court from data/decisions2.tsv
(streamed, filtered by node id).
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(HERE))
csv.field_size_limit(1 << 30)


def main():
    pairs = []
    with open(os.path.join(HERE, "pairs.tsv"), encoding="utf-8", newline="") as f:
        pairs = list(csv.DictReader(f, delimiter="\t"))
    extra = os.path.join(HERE, "pairs_extra.tsv")
    if os.path.exists(extra):
        with open(extra, encoding="utf-8", newline="") as f:
            pairs += list(csv.DictReader(f, delimiter="\t"))
    ys = {p["by_node"] for p in pairs}
    xs = {p["target_node"] for p in pairs if p["target_node"] not in ("-1", "-2", "")}
    pairset = {(p["by_node"], p["target_node"]) for p in pairs}

    # (i) witness rows
    wit = {}
    with open(os.path.join(C2, "data/treatment_witness.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            wit[p[0]] = p
    wrows = []
    with open(os.path.join(C2, "data/treatments.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[0] in wit:
                parts = p[0].split(":")
                y, x, w = parts[1], parts[2], parts[4]
                if y in ys or x in xs:
                    wrows.append((y, x, w, p, wit[p[0]]))
    # (ii) notes in the feed
    feed = set()
    with open(os.path.join(C2, "round5/tests/split/feed_ids.tsv"), encoding="utf-8", newline="") as f:
        next(f)
        for line in f:
            feed.add(line.split("\t", 1)[0])
    notes = []
    with open(os.path.join(C2, "gold/reports_typed.tsv"), encoding="utf-8", newline="") as f:
        rd = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        for r in rd:
            if r["id"] not in feed:
                continue
            if r["by_node"] in ys or r["target_node"] in xs:
                notes.append(r)
    need = {w for _, _, w, _, _ in wrows} | {r["note_node"] for r in notes}
    court = {}
    with open(os.path.join(C2, "data/decisions2.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            t = line.find("\t")
            n = line[:t]
            if n in need:
                p = line.split("\t", 4)
                court[n] = (p[1], p[2])
                if len(court) == len(need):
                    break
    ycourt = {}
    with open(os.path.join(HERE, "nodes_meta.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            ycourt[p[0]] = p[3]
    scotus = {ycourt[y] for y in ys if y in ycourt}
    print("SCOTUS court ids (from Y nodes):", scotus)
    with open(os.path.join(HERE, "d_witness.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("by_node\ttarget_node\twitness_node\twitness_court\twitness_date\tkind\tquote\tby_evidence\tid\tpair_in_66\n")
        for y, x, w, p, wl in sorted(wrows):
            c = court.get(w, ("?", "?"))
            f.write("\t".join([y, x, w, c[0], c[1], p[4], p[11], wl[2], p[0],
                               "1" if (y, x) in pairset else "0"]) + "\n")
    with open(os.path.join(HERE, "d_notes.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("by_node\ttarget_node\tnote_node\tnote_court\tnote_date\tkind\tscope\timplicit\tform\tqual\tsec\tid\tpair_in_66\tsnippet\n")
        for r in sorted(notes, key=lambda r: (r["by_node"], r["target_node"], r["note_date"])):
            c = court.get(r["note_node"], ("?", "?"))
            f.write("\t".join([r["by_node"], r["target_node"], r["note_node"], c[0], r["note_date"], r["kind"],
                               r["scope"], r["implicit"], r["form"], r["qual"], r["sec"], r["id"],
                               "1" if (r["by_node"], r["target_node"]) in pairset else "0",
                               r["snippet"].replace("\t", " ")]) + "\n")
    print("witness rows touching the 66:", len(wrows), "exact pairs:", sum((y, x) in pairset for y, x, *_ in wrows))
    print("feed notes touching the 66:", len(notes), "exact pairs:",
          sum((r["by_node"], r["target_node"]) in pairset for r in notes))


if __name__ == "__main__":
    main()
