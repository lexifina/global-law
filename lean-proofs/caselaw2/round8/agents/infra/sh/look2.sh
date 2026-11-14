cd ~/caselaw2
mkdir -p r8_bin
[ -f r8_bin/caselaw2_r7v3 ] || cp -p r7_bin/caselaw2_v3 r8_bin/caselaw2_r7v3
sha1sum r8_bin/caselaw2_r7v3
ls -la ~/caselaw2/ | head; ls -la ~/caselaw2/global-law-lean
readlink -f ~/caselaw2/lean-proofs ~/caselaw2/global-law-lean/lean-proofs
strings r8_bin/caselaw2_r7v3 | grep -i 'cue_table\|\.json' | head
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
ls $M/difftest | tail -20
cat $M/difftest/r7_v3/lean.log | tail -5
ls -la $M/../lean-in-v3 | head; cat $M/../graph/nodes.count
