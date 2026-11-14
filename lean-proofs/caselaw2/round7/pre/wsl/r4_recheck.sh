#!/bin/bash
# round 4: after the reference fix R4-86: regression set, the 500-round sweep and the real-data reference, concurrently
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
bash $W/wsl/sync.sh code >/dev/null
cd $M; R=difftest/real20
rm -rf difftest/r4_regress2 difftest/r4_drt2
( dirs=$(ls -d fixtures/regress/*/ | sed 's|/$||' | sed "s|^|$M/|" | paste -sd,)
  python3 $T/ref/drt.py --dirs "$dirs" --out $M/difftest/r4_regress2 --jobs 6 --batches 6 > difftest/r4_regress2.txt 2>&1 ) &
( python3 $T/ref/drt.py --seed 63000 --rounds 500 --out $M/difftest/r4_drt2 --jobs 14 --batches 14 > difftest/r4_drt2.txt 2>&1 ) &
python3 $T/ref/precedent_ref.py run --data data --edges ../lean-in-v3 --out $R/ref > $R/ref.log 2>&1
python3 $T/ref/diff.py $R/lean $R/ref --info --tsv $R/diff.tsv > $R/diff.txt 2>&1
python3 $T/ref/real_report.py $R --sample 100 > $R/report.log 2>&1
wait
echo "== regress"; grep -c . difftest/r4_regress2.txt; tail -12 difftest/r4_regress2.txt | head -8
echo "== sweep"; tail -16 difftest/r4_drt2.txt | head -11
echo "== real"; tail -16 $R/diff.txt | head -8
bash $W/wsl/collect.sh real20 | tail -1
cp difftest/r4_regress2.txt difftest/r4_drt2.txt $W/difftest/wsl/
date
