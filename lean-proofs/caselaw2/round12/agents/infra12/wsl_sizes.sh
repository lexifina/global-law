#!/bin/bash
M=$HOME/caselaw2/us-caselaw-lean-work/caselaw-lean-2
B=$M/base_r12_v11d
echo "base_r12_v11d: $(ls $B/*.tsv | wc -l) tables; files with link count 1 (own copies): $(find $B -maxdepth 1 -type f -links 1 -name '*.tsv' -printf '%f %s\n' | tr '\n' ' ')"
ls -la ~/caselaw2/r12_bin/
ls -d $M/data_r12_* $M/difftest/r12_* 2>/dev/null
