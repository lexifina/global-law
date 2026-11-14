M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
cd ~/caselaw2
ls $M | head -80
ls -la $M/data_r7_v3 | head -50
sha1sum r7_bin/* $M/runner/.lake/build/bin/caselaw2
ls -la --time-style=full-iso $M/runner/.lake/build/bin/caselaw2 r7_bin/
cat $M/run_lean.sh
