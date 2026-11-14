"""scdb8: anatomy of the SCDB-disposition h0 misses of a build (diagnosis only; reads the h0 cases file of the base,
never a key file). For each NEG case the model does not show NEG_HIST: where is it lost?

    python -X utf8 anatomy8.py [--cases round8/results/v3/bench/scdb_disposition.h0.cases.tsv] [--diag work/diag8.jsonl.gz]
        -> work/anatomy.tsv, prints counts

Stages (first that applies):
  partial      the model shows UNK_HIST (a row exists; scope or conflict)
  sc_row_other_kind  the SC opinion has a history row on the decision below of a non-negative kind
  sc_row_other_target  the SC opinion has review rows, but on another decision
  not_stored   the SC node is not among the stored SC texts (memorandum order type)
  <reason>     the linker's no-row reason for the SC opinion (no_opinion_part, no_disposition, disp_not_strong,
               no_lower_cite ...), split into below_cited (the decision below is a candidate) or below_not_cand
  row_not_in_v3  the linker makes a row for the decision below that is not in the v3 history (not installed / refused)
"""
import collections, csv, gzip, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
NL = chr(10)
WORK = os.path.join(HERE, "work")


def era(cid):
    y = int(cid[:4])
    return "pre1900" if y < 1900 else "1900-45" if y < 1946 else "1946-90" if y < 1991 else "1991+"


def main():
    args = sys.argv[1:]
    cases = os.path.join(C2, "round8", "results", "v3", "bench", "scdb_disposition.h0.cases.tsv")
    dpath = os.path.join(WORK, "diag8.jsonl.gz")
    if "--cases" in args:
        cases = args[args.index("--cases") + 1]
    if "--diag" in args:
        dpath = args[args.index("--diag") + 1]
    rows = list(csv.DictReader(open(cases, encoding="utf-8"), delimiter="\t"))
    miss = [x for x in rows if x["class"] == "NEG" and x["mclass"] != "NEG_HIST"]
    scn = {int(x["sc_node"]) for x in miss}
    diag = {}
    with gzip.open(dpath, "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if d["n"] in scn:
                diag[d["n"]] = d
    hist = collections.defaultdict(list)
    with open(os.path.join(C2, "round7", "stage", "v3", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if int(p[2]) in scn:
                hist[int(p[2])].append((int(p[1]), p[4], p[5], p[12]))
    st = collections.Counter()
    out = []
    for x in miss:
        n, b = int(x["sc_node"]), int(x["below"])
        h = hist.get(n, [])
        d = diag.get(n)
        on_b = [k for t, k, s, src in h if t == b]
        rev = [t for t, k, s, src in h if k in ("reversed", "vacated", "affirmed", "modified", "reviewDismissed")]
        cand = bool(d and any(c["j"] == b for c in d.get("cands", []) or []))
        made = [r for r in (d or {}).get("rows", []) if r["target"] == b]
        made_other = [r for r in (d or {}).get("rows", []) if r["target"] != b]
        if x["mclass"] == "UNK_HIST":
            stage = "partial"
        elif on_b:
            stage = "sc_row_other_kind:" + ",".join(sorted(set(on_b)))
        elif rev:
            stage = "sc_row_other_target"
        elif d is None:
            stage = "not_stored"
        elif made:
            stage = "row_not_in_v3:" + made[0]["rule"]
        elif made_other:
            stage = "linker_other_target"
        else:
            stage = (d.get("reason") or "?") + (":below_cand" if cand else ":below_not_cand")
        st[stage] += 1
        out.append((x["caseId"], era(x["caseId"]), x["group"], n, b, x["mclass"], stage,
                    (d or {}).get("disp_text", "")[:160].replace("\t", " ").replace(NL, " ")))
    with open(os.path.join(WORK, "anatomy.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("caseId\tera\tgroup\tsc\tbelow\tmclass\tstage\tdisp\n")
        for o in out:
            f.write("\t".join(str(v) for v in o) + NL)
    print("misses", len(miss))
    for k, v in st.most_common():
        print(v, k)


if __name__ == "__main__":
    main()
