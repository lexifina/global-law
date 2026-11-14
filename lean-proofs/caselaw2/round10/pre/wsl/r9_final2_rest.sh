#!/bin/bash
# round 9 (lean9): the batch-2 regressions cut off at 03:21 (C: full, WSL read-only): a2 and c, in parallel (PAR=6).
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
L=~/caselaw2/r9_final2_logs
mkdir -p $L
echo "binary $(sha1sum < ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/runner/.lake/build/bin/caselaw2 | cut -c1-40) $(date '+%T')"
( PAR=6 bash $W/wsl/r7_lean_base.sh a2 > $L/reg_a2.log 2>&1; echo "rc=$?" >> $L/reg_a2.log ) &
sleep 40
( PAR=6 bash $W/wsl/r7_lean_base.sh c > $L/reg_c.log 2>&1; echo "rc=$?" >> $L/reg_c.log ) &
wait
rc=0
for f in reg_a2 reg_c; do grep -v 'byte-identical\|^assembled\|^real\|^user\|^sys\|^$' $L/$f.log | head -20; echo "$f: $(grep -c byte-identical $L/$f.log) byte-identical files, $(tail -1 $L/$f.log)"; grep -q 'rc=0' $L/$f.log || rc=1; done
echo "binary $(sha1sum < ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/runner/.lake/build/bin/caselaw2 | cut -c1-40)"
echo "REST rc=$rc $(date '+%T')"
