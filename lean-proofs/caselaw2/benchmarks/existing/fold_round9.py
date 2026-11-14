#!/usr/bin/env python3
"""Fold round-9 LOGGED results (no sealed scorer is run) into benchmarks/existing/*/results/.

    python -I fold_round9.py

Every number is parsed from a file; nothing is hand-entered.

  shepardized_coa/results/round9.sealed.json  <- round9/SEALED_LOG.md compare.py line (v9c); 4th use
  gold_fresh/results/round9.sealed.json       <- round9/SEALED_LOG.md fresh line (strict model / attributed / lenient
                                                 model) + round9/results/v9c/sealed/fresh_test.txt (precision side); 5th use
  gold_fresh_strict/results/round9.{dev,sealed}.json <- gold_fresh/runs/views/round9/fresh7_dev.json + the log line
  scdb_conan_recognised/results/*.round9.all.json   <- round9/results/v9c/old_by_class.txt
  holdout_notes/results/round9.all.json             <- round9/results/v9c/summary.txt 'HOLDOUT NOTES' lines
        (recall = negOrPartly, precision = 'precedent k/n' — the same figures this folder's scorer writes; checked
        equal on round 8: 4642/12354 and 797/853)
  holdout_notes/results/holdout_notes_history.round9.all.json <- summary.txt 'HOLDOUT NOTES: history' (precision
        only; the recall needs the scorer's decisions cache, ~100 MB, not built for v9c because disk is tight)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
ROOT = os.path.dirname(BENCH)
R9 = os.path.join(ROOT, "round9")
V = os.path.join(R9, "results", "v9c")
sys.path.insert(0, os.path.join(BENCH, "common"))
import benchlib as B  # noqa: E402


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def load(sub, name):
    return json.load(open(os.path.join(HERE, sub, "results", name), encoding="utf-8"))


def out(sub, name, r):
    p = os.path.join(HERE, sub, "results", name)
    B.write_result(p, r)
    print("wrote", os.path.relpath(p, BENCH), {k: "%d/%d" % (v["k"], v["n"]) for k, v in r["metrics"].items()})


log = rd(os.path.join(R9, "SEALED_LOG.md"))

# Shepardized sealed, 4th use
line = [l for l in log.splitlines() if "--split sealed" in l and "round9/out/v9c" in l][-1]
rec = re.search(r"recall NEG strict (\d+)/(\d+)", line)
pre = re.search(r"precision strict (\d+)/(\d+)", line)
cln = re.search(r"CLEAN (\d+)/(\d+)", line)
r = load("shepardized_coa", "round8.sealed.json")
r.update(label="round9", generated=B.now(), use_note="sealed half, 4th use",
         row_label="Shepardized Courts of Appeals: decision reversed/vacated/withdrawn (sealed half, used 4 times)",
         metrics={"recall": B.metric(int(rec[1]), int(rec[2])), "precision": B.metric(int(pre[1]), int(pre[2])),
                  "clean": B.metric(int(cln[1]), int(cln[2]))},
         build={"source": "round9/SEALED_LOG.md (compare.py --split sealed on round9/out/v9c)"},
         notes="Reused from the round-9 lead's single logged run. Fourth use of this half.")
out("shepardized_coa", "round9.sealed.json", r)

# Fresh lists sealed, 5th use
fl = [l for l in log.splitlines() if "fresh sealed, 5th use" in l][-1]
sm = re.search(r"strict model (\d+)/(\d+).*?strict attributed (\d+)/(\d+).*?lenient model (\d+)/(\d+)", fl)
ps = re.search(r"precision side \(model view[^{]*(\{[^}]*\}) of (\d+)", rd(os.path.join(V, "sealed", "fresh_test.txt")))
r = load("gold_fresh", "round8.sealed.json")
r.update(label="round9", generated=B.now(), use_note="sealed half, 5th use",
         row_label="Fresh overruling lists, Supreme Court (sealed half, used 5 times)",
         metrics={"recall": B.metric(int(sm[5]), int(sm[6])), "recall_strict": B.metric(int(sm[1]), int(sm[2])),
                  "recall_strict_attributed": B.metric(int(sm[3]), int(sm[4])),
                  "precision": B.metric(json.loads(ps[1])["listed"], int(ps[2]))},
         build={"source": "round9/SEALED_LOG.md + round9/results/v9c/sealed/fresh_test.txt"},
         notes="Reused from the round-9 lead's single logged run. Fifth use of this half.")
out("gold_fresh", "round9.sealed.json", r)

# Strict fresh lists, two date views
j = json.load(open(os.path.join(HERE, "gold_fresh", "runs", "views", "round9", "fresh7_dev.json"), encoding="utf-8"))
mv = j["views"]["model"]["recall"]["all"]["all"]["strict"]
av = j["views"]["attributed"]["recall"]["all"]["all"]["strict"]
r = load("gold_fresh_strict", "round8.dev.json")
r.update(label="round9", generated=B.now(), blind=False,
         metrics={"recall_model": B.metric(mv["k"], mv["n"]), "recall_attributed": B.metric(av["k"], av["n"])},
         build={"source": "benchmarks/existing/gold_fresh/runs/views/round9/fresh7_dev.json"})
out("gold_fresh_strict", "round9.dev.json", r)
r = load("gold_fresh_strict", "round8.sealed.json")
r.update(label="round9", generated=B.now(), use_note="sealed half, 5th use",
         row_label="Fresh overruling lists, strict: the listed overruling case named (sealed half, used 5 times)",
         metrics={"recall_model": B.metric(int(sm[1]), int(sm[2])), "recall_attributed": B.metric(int(sm[3]), int(sm[4]))},
         build={"source": "round9/SEALED_LOG.md"}, notes="Fifth use of this half.")
out("gold_fresh_strict", "round9.sealed.json", r)

# Old lists with recognised overrulings
ln = [l for l in rd(os.path.join(V, "old_by_class.txt")).splitlines()
      if l.startswith("selfAnnounced+operativeWords+recognised")][0]
s = re.search(r"SCDB (\d+)/(\d+) \(precision (\d+)/(\d+)\)", ln)
c = re.search(r"CRS current (\d+)/(\d+)", ln)
for ds, mets in (("scdb_precedent_alteration_recognised",
                  {"recall": B.metric(int(s[1]), int(s[2])), "precision": B.metric(int(s[3]), int(s[4]))}),
                 ("conan_overruled_recognised", {"recall": B.metric(int(c[1]), int(c[2]))})):
    r = load("scdb_conan_recognised", "%s.round8.all.json" % ds)
    r.update(label="round9", generated=B.now(), metrics=mets, build={"source": "round9/results/v9c/old_by_class.txt"},
             notes=r.get("notes", "") + " Round 9 refuses Supreme Court syllabus quotes (the reporter's words), "
                                         "which removed a few rows deliberately.")
    out("scdb_conan_recognised", "%s.round9.all.json" % ds, r)

# Held-out notes from the round-9 summary
sm9 = rd(os.path.join(V, "summary.txt"))
neg = re.search(r"HOLDOUT NOTES: precedent, Y named.*?negOrPartly (\d+)/(\d+)", sm9)
pp = re.search(r"HOLDOUT NOTES: precedent (\d+)/(\d+)", sm9)
hh = re.search(r"HOLDOUT NOTES: history (\d+)/(\d+)", sm9)
r = load("holdout_notes", "round8.all.json")
r.update(label="round9", generated=B.now(),
         metrics={"recall": B.metric(int(neg[1]), int(neg[2])), "precision": B.metric(int(pp[1]), int(pp[2]))},
         build={"source": "round9/results/v9c/summary.txt (HOLDOUT NOTES lines)"},
         notes="From the round-9 lead's dev-side summary; same scorer and figures as this folder's run (checked on round 8).")
out("holdout_notes", "round9.all.json", r)
r = load("holdout_notes", "holdout_notes_history.round8.all.json")
r.update(label="round9", generated=B.now(), metrics={"precision": B.metric(int(hh[1]), int(hh[2]))},
         primary="precision", plot=["recall", "precision"],
         build={"source": "round9/results/v9c/summary.txt (HOLDOUT NOTES: history)"},
         notes="Precision only: the recall needs the holdout scorer's decisions cache (~100 MB) for v9c, not built "
               "because disk is tight.")
out("holdout_notes", "holdout_notes_history.round9.all.json", r)
