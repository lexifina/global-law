#!/bin/bash
# round 3: reference conflict candidates at a bound court. usage: r3_show.sh <sweep> <seed> <issue> <court> [asof]
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
D=$M/difftest/$1/r$2
echo "=== $1 $2 $3 $4"; cat $D/diff.tsv
python3 /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r3_dbg.py $D $3 $4 ${5:-20261112} 2>&1 | grep -A40 "^cands"
cut -f1-9 $D/data/courts2.tsv | grep -P "^12"; grep -P "^12" $D/data/adoption.tsv $D/data/succession.tsv | cut -f1-7
