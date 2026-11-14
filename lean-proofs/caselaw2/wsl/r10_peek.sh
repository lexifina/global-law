#!/bin/bash
# round 10 (lean10): list the WSL mirror's base / data dirs and their markers (read only).
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
cd $M
ls -d base_* data_r8_* data_r9_* data_r10_* 2>/dev/null
for b in base_r9_v8e base_r10_v9c; do echo "$b: $(cat $b/.verified 2>/dev/null || echo none) $(ls $b/*.tsv 2>/dev/null | wc -l) tables"; done
ls ~/caselaw2/r9_bin ~/caselaw2/r10_bin 2>/dev/null
df -h / | tail -1
