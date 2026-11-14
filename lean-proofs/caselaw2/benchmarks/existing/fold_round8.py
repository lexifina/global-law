#!/usr/bin/env python3
"""Fold round-8 LOGGED results (no sealed scorer is run) into benchmarks/existing/*/results/.

    python -I fold_round8.py

Every number is parsed from a file; nothing is hand-entered.

  shepardized_coa/results/round8.sealed.json   <- round8/SEALED_LOG.md compare.py line (--split sealed, v8e); 3rd use
  gold_fresh/results/round8.sealed.json        <- round8/SEALED_LOG.md lead's line (strict model / attributed /
                                                  lenient) + round8/results/v8e/sealed/fresh_test.txt (precision side);
                                                  4th use
  gold_fresh_strict/results/round8.{dev,sealed}.json  <- gold_fresh/runs/views/round8/fresh7_dev.json
                                                  (round7/score_fresh7.py --split dev on v8e, run here) and the log line
  scdb_conan_recognised/results/*.round8.all.json <- round8/results/v8e/old_by_class.txt
Sealed rows get a 'use_note' and a row label saying the half has been used repeatedly.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
ROOT = os.path.dirname(BENCH)
R8 = os.path.join(ROOT, "round8")
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


log = rd(os.path.join(R8, "SEALED_LOG.md"))
flat = re.sub(r"\s+", " ", log)

# Shepardized sealed (3rd use)
line = [l for l in log.splitlines() if "--split sealed" in l and "round8/out/v8e" in l][-1]
rec = re.search(r"recall NEG strict (\d+)/(\d+)", line)
pre = re.search(r"precision strict (\d+)/(\d+)", line)
cln = re.search(r"CLEAN (\d+)/(\d+)", line)
r = load("shepardized_coa", "round7.sealed.json")
SHEP_LABEL = "Shepardized Courts of Appeals: decision reversed/vacated/withdrawn (sealed half, used 3 times)"
r.update(label="round8", generated=B.now(), row_label=SHEP_LABEL, use_note="sealed half, 3rd use",
         metrics={"recall": B.metric(int(rec[1]), int(rec[2])), "precision": B.metric(int(pre[1]), int(pre[2])),
                  "clean": B.metric(int(cln[1]), int(cln[2]))},
         build={"source": "round8/SEALED_LOG.md (compare.py --split sealed on round8/out/v8e)"},
         notes="Reused from the round-8 lead's single logged run. Third use of this half: no longer a fresh blind test.")
out("shepardized_coa", "round8.sealed.json", r)

# Fresh lists sealed (4th use)
sm = re.search(r"fresh sealed, 4th use: strict model (\d+)/(\d+).*?strict attributed (\d+)/(\d+).*?lenient (\d+)/(\d+)",
               flat)
ps = re.search(r"precision side \(model view[^{]*(\{[^}]*\}) of (\d+)",
               rd(os.path.join(R8, "results", "v8e", "sealed", "fresh_test.txt")))
r = load("gold_fresh", "round7.sealed.json")
FRESH_LABEL = "Fresh overruling lists, Supreme Court (sealed half, used 4 times)"
r.update(label="round8", generated=B.now(), row_label=FRESH_LABEL, use_note="sealed half, 4th use",
         metrics={"recall": B.metric(int(sm[5]), int(sm[6])), "recall_strict": B.metric(int(sm[1]), int(sm[2])),
                  "recall_strict_attributed": B.metric(int(sm[3]), int(sm[4])),
                  "precision": B.metric(json.loads(ps[1])["listed"], int(ps[2]))},
         build={"source": "round8/SEALED_LOG.md + round8/results/v8e/sealed/fresh_test.txt"},
         notes="Reused from the round-8 lead's single logged run. Fourth use of this half: burned.")
out("gold_fresh", "round8.sealed.json", r)

# Strict fresh lists, two date views
j = json.load(open(os.path.join(HERE, "gold_fresh", "runs", "views", "round8", "fresh7_dev.json"), encoding="utf-8"))
mv = j["views"]["model"]["recall"]["all"]["all"]["strict"]
av = j["views"]["attributed"]["recall"]["all"]["all"]["strict"]
r = load("gold_fresh_strict", "round7.dev.json")
r.update(label="round8", generated=B.now(), blind=False,
         metrics={"recall_model": B.metric(mv["k"], mv["n"]), "recall_attributed": B.metric(av["k"], av["n"])},
         build={"source": "benchmarks/existing/gold_fresh/runs/views/round8/fresh7_dev.json"})
out("gold_fresh_strict", "round8.dev.json", r)
r = load("gold_fresh_strict", "round7.sealed.json")
r.update(label="round8", generated=B.now(), use_note="sealed half, 4th use",
         row_label="Fresh overruling lists, strict: the listed overruling case named (sealed half, used 4 times)",
         metrics={"recall_model": B.metric(int(sm[1]), int(sm[2])), "recall_attributed": B.metric(int(sm[3]), int(sm[4]))},
         build={"source": "round8/SEALED_LOG.md"}, notes="Fourth use of this half: burned.")
out("gold_fresh_strict", "round8.sealed.json", r)

# Old lists with recognised overrulings (not blind)
ln = [l for l in rd(os.path.join(R8, "results", "v8e", "old_by_class.txt")).splitlines()
      if l.startswith("selfAnnounced+operativeWords+recognised")][0]
s = re.search(r"SCDB (\d+)/(\d+) \(precision (\d+)/(\d+)\)", ln)
c = re.search(r"CRS current (\d+)/(\d+)", ln)
for ds, mets in (("scdb_precedent_alteration_recognised",
                  {"recall": B.metric(int(s[1]), int(s[2])), "precision": B.metric(int(s[3]), int(s[4]))}),
                 ("conan_overruled_recognised", {"recall": B.metric(int(c[1]), int(c[2]))})):
    r = load("scdb_conan_recognised", "%s.round7.all.json" % ds)
    r.update(label="round8", generated=B.now(), metrics=mets,
             build={"source": "round8/results/v8e/old_by_class.txt"})
    out("scdb_conan_recognised", "%s.round8.all.json" % ds, r)

# Earlier sealed rows of the same halves carry the new label so the row reads consistently
for sub, lab, lbl in (("shepardized_coa", "round6", SHEP_LABEL), ("shepardized_coa", "round7", SHEP_LABEL)):
    pass  # the graph takes the row label from the latest build; earlier files are left as written
