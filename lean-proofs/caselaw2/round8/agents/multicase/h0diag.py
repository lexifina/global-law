"""Round 8, agent `multicase`: h0 diagnosis (counts only) on the state overruled tables.

    python -X utf8 h0diag.py [--cases round8/results/v3/bench/state_overruled_tables.h0.cases.tsv] [--rows rows.jsonl]

Reads ONLY the h0 per-case outcomes file written by agent infra (allowed by DESIGN8 0.2 (b)); never benchmarks/.
For each h0 case that is not a hit, and each listed overruler Y: does the scan hold an act sentence of Y (any), an
MC-OWN sentence of Y, a candidate of Y naming X (resolved target), a read item, a row (rows.jsonl) for (Y, X)?
Prints counts per stage. Nothing here feeds any rule: the key is used for counting after the fact only.
"""
import argparse, collections, glob, gzip, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default=os.path.join(C2, "round8", "results", "v3", "bench",
                                                    "state_overruled_tables.h0.cases.tsv"))
    ap.add_argument("--rows", default=os.path.join(HERE, "rows.jsonl"))
    a = ap.parse_args()
    lines = open(a.cases, encoding="utf-8").read().splitlines()
    hd = lines[0].split("\t")
    cases = [dict(zip(hd, l.split("\t"))) for l in lines[1:]]
    miss = [c for c in cases if c["outcome"] != "hit"]
    ys = {int(y) for c in miss for y in c["listed_overrulers"].split(",") if y.strip().isdigit()}
    scan_n = collections.Counter()
    for p in glob.glob(os.path.join(HERE, "scan", "*.jsonl.gz")):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                i = line.find('"n":')
                n = int(line[i + 4:line.find(",", i)])
                if n in ys:
                    scan_n[n] += 1
    cand_pairs, cand_y = {}, set()
    for line in gzip.open(os.path.join(HERE, "cands.jsonl.gz"), "rt", encoding="utf-8"):
        r = json.loads(line)
        if r["n"] in ys:
            cand_y.add(r["n"])
            for t in r["targets"]:
                cand_pairs[(r["n"], t["t"])] = r["id"]
    read = set()
    if os.path.exists(os.path.join(HERE, "packs", "index.tsv")):
        read = {l.split("\t")[0] for l in open(os.path.join(HERE, "packs", "index.tsv"), encoding="utf-8")}
    rows = set()
    if os.path.exists(a.rows):
        for line in open(a.rows, encoding="utf-8"):
            r = json.loads(line)
            rows.add((r["by"], r["target"]))
    st = collections.Counter()
    for c in miss:
        x = int(c["x_node"])
        yl = [int(y) for y in c["listed_overrulers"].split(",") if y.strip().isdigit()]
        stage = "0_no_scan_sentence_of_Y"
        if any(scan_n[y] for y in yl):
            stage = "1_scan_sentence_of_Y_not_own_or_lt2"
        if any(y in cand_y for y in yl):
            stage = "2_own_candidate_of_Y_not_naming_X"
        if any((y, x) in cand_pairs for y in yl):
            stage = "3_candidate_names_X_not_read"
            if any(cand_pairs.get((y, x)) in read for y in yl):
                stage = "4_read_no_row"
        if any((y, x) in rows for y in yl):
            stage = "5_row"
        st[stage] += 1
    st["misses"] = len(miss)
    st["cases"] = len(cases)
    print(json.dumps(dict(sorted(st.items())), indent=1))


if __name__ == "__main__":
    main()
