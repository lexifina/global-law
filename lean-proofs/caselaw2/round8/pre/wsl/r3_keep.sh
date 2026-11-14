#!/bin/bash
# round 3: keep a sweep universe as a regression universe (Windows tree and mirror). usage: r3_keep.sh <sweep> <seed> <label>
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
for R in $W $M; do mkdir -p $R/fixtures/regress/$3 && cp -r $M/difftest/$1/r$2/data $M/difftest/$1/r$2/edges $R/fixtures/regress/$3/; done
ls $W/fixtures/regress/$3
