#!/usr/bin/env python3
"""Score one model build on the SCDB disposition key (MAPPING.md).

python -I score.py --out <dir> --data <dir> --label <x> [--asof yyyymmdd]
  e.g. --label round6 --out ../../round6/history/out/final2 --data ../../round6/history/stage/final2
  or just --label round4 / round6 (dirs taken from benchlib.BUILDS when --out/--data are omitted).

Writes results/<label>.<split>.json (dataset scdb_disposition, court mixed),
       results/<label>.federal.<split>.json (dataset scdb_disposition_federal),
       results/<label>.state.<split>.json   (dataset scdb_disposition_state)   for split in h0, h1, all,
       and results/<label>.cases.tsv (one row per linked scored case).
Reads key.tsv (link.py) and the build's status.tsv / history.tsv / certs.tsv (read only).
"""
# round 8 h0 shadow (agent infra): copy of benchmarks/scdb_disposition/score.py; changes: paths, results folder (--results), h0-only
# output (see round8/bench_h0/README.md). Reads the h0 key written by round8/bench_h0/build_keys.py.
import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
import benchlib  # noqa: E402

DATASET = "scdb_disposition"
CLEANSET = {"GOOD", "NEG_OTHER", "UNK_OTHER"}
STATE_SOURCES = {"300", "301", "302", "15", "16", "17"}
EXPECT_KIND = {"reversed": "neg:reversed", "vacated": "neg:vacated"}


