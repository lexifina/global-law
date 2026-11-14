"""fjc10: re-trace the v9c FJC h0 misses (fjc9's diag.py, base round9/stage/v9c + round9/out/v9c).

    python -X utf8 diag10.py pairs OUT.tsv            -> (district, appellate) pairs of h0 NEG cited misses
    python -X utf8 diag10.py trace PAIRS.tsv OUT.tsv  -> first failing step per pair (diag.trace_one)

The pairs come from the h0 per-case outcome file of v9c (case identity only: dist_node, app_nodes); no key field is
an input of any rule.
"""
import collections, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FJC9 = os.path.join(C2, "round9", "agents", "fjc9")
sys.path.insert(0, FJC9)
import diag  # noqa: E402

NL = chr(10)
H0 = os.path.join(C2, "round9", "results", "v9c", "bench", "fjc_idb_appeals.h0.cases.tsv")


def base_history():
    by_t = collections.defaultdict(list)
    with open(os.path.join(C2, "round9", "stage", "v9c", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) < 13:
                continue
            try:
                by_t[int(p[1])].append((p[0], int(p[2]), p[4], p[5], p[12]))
            except ValueError:
                continue
    return by_t


def verdicts():
    v = {}
    with open(os.path.join(C2, "round9", "out", "v9c", "certs.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip(NL).split("\t")
            if p[0] == "history":
                v[p[1]] = p[2]
    return v


diag.base_history = base_history
diag.verdicts = verdicts
diag.WORK = os.path.join(FJC9, "work")   # app_shards.json (shard index of CoA opinions) is reused read-only


def pairs(out):
    n = 0
    with open(H0, encoding="utf-8") as f, open(out, "w", encoding="utf-8", newline=NL) as fo:
        hdr = next(f).rstrip(NL).split("\t")
        ix = {k: i for i, k in enumerate(hdr)}
        for line in f:
            p = line.rstrip(NL).split("\t")
            if p[ix["class"]] != "NEG" or p[ix["cited"]] != "1" or p[ix["mclass"]] == "NEG_HIST":
                continue
            for a in p[ix["app_nodes"]].split(","):
                a = a.strip()
                if a and a != "-":
                    fo.write("\t".join([p[ix["dist_node"]], a, p[ix["mclass"]], p[ix["dist_date"]],
                                        p[ix["dist_name"]]]) + NL)
                    n += 1
    print("pairs", n)


if __name__ == "__main__":
    if sys.argv[1] == "pairs":
        pairs(sys.argv[2])
    elif sys.argv[1] == "trace":
        diag.run_trace(sys.argv[2], sys.argv[3])
