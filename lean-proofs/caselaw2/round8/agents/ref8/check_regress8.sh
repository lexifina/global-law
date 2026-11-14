#!/bin/bash
# round 8, agent ref8: the current reference (no round-8 table) on the earlier rounds' universes, against the stored
# round-7 reference output (bytes) and the stored round-7 Lean output (canonical diff). Run INSIDE WSL Ubuntu:
#   MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round8/agents/ref8/check_regress8.sh'
# The reference and the cue table are copied to ~/caselaw2/r8ref/lp/tools/caselaw2/{ref,cues} first (a snapshot).
# Universes (read only): ~/caselaw2/r7ref/regress/* (the 267 round-6 universes, rerun by round 7's difftest run 3),
# ~/caselaw2/r7ref/kept (18 round-7 kept universes), ~/caselaw2/r7ref/sweep/r7sw3* (150 round-7 sweep universes).
WIN=/mnt/c/Users/$USER/Documents
W=$WIN/us-caselaw-lean-work/caselaw-lean-2
ME=$W/round8/agents/ref8
S=~/caselaw2/r8ref
R7=~/caselaw2/r7ref
mkdir -p $S/lp/tools/caselaw2 $S/a $ME/results
rsync -a --delete --exclude __pycache__ $WIN/global-law-lean/lean-proofs/tools/caselaw2/ref/ $S/lp/tools/caselaw2/ref/
rsync -a --delete $WIN/global-law-lean/lean-proofs/tools/caselaw2/cues/ $S/lp/tools/caselaw2/cues/
export CASELAW2_REF=$S/lp/tools/caselaw2/ref PYTHONDONTWRITEBYTECODE=1
sha1sum $CASELAW2_REF/precedent_ref.py $CASELAW2_REF/diff.py $S/lp/tools/caselaw2/cues/cue_table.json
TAG=${1:-regress8}
python3 -X utf8 $ME/check_regress8.py --root $R7/regress/regress --root $R7/regress/fixed \
  --root $R7/regress/sweep_r6sw2 --root $R7/regress/sweep_r6sw2p --root $R7/regress/sweep_r6sw2f \
  --root $R7/kept --root $R7/sweep/r7sw3 --root $R7/sweep/r7sw3p --root $R7/sweep/r7sw3n --root $R7/sweep/r7sw3f \
  --out $S/a --jobs ${JOBS:-10} > $S/$TAG.txt 2>&1
echo "rc=$?" >> $S/$TAG.txt
cp $S/$TAG.txt $ME/results/$TAG.txt
tail -n 25 $S/$TAG.txt
