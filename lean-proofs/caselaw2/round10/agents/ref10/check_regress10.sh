#!/bin/bash
# round 10, agent ref10: the current reference (no round-10 table) against the round-9 final reference
# (round10/pre/ref, 7432cbed), bytes, on the earlier universes. Run INSIDE WSL Ubuntu:
#   MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round10/agents/ref10/check_regress10.sh [tag]'
# Universes (read only): ~/caselaw2/r8ref/regress/* (435), ~/caselaw2/r8ref/kept (9), ~/caselaw2/r8ref/sweep/r8sw1*
# (90), and round9/agents/ref9/universes (9 round-9 kept, copied to ~/caselaw2/r10ref/r9kept).
WIN=/mnt/c/Users/$USER/Documents
W=$WIN/us-caselaw-lean-work/caselaw-lean-2
ME=$W/round10/agents/ref10
S=~/caselaw2/r10ref
R8=~/caselaw2/r8ref
mkdir -p $S/cur/tools/caselaw2 $S/base/tools/caselaw2 $S/a $ME/results
rsync -a --delete --exclude __pycache__ $WIN/global-law-lean/lean-proofs/tools/caselaw2/ref/ $S/cur/tools/caselaw2/ref/
rsync -a --delete $WIN/global-law-lean/lean-proofs/tools/caselaw2/cues/ $S/cur/tools/caselaw2/cues/
rsync -a --delete --exclude __pycache__ $W/round10/pre/ref/ $S/base/tools/caselaw2/ref/
rsync -a --delete $WIN/global-law-lean/lean-proofs/tools/caselaw2/cues/ $S/base/tools/caselaw2/cues/
mkdir -p $S/r9kept
rsync -a --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $W/round9/agents/ref9/universes/ $S/r9kept/
export CASELAW2_REF=$S/cur/tools/caselaw2/ref PYTHONDONTWRITEBYTECODE=1
sha1sum $CASELAW2_REF/precedent_ref.py $CASELAW2_REF/diff.py $S/base/tools/caselaw2/ref/precedent_ref.py $S/cur/tools/caselaw2/cues/cue_table.json
TAG=${1:-regress10}
roots=""; for r in $R8/regress/* $R8/kept $R8/sweep/r8sw1 $R8/sweep/r8sw1p $R8/sweep/r8sw1f $S/r9kept; do roots="$roots --root $r"; done
rm -rf $S/a/*
python3 -X utf8 $ME/check_regress10.py --base $S/base/tools/caselaw2/ref $roots --out $S/a --jobs ${JOBS:-8} > $S/$TAG.txt 2>&1
echo "rc=$?" >> $S/$TAG.txt
cp $S/$TAG.txt $ME/results/$TAG.txt
tail -n 12 $S/$TAG.txt
