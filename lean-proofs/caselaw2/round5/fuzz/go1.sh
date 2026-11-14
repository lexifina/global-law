#!/bin/bash
# round-5 fuzz: refresh the snapshot, then a first small campaign
H=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round5/fuzz
bash $H/setup.sh r4 || exit 1
bash $H/run.sh all ${1:-60} ${2:-5} ${3:-t1}
