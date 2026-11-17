#!/bin/bash
# Population study driver: pool -> Lean + M -> calibration, for income 2023 and 2024. Detached; logs in runs/pop/.
# usage: harness/pop_all.sh N   (N households per year)
set -e
cd ~/fr
P=runs/pop/venv/bin/python
N=${1:-250000}
for Y in 2024 2023; do
  D=runs/pop/$Y
  mkdir -p $D
  echo "$(date '+%F %T') step 2/4: generating $N households for income $Y" >> PROGRESS_pop.md
  $P harness/pop_gen.py $N $Y $Y $D/cases.jsonl
  echo "$(date '+%F %T') step 3/4: running $N households ($Y) through Lean and M (12 jobs)" >> PROGRESS_pop.md
  $P harness/pop_run.py $D/cases.jsonl $D 12 400 > $D/run.log 2>&1
  echo "$(date '+%F %T') step 2/4: calibrating $Y: $(wc -l < $D/m.jsonl) accepted by M, $(wc -l < $D/m_rejected.jsonl) refused" >> PROGRESS_pop.md
  OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 $P harness/pop_calib.py $Y $D $D/weights.json $D/fit.tsv > $D/calib.log 2>&1
done
echo "$(date '+%F %T') step 3/4: pools run and calibrated (see runs/pop/<year>/calib.log)" >> PROGRESS_pop.md
