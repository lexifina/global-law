#!/bin/bash
# Lean regression benchmarks, run before and after a Lean change made for the OpenFisca suite.
# usage: ofsuite_regress.sh TAG      (outputs in ~/fr/runs/ofsuite/regress/TAG; inputs generated once)
# 1. final_run.sh's 100,000 random households (gen.py 100000 2026, income 2024-2025): Lean vs M on 12 figures
# 2. 20,000 random households for income 2020-2023 (gen.py seed 2027)
# 3. official worked examples; 4. OpenFisca calculator tests (of_calc_tests.py)
# 5. production-simulator verdicts already saved (targets 371, family structures 126), rescored for Lean
set -u
TAG=$1
R=~/fr/runs/ofsuite/regress
O=$R/$TAG
mkdir -p $O
cd ~/fr/harness
ls -la --time-style=full-iso ~/fr/lean/.lake/build/bin/frtax > $O/lean_binary.txt
[ -f $R/final.jsonl ] || python3 -I gen.py 100000 2026 $R/final.jsonl
[ -f $R/old.jsonl ] || python3 -I gen.py 20000 2027 $R/old.jsonl 2020,2021,2022,2023
python3 -I run.py $R/final.jsonl $O/final 30 > $O/final_report.txt 2>&1
python3 -I run.py $R/old.jsonl $O/old 30 > $O/old_report.txt 2>&1
. ~/fr/venv-of/bin/activate
python official_examples_run.py ~/fr/data/official_examples.jsonl $O/official_examples.json > $O/official_examples.txt 2>&1
python of_calc_tests.py $O/of_calc.json > $O/of_calc.txt 2>&1
for s in targets:sim_targets_v2.jsonl:targets.jsonl famt:sim_fam.jsonl:fam_targets.jsonl; do
  IFS=: read d sim cases <<< "$s"
  mkdir -p $O/$d; cp ~/fr/runs/$d/m.jsonl ~/fr/runs/$d/cal.log $O/$d/ 2>/dev/null
  python sim_compare2.py ~/fr/runs/$sim ~/fr/runs/$cases $O/$d > $O/sim_$d.txt 2>&1
done
deactivate
echo REGRESS-DONE $TAG
