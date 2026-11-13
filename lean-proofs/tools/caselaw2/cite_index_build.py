"""The slice of graph/cite_index.tsv that the certificates use, for the Lean checker.

    python -X utf8 cite_index_build.py [--out W/data/cite_index.tsv]

Used evidences: every target_evidence `cite:<citation>` in treatments.tsv (CERT column 12), history.tsv (10) and
holdings.tsv (10), from both caselaw-lean-2/data/ and caselaw-lean-2/difftest/snap4/. Matching is by the compact form,
as Lean computes it: keep only ASCII letters and digits (Lean's `Char.isAlphanum` is ASCII-only), lowercased;
compact("575 F.3d 432") = "575f3d432".

Output (no header, LF, sorted): citation exactly as in graph/cite_index.tsv, node — every graph key whose compact form
equals the compact form of some used evidence. Statistics (found / not found / ambiguous compact keys / index node
differs from the row's target) are printed.
"""
import argparse, collections, json, os

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
C2 = os.path.join(WORK, "caselaw-lean-2")
GRAPH_IDX = os.path.join(WORK, "graph", "cite_index.tsv")
# file -> (target node column, target_evidence column); holdings have no target: the holding's own node is used
FILES = {"treatments.tsv": (2, 12), "history.tsv": (1, 10), "holdings.tsv": (1, 10)}


def compact(s):
    return "".join(c.lower() for c in s if c.isascii() and c.isalnum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(C2, "data", "cite_index.tsv"))
    a = ap.parse_args()
    uses = {}  # (file, row line) -> (compact, evidence, target)  (the full line dedups data vs snap4)
    for d in ("difftest/snap4", "data"):
        for f, (tc, ec) in FILES.items():
            with open(os.path.join(C2, d, f), "rb") as fh:
                for line in fh:
                    p = line.rstrip(b"\n").decode("utf-8").split("\t")
                    if len(p) <= ec or not p[ec].startswith("cite:"):
                        continue
                    uses[(f, line)] = (compact(p[ec][5:]), p[ec][5:], int(p[tc]))
    want = {c for c, _, _ in uses.values()}
    hits = collections.defaultdict(set)  # compact -> {(citation, node)}
    with open(GRAPH_IDX, "rb") as fh:
        for line in fh:
            p = line.rstrip(b"\n").decode("utf-8").split("\t")
            if len(p) < 2:
                continue
            c = compact(p[0])
            if c in want:
                hits[c].add((p[0], int(p[1])))
    out = sorted({x for s in hits.values() for x in s})
    tmp = a.out + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fo:
        for cit, n in out:
            fo.write(f"{cit}\t{n}\n")
    os.replace(tmp, a.out)
    ev = {e for _, e, _ in uses.values()}
    st = {"out_rows": len(out), "distinct_cite_evidences": len(ev),
          "distinct_compact_evidences": len(want),
          "evidences_found": sum(1 for e in ev if compact(e) in hits),
          "evidences_not_found": sum(1 for e in ev if compact(e) not in hits),
          "compact_keys_ambiguous": sum(1 for c in want if len({n for _, n in hits.get(c, ())}) >= 2)}
    per = collections.Counter()
    ex = collections.defaultdict(list)
    evf = collections.defaultdict(set)
    for (f, line), (c, e, tgt) in sorted(uses.items()):
        rid = line.split(b"\t", 1)[0].decode()
        evf[f].add(e)
        per[f + ":rows"] += 1
        nodes = {n for _, n in hits.get(c, ())}
        if not nodes:
            per[f + ":not_found"] += 1
        elif tgt in nodes:
            per[f + ":index_node_eq_target"] += 1
            if len(nodes) > 1:
                per[f + ":eq_but_ambiguous"] += 1
        else:
            per[f + ":index_node_neq_target"] += 1
            if len(ex[f]) < 5:
                ex[f].append(f"{rid}  cite:{e}  target={tgt}  index={sorted(nodes)}")
    for f, es in evf.items():
        per[f + ":distinct_evidences"] = len(es)
        per[f + ":distinct_evidences_found"] = sum(1 for e in es if compact(e) in hits)
    st["per_file"] = dict(sorted(per.items()))
    st["mismatch_examples"] = ex
    print(json.dumps(st, indent=1))


if __name__ == "__main__":
    main()
