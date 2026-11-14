#!/bin/bash
cd ~/caselaw2/us-caselaw-lean-work/caselaw-lean-2 || exit 1
for n in fjc9_a scdb9_b state9_a1 state9_a2 shadow9_a calpart9_v2 lean9_z nj_test ref9_nj v9a; do
  rm -rf "data_r9_$n" "difftest/r9_$n" && echo "removed $n"
done
ls -d data_r9_*
df -h ~ | tail -1
