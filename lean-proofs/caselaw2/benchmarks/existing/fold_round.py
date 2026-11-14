#!/usr/bin/env python3
"""Fold one frozen round's LOGGED results into benchmarks/existing/*/results/ (no sealed scorer is run).

    python -I fold_round.py --round 11 --variant v11d --prev round10 --shep-use 6 --fresh-use 7

Generic form of fold_round8/9/10.py (same sources, same parsing). Every number is parsed from a file:

  shepardized_coa/results/round<N>.sealed.json   <- round<N>/SEALED_LOG.md compare.py line on round<N>/out/<variant>
  gold_fresh/results/round<N>.sealed.json        <- round<N>/SEALED_LOG.md 'fresh sealed, <k>th use' line +
                                                    round<N>/results/<variant>/sealed/fresh_test.txt (precision side)
  gold_fresh_strict/results/round<N>.{dev,sealed}.json <- gold_fresh/runs/views/round<N>/fresh7_dev.json + the log line
  scdb_conan_recognised/results/*.round<N>.all.json   <- round<N>/results/<variant>/old_by_class.txt
  holdout_notes/results/round<N>.all.json             <- round<N>/results/<variant>/summary.txt HOLDOUT NOTES lines
        (recall = negOrPartly, precision = 'precedent k/n'; equal to this folder's scorer, checked on round 8)
  holdout_notes/results/holdout_notes_history.round<N>.all.json <- summary 'HOLDOUT NOTES: history' (precision only;
        the recall needs a ~100 MB decisions cache per build, not built while disk is tight)
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
ROOT = os.path.dirname(BENCH)
sys.path.insert(0, os.path.join(BENCH, "common"))
import benchlib as B  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--round", type=int, required=True)
ap.add_argument("--variant", required=True)
ap.add_argument("--prev", required=True, help="label of the previous build's result files used as templates")
ap.add_argument("--shep-use", type=int, required=True)
ap.add_argument("--fresh-use", type=int, required=True)
a = ap.parse_args()

LAB = "round%d" % a.round
RD = os.path.join(ROOT, LAB)
V = os.path.join(RD, "results", a.variant)
OUT_REL = "%s/out/%s" % (LAB, a.variant)


def nth(k):
    return "%d%s" % (k, {1: "st", 2: "nd", 3: "rd"}.get(k if k < 20 else k % 10, "th"))


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def load(sub, name):
    return json.load(open(os.path.join(HERE, sub, "results", name), encoding="utf-8"))


def out(sub, name, r):
    p = os.path.join(HERE, sub, "results", name)
    B.write_result(p, r)
    print("wrote", os.path.relpath(p, BENCH), {k: "%d/%d" % (v["k"], v["n"]) for k, v in r["metrics"].items()})


log = rd(os.path.join(RD, "SEALED_LOG.md"))

line = [l for l in log.splitlines() if "--split sealed" in l and OUT_REL in l][-1]
rec = re.search(r"recall NEG strict (\d+)/(\d+)", line)
pre = re.search(r"precision strict (\d+)/(\d+)", line)
cln = re.search(r"CLEAN (\d+)/(\d+)", line)
r = load("shepardized_coa", "%s.sealed.json" % a.prev)
r.update(label=LAB, generated=B.now(), use_note="sealed half, %s use" % nth(a.shep_use),
         row_label="Shepardized Courts of Appeals: decision reversed/vacated/withdrawn (sealed half, used %d times)"
         % a.shep_use,
         metrics={"recall": B.metric(int(rec[1]), int(rec[2])), "precision": B.metric(int(pre[1]), int(pre[2])),
                  "clean": B.metric(int(cln[1]), int(cln[2]))},
         build={"source": "%s/SEALED_LOG.md (compare.py --split sealed on %s)" % (LAB, OUT_REL)},
         notes="Reused from the %s lead's single logged run. Use %d of this half." % (LAB, a.shep_use))
out("shepardized_coa", "%s.sealed.json" % LAB, r)

fl = [l for l in log.splitlines() if "fresh sealed, %s use" % nth(a.fresh_use) in l][-1]
sm = re.search(r"strict model (\d+)/(\d+).*?strict attributed (\d+)/(\d+).*?lenient model (\d+)/(\d+)", fl)
ps = re.search(r"precision side \(model view[^{]*(\{[^}]*\}) of (\d+)", rd(os.path.join(V, "sealed", "fresh_test.txt")))
r = load("gold_fresh", "%s.sealed.json" % a.prev)
r.update(label=LAB, generated=B.now(), use_note="sealed half, %s use" % nth(a.fresh_use),
         row_label="Fresh overruling lists, Supreme Court (sealed half, used %d times)" % a.fresh_use,
         metrics={"recall": B.metric(int(sm[5]), int(sm[6])), "recall_strict": B.metric(int(sm[1]), int(sm[2])),
                  "recall_strict_attributed": B.metric(int(sm[3]), int(sm[4])),
                  "precision": B.metric(json.loads(ps[1])["listed"], int(ps[2]))},
         build={"source": "%s/SEALED_LOG.md + %s/results/%s/sealed/fresh_test.txt" % (LAB, LAB, a.variant)},
         notes="Reused from the %s lead's single logged run. Use %d of this half." % (LAB, a.fresh_use))
out("gold_fresh", "%s.sealed.json" % LAB, r)

j = json.load(open(os.path.join(HERE, "gold_fresh", "runs", "views", LAB, "fresh7_dev.json"), encoding="utf-8"))
mv = j["views"]["model"]["recall"]["all"]["all"]["strict"]
av = j["views"]["attributed"]["recall"]["all"]["all"]["strict"]
r = load("gold_fresh_strict", "%s.dev.json" % a.prev)
r.update(label=LAB, generated=B.now(), blind=False,
         metrics={"recall_model": B.metric(mv["k"], mv["n"]), "recall_attributed": B.metric(av["k"], av["n"])},
         build={"source": "benchmarks/existing/gold_fresh/runs/views/%s/fresh7_dev.json" % LAB})
out("gold_fresh_strict", "%s.dev.json" % LAB, r)
r = load("gold_fresh_strict", "%s.sealed.json" % a.prev)
r.update(label=LAB, generated=B.now(), use_note="sealed half, %s use" % nth(a.fresh_use),
         row_label="Fresh overruling lists, strict: the listed overruling case named (sealed half, used %d times)"
         % a.fresh_use,
         metrics={"recall_model": B.metric(int(sm[1]), int(sm[2])), "recall_attributed": B.metric(int(sm[3]), int(sm[4]))},
         build={"source": "%s/SEALED_LOG.md" % LAB}, notes="Use %d of this half." % a.fresh_use)
out("gold_fresh_strict", "%s.sealed.json" % LAB, r)

ln = [l for l in rd(os.path.join(V, "old_by_class.txt")).splitlines()
      if l.startswith("selfAnnounced+operativeWords+recognised")][0]
s = re.search(r"SCDB (\d+)/(\d+) \(precision (\d+)/(\d+)\)", ln)
c = re.search(r"CRS current (\d+)/(\d+)", ln)
for ds, mets in (("scdb_precedent_alteration_recognised",
                  {"recall": B.metric(int(s[1]), int(s[2])), "precision": B.metric(int(s[3]), int(s[4]))}),
                 ("conan_overruled_recognised", {"recall": B.metric(int(c[1]), int(c[2]))})):
    r = load("scdb_conan_recognised", "%s.%s.all.json" % (ds, a.prev))
    r.update(label=LAB, generated=B.now(), metrics=mets,
             build={"source": "%s/results/%s/old_by_class.txt" % (LAB, a.variant)})
    out("scdb_conan_recognised", "%s.%s.all.json" % (ds, LAB), r)

smy = rd(os.path.join(V, "summary.txt"))
neg = re.search(r"HOLDOUT NOTES: precedent, Y named.*?negOrPartly (\d+)/(\d+)", smy)
pp = re.search(r"HOLDOUT NOTES: precedent (\d+)/(\d+)", smy)
hh = re.search(r"HOLDOUT NOTES: history (\d+)/(\d+)", smy)
r = load("holdout_notes", "%s.all.json" % a.prev)
r.update(label=LAB, generated=B.now(),
         metrics={"recall": B.metric(int(neg[1]), int(neg[2])), "precision": B.metric(int(pp[1]), int(pp[2]))},
         build={"source": "%s/results/%s/summary.txt (HOLDOUT NOTES lines)" % (LAB, a.variant)})
out("holdout_notes", "%s.all.json" % LAB, r)
r = load("holdout_notes", "holdout_notes_history.%s.all.json" % a.prev)
r.update(label=LAB, generated=B.now(), metrics={"precision": B.metric(int(hh[1]), int(hh[2]))},
         primary="precision", plot=["recall", "precision"],
         build={"source": "%s/results/%s/summary.txt (HOLDOUT NOTES: history)" % (LAB, a.variant)})
out("holdout_notes", "holdout_notes_history.%s.all.json" % LAB, r)