def rows(p):
    with open(p, encoding="utf-8") as f:
        h = next(f).rstrip("\n").split("\t")
        for line in f:
            yield dict(zip(h, line.rstrip("\n").split("\t")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--data")
    ap.add_argument("--label", required=True)
    ap.add_argument("--asof", type=int, default=benchlib.DEFAULT_ASOF)
    ap.add_argument("--results", required=True)
    a = ap.parse_args()
    if not a.out or not a.data:
        if a.label not in benchlib.BUILDS:
            ap.error("--out and --data are required for label %s" % a.label)
        a.out = a.out or benchlib.BUILDS[a.label][0]
        a.data = a.data or benchlib.BUILDS[a.label][1]

    key = list(rows(os.path.join(HERE, "key.tsv")))
    scored = [r for r in key if r["scored"] == "1"]
    linked = [r for r in scored if r["linked"] == "1"]
    nodes = {r["below"] for r in linked}
    st = benchlib.load_status(a.out, nodes=nodes, asof=a.asof)
    hist = benchlib.load_history(a.out, a.data, nodes)
    status_sha1 = benchlib.file_sha1(os.path.join(a.out, "status.tsv"))

    resdir = a.results
    os.makedirs(resdir, exist_ok=True)
    cases = []
    for r in linked:
        s = benchlib.status_of(st, r["below"])
        sc = r["sc_node"]
        hs = [h for h in hist.get(r["below"], []) if h["admitted"] and int(h["date"] or 0) <= a.asof]
        by_sc = sorted({h["kind"] for h in hs if h["by"] == sc})
        cls = r["class"]
        mc = s["mclass"]
        if cls == "NEG":
            agree = mc == "NEG_HIST"
        elif cls == "PART":
            agree = mc in ("NEG_HIST", "UNK_HIST")
        else:
            agree = mc in CLEANSET
        kind_ok = ""
        actor_ok = ""
        if cls == "NEG" and mc == "NEG_HIST":
            kind_ok = int(s["status"] == EXPECT_KIND[r["sub"]])
            actor_ok = int(s["actor"] == sc)
        cases.append({"caseId": r["caseId"], "half": r["half"], "class": cls, "sub": r["sub"],
                      "caseDisposition": r["caseDisposition"], "group": r["below_group"], "sc_node": sc,
                      "below": r["below"], "below_date": r["below_date"], "mclass": mc, "status": s["status"],
                      "path": s["path"], "actor": s["actor"], "actor_is_sc": actor_ok, "kind_ok": kind_ok,
                      "hist_by_sc": ",".join(by_sc) or "-", "agree": int(agree),
                      "below_name": r["below_name"], "caseName": r["caseName"]})
    cols = list(cases[0].keys()) if cases else []
    with open(os.path.join(resdir, "%s.h0.cases.tsv" % DATASET), "w", encoding="utf-8", newline="\n") as o:
        o.write("\t".join(cols) + "\n")
        for c in sorted((c for c in cases if c["half"] == "h0"), key=lambda c: c["caseId"]):
            o.write("\t".join(str(c[k]).replace("\t", " ") for k in cols) + "\n")

    def src_group(r):
        return "state" if r["caseSource"] in STATE_SOURCES else "federal"

    variants = [("", DATASET, "mixed", "SCDB: Supreme Court reversed/vacated the decision below", None),
                (".federal", DATASET + "_federal", "federal",
                 "SCDB: Supreme Court reversed/vacated a federal decision below", "federal"),
                (".state", DATASET + "_state", "state",
                 "SCDB: Supreme Court reversed/vacated a state decision below", "state")]
    summary = []
    for suffix, ds, court, row_label, grp in variants:
        for split in ("h0",):
            def insplit(x):
                return split == "all" or x["half"] == split
            cs = [c for c in cases if insplit(c) and (grp is None or c["group"] == grp)]
            denom = [r for r in scored if insplit(r) and (grp is None or src_group(r) == grp)]
            fails = collections.Counter(r["link"] for r in denom if r["linked"] != "1")
            neg = [c for c in cs if c["class"] == "NEG"]
            part = [c for c in cs if c["class"] == "PART"]
            clean = [c for c in cs if c["class"] == "CLEAN"]
            mneg = [c for c in cs if c["mclass"] == "NEG_HIST"]
            hits = [c for c in neg if c["mclass"] == "NEG_HIST"]
            m = {
                "recall": benchlib.metric(len(hits), len(neg)),
                "precision": benchlib.metric(sum(1 for c in mneg if c["class"] == "NEG"), len(mneg)),
                "clean": benchlib.metric(sum(1 for c in clean if c["mclass"] in CLEANSET), len(clean)),
                "part": benchlib.metric(sum(1 for c in part if c["mclass"] in ("NEG_HIST", "UNK_HIST")), len(part)),
                "link_rate": benchlib.metric(sum(1 for r in denom if r["linked"] == "1"), len(denom)),
                "recall_lenient": benchlib.metric(sum(1 for c in neg if c["mclass"] in ("NEG_HIST", "UNK_HIST")),
                                                  len(neg)),
                "precision_lenient": benchlib.metric(sum(1 for c in mneg if c["class"] in ("NEG", "PART")),
                                                     len(mneg)),
            }
            kind_n = sum(1 for c in hits if c["kind_ok"] == 1)
            act_n = sum(1 for c in hits if c["actor_is_sc"] == 1)
            mc_neg = collections.Counter(c["mclass"] for c in neg)
            mc_clean = collections.Counter(c["mclass"] for c in clean)
            hidden = sum(1 for c in neg if c["mclass"] != "NEG_HIST" and
                         any(k in ("reversed", "vacated") for k in c["hist_by_sc"].split(",")))
            notes = ("Linked scored cases %d (NEG %d, PART %d, CLEAN %d). Secondary: of %d NEG_HIST hits, kind as "
                     "expected (reversed for 3/4, vacated for 5/8) %d, actor = our Supreme Court opinion %d. NEG cases "
                     "by model class %s; CLEAN cases by model class %s. NEG cases not shown NEG_HIST although an "
                     "admitted reversed/vacated history row by the SC opinion exists: %d. Link rate denominator: "
                     "scored SCDB rows%s; split by %s." % (
                         len(cs), len(neg), len(part), len(clean), len(hits), kind_n, act_n, dict(mc_neg),
                         dict(mc_clean), hidden,
                         "" if grp is None else " whose caseSource is a %s court" % grp,
                         "court of the linked decision below (metrics) / SCDB caseSource (link rate)"
                         if grp else "-"))
            res = {"dataset": ds, "label": a.label, "split": split, "row_label": row_label, "tests": "same-case",
                   "court": court, "blind": True, "primary": "recall", "metrics": m,
                   "link": {"n_items": len(denom), "linked": sum(1 for r in denom if r["linked"] == "1"),
                            "fail_reasons": dict(fails.most_common())},
                   "build": {"out": os.path.relpath(a.out, benchlib.ROOT).replace("\\", "/"),
                             "data": os.path.relpath(a.data, benchlib.ROOT).replace("\\", "/"),
                             "status_sha1": status_sha1},
                   "asof": a.asof, "generated": benchlib.now(), "notes": notes}
            benchlib.write_result(os.path.join(resdir, "%s%s.%s.json" % (DATASET, suffix, split)), res)
            summary.append((ds, split, m))
    for ds, split, m in summary:
        print("%-26s %-3s " % (ds, split) + "  ".join(
            "%s %d/%d=%.3f [%.3f,%.3f]" % (k, v["k"], v["n"], v["p"] or 0, v["lo"] or 0, v["hi"] or 0)
            for k, v in m.items() if k in ("recall", "precision", "clean", "part", "link_rate")))


if __name__ == "__main__":
    main()
