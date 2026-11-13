#!/bin/bash
# round 3 final (code only): sync, audit check, regression set, 500-round sweep
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
bash $W/wsl/sync.sh code >/dev/null
cd ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
echo "== audit"; python3 audit/audit.py check 2>&1 | tail -15
echo "== regress"; bash $W/wsl/r3_verify.sh regress r3_regress2
echo "== sweep"; bash $W/wsl/r3_verify.sh sweep 62000 500 r3_drt2
mkdir -p $W/difftest/wsl; cp difftest/r3_fail8.txt difftest/r3_regress1.txt difftest/r3_drt1.txt difftest/r3_regress2.txt difftest/r3_drt2.txt $W/difftest/wsl/
date
