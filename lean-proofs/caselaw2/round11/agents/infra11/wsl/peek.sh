#!/bin/bash
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
ls -la ~/caselaw2/r10_bin/
ls -d $M/data_r10_* $M/base_r1* $M/difftest/r10_* 2>&1 | head -40
ls -la $M/data_r10_v10d | head -50
ls -la $M/base_r10_v9c | head -5
du -sh $M/difftest 2>/dev/null
