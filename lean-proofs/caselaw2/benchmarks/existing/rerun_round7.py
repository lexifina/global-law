#!/usr/bin/env python3
"""Re-run every NON-sealed scorer of benchmarks/existing on a round-7 build, label `round7`.

    python benchmarks/existing/rerun_round7.py --out round7/out/<name> --data round7/stage/<name>

One command: Shepardized dev (compare.py --split dev), fresh overruling lists dev (score_fresh copy, dev only),
held-out later-court notes (check_no_leak + score_holdout on the frozen pool), behavioural test (classes_r5.tsv),
SCDB precedentAlteration + Constitution Annotated (eval/score.py). Writes
benchmarks/existing/<bench>/runs/round7*/ and results/*round7*.json. The sealed halves (Shepardized sealed,
gold_fresh test) are NOT run here: each is a single logged run done by hand after a freeze
(round6/history/SEALED_LOG.md, round5/gold_fresh/sealed/TEST_RUNS.log).

Python 3 with numpy (Windows: the same interpreter that ran round 4/6, e.g. Python312). ~1 minute plus the
one-off decisions cache (_r5tests/cache) for a new data dir.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--data", required=True)
ap.add_argument("--label", default="round7")
ap.add_argument("--only", default="shep,fresh,holdout,behaviour,scdb")
a = ap.parse_args()
sys.exit(subprocess.call([sys.executable, os.path.join(HERE, "run_existing.py"), "--label", a.label, "--out", a.out,
                          "--data", a.data, "--only", a.only]))
