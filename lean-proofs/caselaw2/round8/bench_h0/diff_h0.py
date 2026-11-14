"""Round 8: compare two builds' h0 benchmark results (agent infra; for diagnosis agents).

    python round8/bench_h0/diff_h0.py A B [--tsv FILE] [--show N]

A, B: labels (round8/results/<label>/bench/, written by score_h0.py) or result folders. Prints, per key, every
metric whose k/n changed (A -> B), then the h0 cases whose outcome flips: per key the case id, its class in the key,
the model class (or outcome) in A and in B, and the agreement in A and in B. --tsv writes every flip (key, case,
class, a_model, b_model, a_agree, b_agree, change); --show N prints at most N flips per key (default 20). Reads only
the h0 files under round8/results/; nothing under benchmarks/.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(HERE))
# key -> (case id column, class column, model column, agree column)
CASES = {"fjc_idb_appeals": ("dist_node", "class", "mclass", "agree"),
         "shadow_docket": ("node", "class", "model_class", "agree"),
         "scdb_disposition": ("caseId", "class", "mclass", "agree"),
         "state_overruled_tables": ("x_node", "partial", "outcome", "outcome")}
FILES = ["fjc_idb_appeals", "shadow_docket", "scdb_disposition", "scdb_disposition.federal",
         "scdb_disposition.state", "state_overruled_tables"]


def folder(x):
    if os.path.isdir(x):
        return x
    p = os.path.join(C2, "round8", "results", x, "bench")
    if not os.path.isdir(p):
        sys.exit("no results folder for %s" % x)
    return p


def load_cases(d, key):
    p = os.path.join(d, "%s.h0.cases.tsv" % key)
    if not os.path.exists(p):
        return None
    out = {}
    with open(p, encoding="utf-8") as f:
        hdr = f.readline().rstrip("\n").split("\t")
        for line in f:
            r = dict(zip(hdr, line.rstrip("\n").split("\t")))
            out[r[CASES[key][0]]] = r
    return out


def agree_of(key, r):
    if key == "state_overruled_tables":
        return "1" if r["outcome"] == "hit" else "0"
    return r[CASES[key][3]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--tsv")
    ap.add_argument("--show", type=int, default=20)
    a = ap.parse_args()
    da, db = folder(a.a), folder(a.b)
    print("A = %s\nB = %s" % (os.path.relpath(da, C2), os.path.relpath(db, C2)))
    for name in FILES:
        pa, pb = (os.path.join(d, "%s.h0.json" % name) for d in (da, db))
        if not (os.path.exists(pa) and os.path.exists(pb)):
            continue
        ma, mb = (json.load(open(p, encoding="utf-8")) for p in (pa, pb))
        ch = []
        for part in ("metrics", "extra_metrics"):
            for k in (mb.get(part) or {}):
                va, vb = (ma.get(part) or {}).get(k), mb[part][k]
                if va is None or (va["k"], va["n"]) != (vb["k"], vb["n"]):
                    ch.append("%s%s %s -> %d/%d" % ("" if part == "metrics" else "x:", k,
                                                    "-" if va is None else "%d/%d" % (va["k"], va["n"]),
                                                    vb["k"], vb["n"]))
        prim = mb["primary"]
        pa_, pb_ = ma["metrics"][prim], mb["metrics"][prim]
        print("%-26s %s %d/%d -> %d/%d%s" % (name, prim, pa_["k"], pa_["n"], pb_["k"], pb_["n"],
                                             ("; changed: " + "; ".join(ch)) if ch else "; no metric changed"))
    rows = []
    for key in CASES:
        ca, cb = load_cases(da, key), load_cases(db, key)
        if ca is None or cb is None:
            continue
        idc, clc, mc, _ = CASES[key]
        flips = collections.Counter()
        shown = 0
        for cid in sorted(set(ca) | set(cb), key=lambda x: (len(x), x)):
            ra, rb = ca.get(cid), cb.get(cid)
            if ra is None or rb is None:
                flips["case only in " + ("B" if ra is None else "A")] += 1
                continue
            ga, gb = agree_of(key, ra), agree_of(key, rb)
            if ra[mc] == rb[mc] and ga == gb:
                continue
            change = "gained" if (ga, gb) == ("0", "1") else "lost" if (ga, gb) == ("1", "0") else "model changed"
            flips[change] += 1
            cls = rb.get(clc, "-") if key != "state_overruled_tables" else "listed"
            rows.append((key, cid, cls, ra[mc], rb[mc], ga, gb, change))
            if shown < a.show:
                print("  %-22s %-10s class %-6s %s -> %s (agree %s -> %s) %s" % (key, cid, cls, ra[mc], rb[mc],
                                                                                 ga, gb, change))
                shown += 1
        print("%-26s h0 cases changed: %s" % (key, dict(flips) or "none"))
    if a.tsv:
        with open(a.tsv, "w", encoding="utf-8", newline="\n") as f:
            f.write("key\tcase\tclass\ta_model\tb_model\ta_agree\tb_agree\tchange\n")
            for r in rows:
                f.write("\t".join(r) + "\n")


if __name__ == "__main__":
    main()
