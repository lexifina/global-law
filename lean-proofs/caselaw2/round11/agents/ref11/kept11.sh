#!/bin/bash
# round 11, ref11: the kept universes (main 4, probe 3, fuzz 2), their self-check and the `empty` check; copied to
# round11/agents/ref11/universes/ (without reference outputs).
B=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round11/agents/ref11/gen11.sh
ME=$(dirname $B)
S=~/caselaw2/r11ref
bash $B gen kept 110000 4 | grep -v '^  at_'
bash $B gen keptq 110100 3 --probe | grep -v '^  at_'
bash $B gen keptf 110200 2 --fuzz 6 | grep -v '^  at_'
bash $B empty kept
bash $B empty keptq
mkdir -p $ME/universes
for d in kept keptq keptf; do
  rsync -a --exclude ref_check --exclude 'ref_*' --exclude 'data_*' $S/$d/ $ME/universes/
done
du -sh $ME/universes
