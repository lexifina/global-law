#!/bin/bash
# round 4 final: sync, audit check, then concurrently: regression set, 500-round sweep, real-data run (Lean + reference)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
R=difftest/real20
date
bash $W/wsl/sync.sh all | tail -1
cd $M
echo "== audit"; python3 audit/audit.py check 2>&1 | tail -4
wc -l data/treatments.tsv data/treatment_witness.tsv data/courts2.tsv
rm -rf $R difftest/r4_regress difftest/r4_drt; mkdir -p $R
( dirs=$(ls -d fixtures/regress/*/ | sed 's|/$||' | sed "s|^|$M/|" | paste -sd,)
  python3 $T/ref/drt.py --dirs "$dirs" --out $M/difftest/r4_regress --jobs 6 --batches 6 > difftest/r4_regress.txt 2>&1 ) &
( python3 $T/ref/drt.py --seed 63000 --rounds 500 --out $M/difftest/r4_drt --jobs 10 --batches 10 > difftest/r4_drt.txt 2>&1 ) &
python3 $T/ref/precedent_ref.py run --data data --edges ../lean-in-v3 --out $R/ref > $R/ref.log 2>&1 &
( time PAR=8 bash run_lean.sh 8 data ../lean-in-v3 $R/lean ) > $R/lean.log 2>&1
wait
python3 $T/ref/diff.py $R/lean $R/ref --info --tsv $R/diff.tsv > $R/diff.txt 2>&1
python3 $T/ref/real_report.py $R --sample 100 > $R/report.log 2>&1
echo "== regress"; tail -12 difftest/r4_regress.txt
echo "== sweep"; tail -25 difftest/r4_drt.txt
echo "== real"; tail -5 $R/lean.log; tail -3 $R/ref.log; tail -45 $R/diff.txt
bash $W/wsl/collect.sh real20 | tail -3
mkdir -p $W/difftest/wsl; cp difftest/r4_regress.txt difftest/r4_drt.txt $W/difftest/wsl/
date
