#!/usr/bin/env python3
"""Re-run every NON-sealed scorer of the already-built benchmarks on one build and fold the outputs into
benchmarks/existing/<bench>/results/<label>.<split>.json (benchmarks/CONTRACT.md, benchlib.write_result).

    python run_existing.py --label round6 --out <out dir> --data <data/stage dir> [--only shep,fresh,holdout,behaviour,scdb]
                           [--fold-only]

Scorers (never modified in place; outputs go to benchmarks/existing/<bench>/runs/<label>/):
  shep       round6/shepardized/compare.py --split dev --results ...                  (original, flag redirect)
  fresh      gold_fresh/scorer/score_fresh_copy.py --split dev --results-dir ...      (copy: output path only; refuses test)
  holdout    _r5tests/score_holdout.py ... --pool round5/tests/results/testable_pool_baseline-round4.tsv --out ...
  behaviour  _r5tests/behaviour.py ... --classes round5/classes_r5.tsv --out ...
             (_r5tests/ = copies of round5/tests/{common,score_holdout,behaviour}.py; only common.py's cache path
             differs, so the numpy caches are written to _r5tests/cache instead of round5/tests/cache)
  scdb       <lean-proofs>/tools/caselaw2/eval/score.py --out --data --results ...    (original, flag redirect)

Sealed halves are never run here (see fold_logged.py). Standard library + numpy (behaviour/holdout only).
"""
import argparse
import collections
import csv
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
ROOT = os.path.dirname(BENCH)
sys.path.insert(0, os.path.join(BENCH, "common"))
import benchlib as B  # noqa: E402

SHEP = os.path.join(ROOT, "round6", "shepardized")
R6H = os.path.join(ROOT, "round6", "history")
FRESH = os.path.join(ROOT, "round5", "gold_fresh")
R5T = os.path.join(ROOT, "round5", "tests")
EVAL = os.environ.get("CASELAW2_EVAL") or os.path.expanduser("~/gl-pub/lean-proofs/tools/caselaw2/eval")
PY = sys.executable

ALL = ("shep", "fresh", "holdout", "behaviour", "scdb")
FOLDER = {"shep": "shepardized_coa", "fresh": "gold_fresh", "holdout": "holdout_notes", "behaviour": "behaviour",
          "scdb": "scdb_conan"}


def sha(p):
    return B.file_sha1(p) if os.path.isfile(p) else "absent"


def build_info(out, data):
    return {"out": os.path.abspath(out), "data": os.path.abspath(data),
            "status_sha1": sha(os.path.join(out, "status.tsv"))}


def run(cmd, log, env=None):
    os.makedirs(os.path.dirname(log), exist_ok=True)
    t0 = time.time()
    with open(log, "w", encoding="utf-8", newline="\n") as f:
        f.write("# " + " ".join('"%s"' % c if " " in c else c for c in cmd) + "\n")
        f.flush()
        e = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", **(env or {}))
        rc = subprocess.call(cmd, stdout=f, stderr=subprocess.STDOUT, env=e)
    print("  %s -> exit %d in %.0fs (log %s)" % (os.path.basename(cmd[1 if cmd[1] != "-I" else 2]), rc,
                                                 time.time() - t0, log), flush=True)
    if rc != 0:
        sys.exit("scorer failed: see " + log)


def write_inputs(path, files):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    d = {k: {"path": os.path.abspath(v), "sha1": sha(v)} for k, v in files.items()}
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, indent=1, sort_keys=True)
        f.write("\n")
    return d


def res_path(bench, label, split, dataset=None):
    name = "%s.%s.json" % (label, split) if dataset is None else "%s.%s.%s.json" % (dataset, label, split)
    return os.path.join(HERE, FOLDER[bench], "results", name)


def M(k, n):
    return B.metric(int(k), int(n))


def kn(s):
    k, n = s.replace(",", "").split("/")
    return int(k), int(n)


