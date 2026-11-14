#!/usr/bin/env python3
"""Fold round-7 LOGGED results (no sealed scorer is run) and the extra views asked for the graph.

    python -I fold_round7.py

Every number is parsed from a file named below; nothing is hand-entered.

  shepardized_coa/results/round7.sealed.json   <- round7/SEALED_LOG.md, the compare.py line (--split sealed, v3)
  gold_fresh/results/round7.sealed.json        <- round7/SEALED_LOG.md lead's summary line (model view strict and
                                                  lenient, attributed strict) + round7/results/v3/sealed/fresh_test.txt
                                                  (precision side "listed" of N, model view)
  gold_fresh_strict/results/<label>.<split>.json  strict recall (the listed overruling case named) in two date views:
        recall_model (model timeline) and recall_attributed (dated from the overruling decision Y)
        dev:    gold_fresh/runs/views/<label>/fresh7_dev.json (round7/score_fresh7.py --split dev, run here with --out)
        sealed: round4 <- round5/gold_fresh/sealed/results/baseline-round4.json (model view only; the attributed
                view did not exist), round5 <- final-frozen.json (model view only), round7 <- SEALED_LOG.md
  scotus_timesplit_2021/results/<label>.all.json <- round7/heldout/results/{r6-final2,r7-v3}/tables.tsv
        recall: kind 'negative (reversed+vacated)', 'effect (status at d): strict';
        precision: 'target / all rows / row points to a key lower decision of O'
  scdb_conan_recognised/results/{scdb_precedent_alteration_recognised,conan_overruled_recognised}.<label>.all.json
        <- round7/results/{base,v3}/old_by_class.txt line 'selfAnnounced+operativeWords+recognised'
           (base = round6/history/stage/final2, i.e. round 6; v3 = round 7). Not blind.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
ROOT = os.path.dirname(BENCH)
R7 = os.path.join(ROOT, "round7")
sys.path.insert(0, os.path.join(BENCH, "common"))
import benchlib as B  # noqa: E402


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def base(dataset, label, split, row_label, tests, court, blind, primary, metrics, src, notes="", plot=None):
    r = {"dataset": dataset, "label": label, "split": split, "row_label": row_label, "tests": tests, "court": court,
         "blind": blind, "primary": primary, "metrics": metrics, "link": {}, "build": {"source": src},
         "generated": B.now(), "notes": notes}
    if plot:
        r["plot"] = plot
    return r


def out(sub, name, r):
    p = os.path.join(HERE, sub, "results", name)
    B.write_result(p, r)
    print("wrote", os.path.relpath(p, BENCH), {k: "%d/%d" % (v["k"], v["n"]) for k, v in r["metrics"].items()})


SEALED_LOG = os.path.join(R7, "SEALED_LOG.md")
log = rd(SEALED_LOG)

# 1. Shepardized sealed, round 7
line = [l for l in log.splitlines() if "--split sealed" in l and "round7/out/v3" in l][-1]
rec = re.search(r"recall NEG strict (\d+)/(\d+)", line)
pre = re.search(r"precision strict (\d+)/(\d+)", line)
cln = re.search(r"CLEAN (\d+)/(\d+)", line)
tmpl = json.load(open(os.path.join(HERE, "shepardized_coa", "results", "round6.sealed.json"), encoding="utf-8"))
r = dict(tmpl)
r.update(label="round7", generated=B.now(), blind=True,
         metrics={"recall": B.metric(int(rec[1]), int(rec[2])), "precision": B.metric(int(pre[1]), int(pre[2])),
                  "clean": B.metric(int(cln[1]), int(cln[2]))},
         build={"source": "round7/SEALED_LOG.md (compare.py --split sealed on round7/out/v3, logged by the round-7 lead)"},
         notes="Reused from the round-7 lead's single logged sealed run; not re-run here.")
out("shepardized_coa", "round7.sealed.json", r)

# 2. Fresh lists sealed, round 7
m = re.search(r"model view strict (\d+) = .*?\], lenient (\d+)", log.replace("\n", " "))
att = re.search(r"attributed view strict (\d+)", log.replace("\n", " "))
npairs = int(re.search(r"(\d+) pairs;", log)[1])
ft = rd(os.path.join(R7, "results", "v3", "sealed", "fresh_test.txt"))
ps = re.search(r"precision side \(model view[^{]*(\{[^}]*\}) of (\d+)", ft)
listed = json.loads(ps[1])["listed"]
tmpl = json.load(open(os.path.join(HERE, "gold_fresh", "results", "round5.sealed.json"), encoding="utf-8"))
r = dict(tmpl)
r.update(label="round7", generated=B.now(), blind=True,
         metrics={"recall": B.metric(int(m[2]), npairs), "recall_strict": B.metric(int(m[1]), npairs),
                  "recall_strict_attributed": B.metric(int(att[1]), npairs),
                  "precision": B.metric(listed, int(ps[2]))},
         build={"source": "round7/SEALED_LOG.md + round7/results/v3/sealed/fresh_test.txt (score_fresh7 --split test)"},
         notes="Reused from the round-7 lead's single logged sealed run; not re-run here. Third use of this half.")
out("gold_fresh", "round7.sealed.json", r)

# 3. Strict fresh-list recall in two date views
FS_LABEL = "Fresh overruling lists, strict: the listed overruling case named"
for lab in ("round4", "round6", "round7"):
    j = json.load(open(os.path.join(HERE, "gold_fresh", "runs", "views", lab, "fresh7_dev.json"), encoding="utf-8"))
    mv = j["views"]["model"]["recall"]["all"]["all"]["strict"]
    av = j["views"]["attributed"]["recall"]["all"]["all"]["strict"]
    blind = lab == "round4"
    out("gold_fresh_strict", "%s.dev.json" % lab, base(
        "gold_fresh_strict", lab, "dev", FS_LABEL, "overruling", "supreme", blind, "recall_model",
        {"recall_model": B.metric(mv["k"], mv["n"]), "recall_attributed": B.metric(av["k"], av["n"])},
        "benchmarks/existing/gold_fresh/runs/views/%s/fresh7_dev.json" % lab,
        "round7/score_fresh7.py --split dev, both views. Rounds 5-7 were developed with the dev half in view.",
        plot=["recall_model", "recall_attributed"]))
for lab, fn in (("round4", "baseline-round4.json"), ("round5", "final-frozen.json")):
    j = json.load(open(os.path.join(HERE, "gold_fresh", "results", "%s.sealed.json" % lab), encoding="utf-8"))
    s = j["metrics"]["recall_strict"]
    out("gold_fresh_strict", "%s.sealed.json" % lab, base(
        "gold_fresh_strict", lab, "sealed", FS_LABEL, "overruling", "supreme", True, "recall_model",
        {"recall_model": B.metric(s["k"], s["n"])}, "round5/gold_fresh/sealed/results/" + fn,
        "Model view only (the attributed view did not exist for this logged run).",
        plot=["recall_model", "recall_attributed"]))
out("gold_fresh_strict", "round7.sealed.json", base(
    "gold_fresh_strict", "round7", "sealed", FS_LABEL, "overruling", "supreme", True, "recall_model",
    {"recall_model": B.metric(int(m[1]), npairs), "recall_attributed": B.metric(int(att[1]), npairs)},
    "round7/SEALED_LOG.md", "Reused from the round-7 lead's single logged sealed run.",
    plot=["recall_model", "recall_attributed"]))

# 4. Time split of Supreme Court judgments 2021 on
TS_LABEL = "Supreme Court judgments 2021 on (docket record): decision below reversed or vacated"
for lab, d in (("round6", "r6-final2"), ("round7", "r7-v3")):
    t = rd(os.path.join(R7, "heldout", "results", d, "tables.tsv"))
    rr = re.search(r"negative \(reversed\+vacated\)\teffect \(status at d\): strict\t(\d+)/(\d+)", t)
    pp = re.search(r"target\tall rows\trow points to a key lower decision of O\t(\d+)/(\d+)", t)
    out("scotus_timesplit_2021", "%s.all.json" % lab, base(
        "scotus_timesplit_2021", lab, "all", TS_LABEL, "same-case", "mixed", True, "recall",
        {"recall": B.metric(int(rr[1]), int(rr[2])), "precision": B.metric(int(pp[1]), int(pp[2]))},
        "round7/heldout/results/%s/tables.tsv" % d,
        "Round-7 time-split key (round7/heldout/HELDOUT.md), each build scored once by the round-7 lead "
        "(RUNS.log); precision = admitted rows by a key order that point to that order's lower decision. "
        "Round 4 not scored on this key."))

# 5. Old lists counting recognised overrulings (not blind)
for lab, d in (("round6", "base"), ("round7", "v3")):
    t = rd(os.path.join(R7, "results", d, "old_by_class.txt"))
    ln = [l for l in t.splitlines() if l.startswith("selfAnnounced+operativeWords+recognised")][0]
    s = re.search(r"SCDB (\d+)/(\d+) \(precision (\d+)/(\d+)\)", ln)
    c = re.search(r"CRS current (\d+)/(\d+)", ln)
    src = "round7/results/%s/old_by_class.txt ('selfAnnounced+operativeWords+recognised')" % d
    out("scdb_conan_recognised", "scdb_precedent_alteration_recognised.%s.all.json" % lab, base(
        "scdb_precedent_alteration_recognised", lab, "all",
        "SCDB precedentAlteration, counting overrulings recognised by a later court", "overruling", "supreme", False,
        "recall", {"recall": B.metric(int(s[1]), int(s[2])), "precision": B.metric(int(s[3]), int(s[4]))}, src,
        "Burned key (not blind). The explicit-only row is scdb_precedent_alteration."))
    out("scdb_conan_recognised", "conan_overruled_recognised.%s.all.json" % lab, base(
        "conan_overruled_recognised", lab, "all",
        "Constitution Annotated list, counting overrulings recognised by a later court", "overruling", "supreme",
        False, "recall", {"recall": B.metric(int(c[1]), int(c[2]))}, src,
        "Burned key (not blind). Precision for this view is not in the source file."))
