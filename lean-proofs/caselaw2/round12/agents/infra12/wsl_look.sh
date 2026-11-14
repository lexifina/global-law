#!/bin/bash
M=$HOME/caselaw2/us-caselaw-lean-work/caselaw-lean-2
ls -d $M/data_r1* $M/base_r1* 2>&1
ls -la $M/data_r11_v11d | head -45
sha1sum < ~/caselaw2/r11_bin/caselaw2_lean11_s51
du -sh $M/data_r11_v11d
