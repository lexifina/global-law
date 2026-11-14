#!/bin/bash
# round 3 final real-data run: fresh data snapshot into the mirror, Lean and reference side by side, diff, copy back
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
R=difftest/${1:-real19}
date
bash $W/wsl/sync.sh all | tail -1
cd ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
wc -l data/treatments.tsv data/courts2.tsv data/decisions2.tsv
rm -rf $R; mkdir -p $R
python3 $T/ref/precedent_ref.py run --data data --edges ../lean-in-v3 --out $R/ref > $R/ref.log 2>&1 &
( time PAR=8 bash run_lean.sh 8 data ../lean-in-v3 $R/lean ) > $R/lean.log 2>&1
wait
python3 $T/ref/diff.py $R/lean $R/ref --info --tsv $R/diff.tsv > $R/diff.txt 2>&1
python3 $T/ref/real_report.py $R --sample 100 > $R/report.log 2>&1
tail -5 $R/lean.log; tail -3 $R/ref.log; tail -40 $R/diff.txt
bash $W/wsl/collect.sh ${1:-real19} | tail -12
date
