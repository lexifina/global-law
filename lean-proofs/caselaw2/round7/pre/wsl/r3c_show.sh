#!/bin/bash
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
for s in 62391 62003; do D=$M/difftest/r3_drt2/r$s
echo "=== $s"; cat $D/diff.tsv
python3 /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r3_dbg.py $D tx.a 102 20261112 2>&1 | grep -A25 "^cands" | cut -c1-260
grep -P "^10[0-9]\t" $D/data/courts2.tsv | cut -f1-11; grep -P "\t10[0-9]\t|^10[0-9]\t" $D/data/adoption.tsv $D/data/succession.tsv | cut -f1-7
done
