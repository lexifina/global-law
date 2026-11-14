"""scdb11: list the sc_row_other_target h0 misses of v10d (diagnosis only; h0 cases file + stage history, no key file).

    python -X utf8 othertgt11.py  -> work/othertgt_v10d.tsv, prints relation counts
"""
import collections, csv, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import r6lib as L  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work")
REVIEW = ("reversed", "vacated", "affirmed", "modified", "reviewDismissed")


def main():
    an = list(csv.DictReader(open(os.path.join(WORK, "anatomy_v10d.tsv"), encoding="utf-8"), delimiter="\t"))
    oth = [x for x in an if x["stage"] == "sc_row_other_target"]
    scn = {int(x["sc"]) for x in oth}
    hist = collections.defaultdict(list)
    allh = collections.defaultdict(list)
    with open(os.path.join(C2, "round10", "stage", "v10d", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            t, by = int(p[1]), int(p[2])
            if by in scn:
                hist[by].append((t, p[4], p[5], p[12]))
            allh[t].append((by, p[4]))
            allh[by].append((t, "by:" + p[4]))
    F = L.Facts()
    st = collections.Counter()
    out = []
    for x in oth:
        n, b = int(x["sc"]), int(x["below"])
        tg = sorted({t for t, k, s, src in hist[n] if k in REVIEW})
        for t in tg:
            ks = ",".join(sorted({k for tt, k, s, src in hist[n] if tt == t}))
            srcs = ",".join(sorted({src for tt, k, s, src in hist[n] if tt == t}))
            same = int(F.court[t]) == int(F.court[b])
            rel = "same_court" if same else "other_court"
            if same:
                rel += ":t_before_b" if F.date[t] < F.date[b] else ":t_after_b" if F.date[t] > F.date[b] else ":same_date"
            link_tb = [k for (o, k) in allh[t] if o == b]
            rel2 = ";".join(link_tb) if link_tb else "-"
            st[rel] += 1
            out.append((x["caseId"], x["era"], x["group"], n, b, int(F.date[b]), F.court_name(int(F.court[b])), t,
                        int(F.date[t]), F.court_name(int(F.court[t])), ks, srcs, rel, rel2))
    with open(os.path.join(WORK, "othertgt_v10d.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("caseId\tera\tgroup\tsc\tbelow\tb_date\tb_court\ttarget\tt_date\tt_court\tkinds\tsrc\trel\thist_t_b\n")
        for o in out:
            f.write("\t".join(str(v) for v in o) + NL)
    print(len(oth), "misses;", len(out), "target rows")
    for k, v in st.most_common():
        print(v, k)


if __name__ == "__main__":
    main()