# ------------------------------------------------------------------------------------------------ Shepardized
SHEP_MAP = {  # headline.tsv (group, value) -> metric name
    ("agreement", "overall, scored classes (NEG, PART, MOD, CLEAN)"): "agreement",
    ("(a) recall", "NEG: model NEG_HIST (strict)"): "recall",
    ("(a) recall", "NEG: model NEG_HIST or UNK_HIST (lenient)"): "recall_lenient",
    ("(a) recall", "PART: model NEG_HIST or UNK_HIST"): "recall_part",
    ("(a) recall", "NEG and PART together: model as expected"): "recall_neg_and_part",
    ("(b) precision", "of model NEG_HIST: Shepardized NEG (strict; AMBIG left out)"): "precision",
    ("(b) precision", "of model NEG_HIST: Shepardized NEG or PART (lenient; AMBIG left out)"): "precision_lenient",
    ("(c) clean", "CLEAN: model shows no same-case negative"): "clean",
    ("(c) clean", "MOD: model CLEAN or UNK_HIST"): "mod_kept",
}


def shep_fold_headline(path):
    """headline.tsv -> metrics (raw) + metrics with documented database errors set aside (suffix _setaside)."""
    m = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 7 and (p[0], p[1]) in SHEP_MAP:
                name = SHEP_MAP[(p[0], p[1])]
                m[name] = M(*kn(p[2]))
                m[name + "_setaside"] = M(*kn(p[6]))
            elif len(p) >= 7 and p[0] == "recall by subclass" and p[1].startswith("NEG/"):
                m["recall_sub_" + p[1][4:]] = M(*kn(p[2]))
    return m


