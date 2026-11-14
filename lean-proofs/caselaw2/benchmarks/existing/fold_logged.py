#!/usr/bin/env python3
"""Fold the SEALED results that already exist in logs into benchmarks/existing/*/results/ (no sealed scorer is run).

    python fold_logged.py

  shepardized_coa  round6 sealed  <- round6/history/SEALED_LOG.md (the one line; final2)
                   round4 sealed  <- round-4 aggregate over ALL cases (round6/shepardized/results/asof20101119/tables.tsv,
                                     aggregate lines only) minus the round-4 dev re-run of this folder
                                     (shepardized_coa/runs/round4_dev/headline.tsv); cross-checked line by line
                                     against the "sealed before" column of round6/history/ROUND6.md.
                                     Arithmetic, not a second sealed run.
                   sealed link rate <- round6/history/split/SPLIT.md counts table.
  gold_fresh       round4 sealed  <- round5/gold_fresh/sealed/results/baseline-round4.json
                   round5 sealed  <- round5/gold_fresh/sealed/results/final-frozen.json (round-5 frozen build)
                   (only these two result files are read; no key row, no TEST_RUNS.log)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_existing as X  # noqa: E402

B = X.B
ROOT = X.ROOT
R6H = X.R6H


def shep_sealed_round6():
    log = os.path.join(R6H, "SEALED_LOG.md")
    lines = [l for l in open(log, encoding="utf-8") if l.startswith("- ") and "--split sealed" in l]
    if len(lines) != 1:
        sys.exit("expected exactly one sealed line in SEALED_LOG.md, found %d" % len(lines))
    L = lines[0]
    lineno = [i + 1 for i, l in enumerate(open(log, encoding="utf-8")) if l == L][0]
    get = lambda name: re.search(re.escape(name) + r" (\d+)/(\d+) \((\d+)/(\d+)\)", L).groups()
    names = {"recall": "recall NEG strict", "recall_lenient": "recall NEG lenient", "recall_part": "PART",
             "precision": "precision strict", "precision_lenient": "precision lenient", "clean": "CLEAN",
             "mod_kept": "MOD", "agreement": "agreement"}
    m = {}
    for k, nm in names.items():
        a, b, c, d = map(int, get(nm))
        m[k] = B.metric(a, b)
        m[k + "_setaside"] = B.metric(c, d)
    out = re.search(r"--out (\S+)", L).group(1)
    data = re.search(r"--data (\S+)", L).group(1)
    st_sha = re.search(r"status\.tsv sha1 ([0-9a-f]{40})", L).group(1)
    return m, {"out": out, "data": data, "status_sha1": st_sha}, "round6/history/SEALED_LOG.md line %d" % lineno


def parse_tables_all(path):
    """Aggregate lines of a compare.py --split all tables.tsv -> {name: (k, n)}."""
    want = {("overall", "all"): "agreement", ("recall", "strict (NEG_HIST)"): "recall",
            ("recall", "lenient (NEG_HIST or UNK_HIST)"): "recall_lenient",
            ("recall", "PART: model NEG_HIST or UNK_HIST"): "recall_part",
            ("precision", "strict (Shepardized NEG)"): "precision",
            ("precision", "lenient (Shepardized NEG or PART)"): "precision_lenient",
            ("clean", "model CLEAN (GOOD, NEG_OTHER, UNK_OTHER)"): "clean", ("class", "MOD"): "mod_kept"}
    r, cases = {}, None
    for line in open(path, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if p[0] == "cases" and len(p) == 4:
            cases = (int(p[3]), int(p[1]))
        if len(p) >= 3 and (p[0], p[1]) in want and "/" in p[2]:
            r[want[(p[0], p[1])]] = X.kn(p[2])
        if p[0] == "recall by subclass" and len(p) >= 3:
            r["recall_sub_" + p[1]] = X.kn(p[2])
    return r, cases


def shep_sealed_round4():
    allp = os.path.join(ROOT, "round6", "shepardized", "results", "asof20101119", "tables.tsv")
    A, cases_all = parse_tables_all(allp)
    head = open(allp, encoding="utf-8").readline()
    if "caselaw-lean-2\\out" not in head and "caselaw-lean-2/out" not in head:
        sys.exit("asof20101119/tables.tsv is not the round-4 out dir: " + head)
    dev = X.shep_fold_headline(os.path.join(HERE, "shepardized_coa", "runs", "round4_dev", "headline.tsv"))
    m = {}
    for k in ("agreement", "recall", "recall_lenient", "recall_part", "precision", "precision_lenient", "clean",
              "mod_kept"):
        m[k] = B.metric(A[k][0] - dev[k]["k"], A[k][1] - dev[k]["n"])
    # NEG sub-classes: the all-cases table splits off one 'sc_vacated+enbanc_different' case; dev has none
    for sub in ("sc_reversed", "sc_vacated", "panel_withdrawn", "enbanc_different"):
        d = dev.get("recall_sub_" + sub, {"k": 0, "n": 0})
        m["recall_sub_" + sub] = B.metric(A["recall_sub_" + sub][0] - d["k"], A["recall_sub_" + sub][1] - d["n"])
    # cross-check against ROUND6.md "sealed before" column
    r6 = open(os.path.join(R6H, "ROUND6.md"), encoding="utf-8").read()
    rows = {"recall": "NEG recall (strict)", "recall_sub_sc_reversed": "Supreme Court reversed",
            "recall_sub_sc_vacated": "Supreme Court vacated",
            "recall_sub_panel_withdrawn": "panel opinion withdrawn / changed on rehearing",
            "recall_sub_enbanc_different": "different result en banc",
            "recall_part": "part-and-part (negative or partly)",
            "precision": "precision (model same-case negative, Shepardized NEG)", "clean": "clean agreement",
            "mod_kept": "modified on rehearing kept not negative"}
    checks = []
    for k, label in rows.items():
        line = [l for l in r6.splitlines() if l.startswith("| " + label + " |")][0]
        cell = [c.strip() for c in line.strip("|").split("|")][3]
        kk, nn = X.kn(re.match(r"[\d,]+/[\d,]+", cell).group(0))
        ok = (kk, nn) == (m[k]["k"], m[k]["n"])
        checks.append("%s %d/%d %s" % (k, kk, nn, "ok" if ok else "MISMATCH (arithmetic %d/%d)" % (m[k]["k"], m[k]["n"])))
        if not ok:
            sys.exit("round-4 sealed arithmetic disagrees with ROUND6.md: " + checks[-1])
    return m, checks


def sealed_link():
    t = open(os.path.join(R6H, "split", "SPLIT.md"), encoding="utf-8").read()
    a = re.search(r"\| All cases \| (\d+) \| (\d+) \|", t).groups()
    l = re.search(r"\| Linked to a corpus decision \(scored\) \| (\d+) \| (\d+) \|", t).groups()
    return int(l[1]), int(a[1])


def shep_write(label, m, build, notes):
    linked, n = sealed_link()
    m["link_rate"] = B.metric(linked, n)
    B.write_result(X.res_path("shep", label, "sealed"), {
        "dataset": "shepardized_coa", "label": label, "split": "sealed",
        "row_label": "Shepardized Courts of Appeals: decision reversed/vacated/withdrawn (same case)",
        "tests": "same-case", "court": "federal", "blind": True, "primary": "recall", "metrics": m,
        "link": {"n_items": n, "linked": linked, "fail_reasons": {},
                 "note": "sealed-half counts from round6/history/split/SPLIT.md (no per-case sealed file is read)"},
        "build": build, "asof": 20101119, "generated": B.now(), "notes": notes})


def main():
    m6, b6, src6 = shep_sealed_round6()
    shep_write("round6", m6, b6,
               "REUSED, not re-run: %s (compare.py --split sealed on final2 after FREEZE.md, run once by the round-6 "
               "lead). Wilson recomputed with benchlib.metric from the logged k/n. Metric names as in "
               "run_existing.SHEP_MAP; *_setaside = shep_errors.tsv cases left out (the bracketed figures). The log "
               "gives no sub-class split." % src6)
    m4, checks = shep_sealed_round4()
    shep_write("round4", m4, X.build_info(*X.B.BUILDS["round4"]),
               "DERIVED, not a sealed run: round-4 figure over all cases (round6/shepardized/results/asof20101119/"
               "tables.tsv, aggregate lines) minus the round-4 dev half (re-run here: shepardized_coa/runs/round4_dev/"
               "headline.tsv). This is the 'sealed before' column of round6/history/ROUND6.md ('all cases minus the dev "
               "half, arithmetic, not a second sealed run'); checked equal: %s. agreement / recall_lenient / "
               "precision_lenient are the same subtraction (not in ROUND6.md). No set-aside variant." % "; ".join(checks))
    sres = os.path.join(ROOT, "round5", "gold_fresh", "sealed", "results")
    for label, fn, build_key in (("round4", "baseline-round4.json", "round4"), ("round5", "final-frozen.json", None)):
        p = os.path.join(sres, fn)
        r = json.load(open(p, encoding="utf-8"))
        if r["split"] != "test":
            sys.exit("not a sealed result: " + p)
        if build_key:
            build = X.build_info(*X.B.BUILDS[build_key])
            if build["status_sha1"] != r["inputs"]["status_sha1"]:
                sys.exit("round-4 status.tsv changed since the sealed run")
        else:
            build = {"out": os.path.join(ROOT, "round5", "out", "final"),
                     "data": os.path.join(ROOT, "round5", "stage", "final"),
                     "status_sha1": r["inputs"]["status_sha1"]}
        X.fresh_write(label, "sealed", r, build, "REUSED, not re-run: round5/gold_fresh/sealed/results/%s, label %s, "
                      "status sha1 %s" % (fn, r["label"], r["inputs"]["status_sha1"]), blind=True,
                      extra=(" Round-5 frozen build (round5/out/final). No sealed run exists on round6 final2: the "
                             "sealed half was scored once, on round 5, and is not re-run here."
                             if label == "round5" else ""))
    print("written: shepardized_coa sealed round4/round6; gold_fresh sealed round4/round5")


if __name__ == "__main__":
    main()
