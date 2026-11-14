#!/bin/bash
# round 11, ref11: the differential sweeps (main / probe / fuzz) + the 552 earlier universes, one after another.
#   sweeps11.sh <tagprefix> <seedbase>   (env BIN, NO52 passed through)
D=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round11/agents/ref11/difftest11.sh
p=$1; s=$2
bash $D sweep ${p} $s 20 > /dev/null 2>&1
bash $D sweep ${p}p $((s+1000)) 10 --probe > /dev/null 2>&1
bash $D sweep ${p}f $((s+2000)) 10 --fuzz 8 > /dev/null 2>&1
bash $D regress ${p}reg > /dev/null 2>&1
for t in ${p} ${p}p ${p}f ${p}reg; do echo "== $t"; grep -v '^  ' ~/caselaw2/r11ref/out/$t.txt | tail -4; head -3 ~/caselaw2/r11ref/out/$t.report.txt; done
for t in ${p} ${p}p; do echo "== selfcheck $t"; grep 'expectations checked' ~/caselaw2/r11ref/out/$t.selfcheck.txt; done
