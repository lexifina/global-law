#!/bin/bash
# round 10, ref10: the kept universes (main 4, probe 3, fuzz 2), their self-check and the `empty` check; copied to
# round10/agents/ref10/universes/ (without ref_check outputs).
B=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round10/agents/ref10/gen10.sh
ME=$(dirname $B)
S=~/caselaw2/r10ref
bash $B gen kept 100000 4 | grep -v '^  rm_'
bash $B gen keptq 100100 3 --probe | grep -v '^  rm_'
bash $B gen keptf 100200 2 --fuzz 6 | grep -v '^  rm_'
bash $B empty kept
mkdir -p $ME/universes
for d in kept keptq keptf; do
  rsync -a --exclude ref_check --exclude 'ref_*' --exclude 'data_*' $S/$d/ $ME/universes/
done
du -sh $ME/universes
