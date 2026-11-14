#!/bin/bash
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
ls $M/base_r11_v10d* -d; ls $M/base_r11_v10d.tmp 2>/dev/null | wc -l; ls $M/base_r11_v10d 2>/dev/null | wc -l
ls -la $M/difftest/r11_v10d_check/ 2>/dev/null; tail -3 $M/difftest/r11_v10d_check/lean.log 2>/dev/null
ps aux | grep -c "[c]aselaw2_r10v10d"
