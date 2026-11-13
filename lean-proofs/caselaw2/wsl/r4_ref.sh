#!/bin/bash
# round 4: re-run only the reference on the real data and diff against the Lean output of real20
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
bash $W/wsl/sync.sh code >/dev/null
cd ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
R=difftest/real20
python3 $T/ref/precedent_ref.py run --data data --edges ../lean-in-v3 --out $R/ref > $R/ref.log 2>&1
python3 $T/ref/diff.py $R/lean $R/ref --info --tsv $R/diff.tsv > $R/diff.txt 2>&1
python3 $T/ref/real_report.py $R --sample 100 > $R/report.log 2>&1
tail -2 $R/ref.log; tail -30 $R/diff.txt
bash $W/wsl/collect.sh real20 | tail -1
date
