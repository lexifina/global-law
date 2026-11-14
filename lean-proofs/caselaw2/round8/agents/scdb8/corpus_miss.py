"""scdb8: corpus-wide picture (no key): Supreme Court opinions whose final judgment line (round-6/7 reading) is
negative (reverse / vacate) but that have no negative review row in v3 history; counted by the round-7 no-row reason.

    python -X utf8 corpus_miss.py  -> work/corpus_miss.json, work/corpus_miss_nodes.tsv
"""
import collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work")
NEG = re.compile(r"\b(?:revers|vacat)", re.I)


def main():
    idx = json.load(open(os.path.join(WORK, "diag7_index.json"), encoding="utf-8"))
    by_rows = collections.defaultdict(set)
    with open(os.path.join(C2, "round7", "stage", "v3", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            by_rows[int(p[2])].add(p[4])
    st = collections.Counter()
    era = collections.Counter()
    rows = []
    for k, d in idx.items():
        n = int(k)
        dt = d.get("disp_text") or ""
        if not dt or not NEG.search(dt):
            continue
        st["neg_disp"] += 1
        kinds = by_rows.get(n, set())
        if kinds & {"reversed", "vacated", "modified"}:
            st["has_neg_row"] += 1
            continue
        if kinds:
            st["has_other_row:" + ",".join(sorted(kinds))] += 1
        r = d.get("reason") or ("rows_not_in_v3" if d.get("rows") else "?")
        st["miss:" + r] += 1
        y = d["date"] // 10000
        e = "pre1900" if y < 1900 else "1900-45" if y < 1946 else "1946-90" if y < 1991 else "1991+"
        era[(e, r)] += 1
        rows.append((n, d["date"], r))
    json.dump({"stats": st, "era": {"%s|%s" % k: v for k, v in era.items()}}, open(os.path.join(WORK, "corpus_miss.json"), "w"),
              indent=1, sort_keys=True)
    with open(os.path.join(WORK, "corpus_miss_nodes.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for n, dt, r in sorted(rows):
            f.write("%d\t%d\t%s\n" % (n, dt, r))
    for k, v in st.most_common():
        print(v, k)


if __name__ == "__main__":
    main()
