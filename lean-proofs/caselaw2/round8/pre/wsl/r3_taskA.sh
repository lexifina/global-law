#!/bin/bash
# round 3, Task A: keep three drt9 universes as regression universes, run the regression set and a fresh sweep
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl
for s in 57420 57295 57433; do bash $W/r3_keep.sh drt9 $s r3-ceased-$s; done
bash $W/r3_verify.sh regress ${1:-r3_regress1}
bash $W/r3_verify.sh sweep ${2:-61000} ${3:-240} ${4:-r3_drt1}
date