def do_shep(label, out, data, run_it):
    rd = os.path.join(HERE, FOLDER["shep"], "runs", label + "_dev")
    if run_it:
        write_inputs(os.path.join(rd, "inputs.json"), {
            "scorer compare.py": os.path.join(SHEP, "compare.py"), "out/status.tsv": os.path.join(out, "status.tsv"),
            "out/certs.tsv": os.path.join(out, "certs.tsv"), "data/history.tsv": os.path.join(data, "history.tsv"),
            "key work/shepardized.tsv": os.path.join(SHEP, "work", "shepardized.tsv"),
            "key results/links.tsv": os.path.join(SHEP, "results", "links.tsv"),
            "split dev.tsv": os.path.join(R6H, "split", "dev.tsv"),
            "shep_errors.tsv": os.path.join(R6H, "shep_errors.tsv")})
        run([PY, "-I", os.path.join(SHEP, "compare.py"), "--split", "dev", "--out", out, "--data", data,
             "--results", rd], os.path.join(rd, "compare.log"))
    m = shep_fold_headline(os.path.join(rd, "headline.tsv"))
    n_cases = n_linked = None
    with open(os.path.join(rd, "tables.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[0] == "cases" and len(p) == 4:
                n_cases, n_linked = int(p[1]), int(p[3])
                break
    fails = collections.Counter()
    with open(os.path.join(rd, "cases_dev.tsv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if not r["node"]:
                fails[r["link"]] += 1
    m["link_rate"] = M(n_linked, n_cases)
    blind = label == "round4"
    B.write_result(res_path("shep", label, "dev"), {
        "dataset": "shepardized_coa", "label": label, "split": "dev",
        "row_label": "Shepardized Courts of Appeals: decision reversed/vacated/withdrawn (same case)",
        "tests": "same-case", "court": "federal", "blind": blind, "primary": "recall", "metrics": m,
        "link": {"n_items": n_cases, "linked": n_linked, "fail_reasons": dict(fails)},
        "build": build_info(out, data), "asof": 20101119, "generated": B.now(),
        "notes": ("Re-run: round6/shepardized/compare.py --split dev (MAPPING.md classes), headline.tsv in "
                  "existing/shepardized_coa/runs/%s_dev/. recall = NEG strict (model NEG_HIST); precision = strict "
                  "(of model NEG_HIST, Shepardized NEG; AMBIG left out); clean = CLEAN cases shown clean; *_setaside = "
                  "documented database errors (round6/history/shep_errors.tsv) left out. As-of 2010-11-19. %s"
                  % (label, "Blind: round 4 was built before this key was linked." if blind else
                     "NOT blind: the dev half was open to the round-6 builders (dev_misses / dev_fp read case by "
                     "case; DESIGN6.md 1); the sealed half is the blind figure."))})
    return m


# ------------------------------------------------------------------------------------------------ fresh lists
def do_fresh(label, out, data, run_it):
    rd = os.path.join(HERE, FOLDER["fresh"], "runs", label)
    copy = os.path.join(HERE, FOLDER["fresh"], "scorer", "score_fresh_copy.py")
    if run_it:
        write_inputs(os.path.join(rd, "inputs.json"), {
            "scorer score_fresh_copy.py": copy, "original score_fresh.py": os.path.join(FRESH, "score_fresh.py"),
            "out/status.tsv": os.path.join(out, "status.tsv"), "out/findings.tsv": os.path.join(out, "findings.tsv"),
            "data/treatments.tsv": os.path.join(data, "treatments.tsv"),
            "key dev/dev.tsv": os.path.join(FRESH, "dev", "dev.tsv"),
            "work/scotus_meta.tsv": os.path.join(FRESH, "work", "scotus_meta.tsv")})
        run([PY, "-I", copy, "--split", "dev", "--status", os.path.join(out, "status.tsv"), "--treatments",
             os.path.join(data, "treatments.tsv"), "--label", label, "--results-dir", rd],
            os.path.join(rd, "score_fresh.log"))
    with open(os.path.join(rd, label + ".json"), encoding="utf-8") as f:
        r = json.load(f)
    fresh_write(label, "dev", r, build_info(out, data), "existing/gold_fresh/runs/%s/%s.json" % (label, label),
                blind=(label == "round4"))


def fresh_metrics(r):
    a = r["recall"]["all"]["all"]
    m = {"recall": M(a["lenient"]["k"], a["n"]), "recall_strict": M(a["strict"]["k"], a["n"])}
    for dim, key, name in (("express", "express", "express"), ("express", "implied", "implied"),
                           ("burned_crs", "notInCRS", "notInCRS"), ("burned_crs", "inCRS", "inCRS"),
                           ("scope", "partial", "partial"), ("scope", "full", "full")):
        v = r["recall"].get(dim, {}).get(key)
        if v:
            m["recall_" + name] = M(v["lenient"]["k"], v["n"])
            m["recall_strict_" + name] = M(v["strict"]["k"], v["n"])
    p = r["precision_side"]
    m["precision"] = M(p["listed_share"]["k"], p["listed_share"]["n"])
    return m


def fresh_write(label, split, r, build, src, blind, extra=""):
    m = fresh_metrics(r)
    n = r["gold_pairs"]
    m["link_rate"] = M(n, n)
    B.write_result(res_path("fresh", label, split), {
        "dataset": "gold_fresh", "label": label, "split": split,
        "row_label": "Fresh overruling lists (Wikipedia, Blaustein-Field, Gerhardt, Payne n.1): Supreme Court",
        "tests": "overruling", "court": "supreme", "blind": blind, "primary": "recall", "metrics": m,
        "link": {"n_items": n, "linked": n, "fail_reasons": {},
                 "note": "key pairs are resolved by construction (GOLD_FRESH.md: 449 of 451 source rows scoreable; "
                         "the 2 unresolved rows are outside both halves)"},
        "build": build, "asof": None, "generated": B.now(),
        "notes": ("Scorer round5/gold_fresh/score_fresh.py (%s). recall = lenient (overruled X is neg:* or unknown:* "
                  "in status.tsv: outcomes a, a_date, a_kind, b, c); recall_strict = outcome a (neg:overruled/"
                  "abrogated by the listed Y from Y's date). precision = of the model's Supreme-Court-on-Supreme-Court "
                  "overrulings in this half, the share on a fresh list ('unlisted' is not 'wrong': the lists are "
                  "incomplete, so this is a lower bound). 91%% of key pairs are also in a CRS edition (GOLD_FRESH.md); "
                  "recall_notInCRS is the truly new part. %s%s" % (
                      src, "Blind." if blind else "NOT blind on dev: the dev half was open to the round-5 builders "
                      "(scored at every iteration, ROUND5.md); the sealed half is the blind figure. ", extra))})


# ------------------------------------------------------------------------------------------------ holdout notes
CATS = ("negByY", "partlyByY", "negByOther", "partlyByOther", "atRiskOnly", "laterOnly", "nothing")


def hcounts(c):
    n = sum(c.get(x, 0) for x in CATS)
    return {"n": n, "negByY": c.get("negByY", 0),
            "byAnyone": c.get("negByY", 0) + c.get("negByOther", 0),
            "negOrPartly": sum(c.get(x, 0) for x in CATS[:4]),
            "anySignal": sum(c.get(x, 0) for x in CATS[:5])}


def do_holdout(label, out, data, run_it):
    rd = os.path.join(HERE, FOLDER["holdout"], "runs", label)
    sc = os.path.join(HERE, "_r5tests", "score_holdout.py")
    pool = os.path.join(R5T, "results", "testable_pool_baseline-round4.tsv")
    if run_it:
        write_inputs(os.path.join(rd, "inputs.json"), {
            "scorer copy _r5tests/score_holdout.py": sc, "original score_holdout.py": os.path.join(R5T, "score_holdout.py"),
            "copy _r5tests/common.py": os.path.join(HERE, "_r5tests", "common.py"),
            "original common.py": os.path.join(R5T, "common.py"),
            "out/status.tsv": os.path.join(out, "status.tsv"), "out/findings.tsv": os.path.join(out, "findings.tsv"),
            "out/certs.tsv": os.path.join(out, "certs.tsv"), "data/treatments.tsv": os.path.join(data, "treatments.tsv"),
            "data/decisions2.tsv": os.path.join(data, "decisions2.tsv"),
            "split/holdout_ids.tsv": os.path.join(R5T, "split", "holdout_ids.tsv"),
            "split/manifest.json": os.path.join(R5T, "split", "manifest.json"), "frozen pool": pool})
        run([PY, os.path.join(HERE, "_r5tests", "check_no_leak.py"), os.path.join(data, "treatments.tsv"),
             os.path.join(data, "treatment_witness.tsv"), "--certs", os.path.join(out, "certs.tsv"), "--data", data],
            os.path.join(rd, "check_no_leak.log"))
        run([PY, sc, "--status", os.path.join(out, "status.tsv"), "--label", label, "--data", data, "--pool", pool,
             "--out", rd], os.path.join(rd, "score_holdout.log"))
    with open(os.path.join(rd, "holdout_%s.json" % label), encoding="utf-8") as f:
        r = json.load(f)
    holdout_write(label, r, build_info(out, data), "existing/holdout_notes/runs/%s/holdout_%s.json" % (label, label))


def holdout_write(label, r, build, src):
    T = r["tables"]
    rev = r["reverse"]
    for fam, ds, tests, rl in (
            ("precedent", "holdout_notes", "overruling",
             "Later-court notes 'X, overruled/abrogated by Y' from courts with no power over X (held out)"),
            ("history", "holdout_notes_history", "same-case",
             "Later-court notes 'X, rev'd/vacated by Y' from courts with no power over X (held out)")):
        c = hcounts(T["pair|all|named"][fam])
        m = {"recall": M(c["negOrPartly"], c["n"]), "recall_strict": M(c["negByY"], c["n"]),
             "recall_byAnyone": M(c["byAnyone"], c["n"]), "any_signal": M(c["anySignal"], c["n"])}
        if fam == "precedent":
            for key in ("all", "alsoInFeed", "holdoutOnly"):
                v = T.get("pool|frozenPool|named", {}).get(key)
                if v:
                    pc = hcounts(v)
                    m["pool_%s_recall" % key] = M(pc["negOrPartly"], pc["n"])
                    m["pool_%s_recall_strict" % key] = M(pc["negByY"], pc["n"])
            ex = T["pair|explicitAdmitted|named"]
            for key in ("precedent:notExplicit", "precedent:explicit"):
                pc = hcounts(ex[key])
                m["recall_" + key.split(":")[1]] = M(pc["negOrPartly"], pc["n"])
        rv = rev.get(fam, {})
        if rv.get("same", 0) + rv.get("other", 0):
            m["precision"] = M(rv["same"], rv["same"] + rv["other"])
        B.write_result(res_path("holdout", label, "all", None if ds == "holdout_notes" else ds), {
            "dataset": ds, "label": label, "split": "all", "row_label": rl, "tests": tests, "court": "mixed",
            "blind": True, "primary": "recall", "metrics": m,
            "link": {"n_items": c["n"], "linked": c["n"], "fail_reasons": {},
                     "note": "items are (X, Y) pairs of the frozen split (round5/tests/split); targets and Y are "
                             "corpus nodes by construction (regex 'nearest citation', not audited)"},
            "build": build, "asof": None, "generated": B.now(),
            "notes": ("Scorer round5/tests/score_holdout.py (%s). Pair level, Y named, %s family; each (X, Y) read "
                      "on the date of its first holdout statement. recall = negOrPartly (X negative or partly "
                      "negative by any actor on that date); recall_strict = whole-decision negative by Y; "
                      "precision = reverse direction (of the model's whole-decision negative (X, actor) rows whose X "
                      "a holdout note of this family names with a Y, the share where the note names the model's "
                      "actor). %sBlind in input: holdout speakers never feed the model (check_no_leak.py); round-5 "
                      "builders did see these aggregate scores at each iteration (TESTS.md, results/holdout_it*)."
                      % (src, fam, "pool_* = the frozen testable pool (9,374 pairs not explicitly admitted by "
                         "round 4; alsoInFeed / holdoutOnly halves); 71%% of the pool is 'overruled on other "
                         "grounds' notes where partly is the right answer. " if fam == "precedent" else ""))})


# ------------------------------------------------------------------------------------------------ behaviour
def do_behaviour(label, out, data, run_it):
    rd = os.path.join(HERE, FOLDER["behaviour"], "runs", label)
    sc = os.path.join(HERE, "_r5tests", "behaviour.py")
    classes = os.path.join(ROOT, "round5", "classes_r5.tsv")
    if run_it:
        write_inputs(os.path.join(rd, "inputs.json"), {
            "scorer copy _r5tests/behaviour.py": sc, "original behaviour.py": os.path.join(R5T, "behaviour.py"),
            "copy _r5tests/common.py": os.path.join(HERE, "_r5tests", "common.py"),
            "classes_r5.tsv": classes, "out/status.tsv": os.path.join(out, "status.tsv"),
            "out/findings.tsv": os.path.join(out, "findings.tsv"),
            "data/decisions2.tsv": os.path.join(data, "decisions2.tsv"),
            "graph/edges.bin": os.path.join(os.path.dirname(ROOT), "graph", "edges.bin"),
            "gold/reports_typed.tsv": os.path.join(ROOT, "gold", "reports_typed.tsv")})
        run([PY, sc, "--status", os.path.join(out, "status.tsv"), "--label", label, "--data", data, "--classes",
             classes, "--out", rd], os.path.join(rd, "behaviour.log"))
    behaviour_write(label, os.path.join(rd, "behaviour_%s.tsv" % label), build_info(out, data),
                    "existing/behaviour/runs/%s/behaviour_%s.tsv" % (label, label))


def fnum(x):
    return float(x) if x not in ("", None) else None


def behaviour_write(label, tsv, build, src):
    m = {}
    with open(tsv, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r["series"] not in ("bound", "boundClean") or r["k"] not in ("5", "10"):
                continue
            cls = r["class"].replace("placebo:", "placebo_")
            key = "did_%s_k%s%s" % (cls, r["k"], "" if r["series"] == "bound" else "_clean")
            m[key] = {"value": fnum(r["did"]), "lo": fnum(r["did_lo"]), "hi": fnum(r["did_hi"]), "n": int(r["n"]),
                      "kind": "did_ratio",
                      "index_did": fnum(r["index_did"]), "index_lo": fnum(r["index_lo"]),
                      "index_hi": fnum(r["index_hi"]),
                      "share_of_explicit": fnum(r["share_of_explicit"]), "share_lo": fnum(r["share_lo"]),
                      "share_hi": fnum(r["share_hi"])}
    B.write_result(res_path("behaviour", label, "all"), {
        "dataset": "behaviour", "label": label, "split": "all",
        "row_label": "Behavioural test: bound citations after the model's overruling date (DiD vs matched controls)",
        "tests": "overruling", "court": "mixed", "blind": True, "primary": "did_explicit_k10", "metrics": m,
        "link": {"n_items": m.get("did_explicit_k10", {}).get("n"), "linked": m.get("did_explicit_k10", {}).get("n"),
                 "fail_reasons": {}, "note": "items = event decisions used (see the samples table of the run)"},
        "build": build, "asof": None, "generated": B.now(),
        "notes": ("Scorer round5/tests/behaviour.py with --classes round5/classes_r5.tsv (%s). No labels: metrics are "
                  "NOT k/n proportions. Each did_<class>_k<years> = {value: DiD = (post/pre of event decisions) / "
                  "(post/pre of matched controls), lo/hi: bootstrap 95%% over event decisions (1,000 draws, seed 5), "
                  "n: event decisions used}; 1 = no drop. Series bound (citing court bound by the decision), *_clean = "
                  "boundClean (citations that report the treatment removed; not label-free). Headline: "
                  "did_explicit_k10 (self-announced whole-decision overrulings: the calibration class); compare each "
                  "class with its placebo_* (should sit at 1) and share_of_explicit. Classes absent from a build "
                  "(e.g. recognised on round 4) are absent here." % src)})


# ------------------------------------------------------------------------------------------------ SCDB / CONAN
def do_scdb(label, out, data, run_it):
    rd = os.path.join(HERE, FOLDER["scdb"], "runs", label)
    sc = os.path.join(EVAL, "score.py")
    gold = os.path.join(ROOT, "gold")
    if run_it:
        write_inputs(os.path.join(rd, "inputs.json"), {
            "scorer eval/score.py": sc, "out/status.tsv": os.path.join(out, "status.tsv"),
            "out/certs.tsv": os.path.join(out, "certs.tsv"), "out/findings.tsv": os.path.join(out, "findings.tsv"),
            "data/treatments.tsv": os.path.join(data, "treatments.tsv"),
            "data/history.tsv": os.path.join(data, "history.tsv"),
            "data/decisions2.tsv": os.path.join(data, "decisions2.tsv"),
            "gold/scdb.tsv": os.path.join(gold, "scdb.tsv"), "gold/crs_overruled.tsv": os.path.join(gold, "crs_overruled.tsv")})
        run([PY, sc, "--out", out, "--data", data, "--results", rd], os.path.join(rd, "score.log"))
    with open(os.path.join(rd, "results.json"), encoding="utf-8") as f:
        r = json.load(f)
    # key-side link counts (read from the key files the scorer reads)
    n_flag = n_flag_linked = 0
    with open(os.path.join(gold, "scdb.tsv"), encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if row["precedentAlteration"] == "1":
                n_flag += 1
                try:
                    n_flag_linked += int(row["node"]) >= 0
                except ValueError:
                    pass
    scdb_write(label, r, build_info(out, data), "existing/scdb_conan/runs/%s/results.json" % label, n_flag,
               n_flag_linked)


def scdb_write(label, r, build, src, n_flag, n_flag_linked):
    s = r["scdb"]
    common = ("Scorer tools/caselaw2/eval/score.py (%s); it counts admitted explicit treatment rows (certificate ok, "
              "explicit = 1, kinds overruled/disapproved/recededFrom/abrogated/supersededByEnactment); the implicit "
              "tier and round-5 'recognised' status rows are not counted (ROUND5.md reports 175/278 SCDB and 195/292 "
              "CRS with recognised rows, from another scorer). NOT blind: these keys were used to evaluate and tune "
              "rounds 1-4 (eval/score_round*.txt). " % src)
    B.write_result(res_path("scdb", label, "all", "scdb_precedent_alteration"), {
        "dataset": "scdb_precedent_alteration", "label": label, "split": "all",
        "row_label": "SCDB precedentAlteration = 1: Supreme Court decision overrules a Supreme Court precedent",
        "tests": "overruling", "court": "supreme", "blind": False, "primary": "recall",
        "metrics": {"recall": M(s["flagged_with_admitted_overruling"], s["flagged_decisions"]),
                    "precision": M(s["of_which_flagged"], s["scotus_decisions_with_admitted_overruling_of_scotus"]),
                    "link_rate": M(n_flag_linked, n_flag)},
        "link": {"n_items": n_flag, "linked": n_flag_linked, "fail_reasons": {"no corpus node": n_flag - n_flag_linked}},
        "build": build, "asof": None, "generated": B.now(),
        "notes": common + "Unit: the overruling decision. recall = of SCDB-flagged decisions, the model admits an "
                          "overruling by it of a Supreme Court decision; precision = of Supreme Court decisions the "
                          "model has overruling a Supreme Court decision, SCDB flags it."})
    c = r["crs"]
    ct = c["current_table"]
    m = {"recall": M(ct["found"], ct["resolved"]), "link_rate": M(ct["resolved"], ct["pairs"])}
    for k in ("2016_express", "2016_all"):
        m["recall_" + k] = M(c[k]["found"], c[k]["resolved"])
    m["precision"] = M(c["of_which_in_crs"], c["admitted_scotus_on_scotus"])
    B.write_result(res_path("scdb", label, "all", "conan_overruled"), {
        "dataset": "conan_overruled", "label": label, "split": "all",
        "row_label": "Constitution Annotated (CRS) table of overruled Supreme Court decisions",
        "tests": "overruling", "court": "supreme", "blind": False, "primary": "recall", "metrics": m,
        "link": {"n_items": ct["pairs"], "linked": ct["resolved"],
                 "fail_reasons": {"unresolved": ct["pairs"] - ct["resolved"]}},
        "build": build, "asof": None, "generated": B.now(),
        "notes": common + "Unit: (overruling, overruled) pair. recall = current table (2022 + 2026 supp.) pairs "
                          "the model admits; recall_2016_express / recall_2016_all = the 2016 edition; precision = "
                          "of the model's admitted Supreme-Court-on-Supreme-Court pairs, the share in any CRS "
                          "edition (an incomplete list: a lower bound)."})


DO = {"shep": do_shep, "fresh": do_fresh, "holdout": do_holdout, "behaviour": do_behaviour, "scdb": do_scdb}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--only", default=",".join(ALL))
    ap.add_argument("--fold-only", action="store_true", help="do not run scorers; re-fold existing run outputs")
    a = ap.parse_args()
    out, data = os.path.abspath(a.out), os.path.abspath(a.data)
    for p in (os.path.join(out, "status.tsv"), os.path.join(data, "history.tsv")):
        if not os.path.isfile(p):
            sys.exit("missing " + p)
    for b in a.only.split(","):
        print("== %s (%s)" % (b, a.label), flush=True)
        DO[b](a.label, out, data, not a.fold_only)


if __name__ == "__main__":
    main()
