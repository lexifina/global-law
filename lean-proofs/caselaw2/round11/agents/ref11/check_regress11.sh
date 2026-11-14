#!/bin/bash
# round 11, agent ref11: the current reference (no anchorTribunal claim) against the round-10 final reference
# (round11/pre/ref), bytes, on the earlier universes (r8ref 534 + round-9 kept 9 + round-10 kept 9). Run INSIDE WSL:
#   MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round11/agents/ref11/check_regress11.sh [tag]'
WIN=/mnt/c/Users/$USER/Documents
W=$WIN/us-caselaw-lean-work/caselaw-lean-2
ME=$W/round11/agents/ref11
S=~/caselaw2/r11ref
R8=~/caselaw2/r8ref
mkdir -p $S/cur/tools/caselaw2 $S/base/tools/caselaw2 $S/a $ME/results
rsync -a --delete --exclude __pycache__ $WIN/global-law-lean/lean-proofs/tools/caselaw2/ref/ $S/cur/tools/caselaw2/ref/
rsync -a --delete $WIN/global-law-lean/lean-proofs/tools/caselaw2/cues/ $S/cur/tools/caselaw2/cues/
rsync -a --delete --exclude __pycache__ --exclude SHA256SUMS $W/round11/pre/ref/ $S/base/tools/caselaw2/ref/
rsync -a --delete $WIN/global-law-lean/lean-proofs/tools/caselaw2/cues/ $S/base/tools/caselaw2/cues/
mkdir -p $S/r9kept $S/r10kept
rsync -a --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $W/round9/agents/ref9/universes/ $S/r9kept/
rsync -a --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $W/round10/agents/ref10/universes/ $S/r10kept/
export CASELAW2_REF=$S/cur/tools/caselaw2/ref PYTHONDONTWRITEBYTECODE=1
sha1sum $CASELAW2_REF/precedent_ref.py $CASELAW2_REF/diff.py $S/base/tools/caselaw2/ref/precedent_ref.py $S/cur/tools/caselaw2/cues/cue_table.json
TAG=${1:-regress11}
roots=""; for r in $R8/regress/* $R8/kept $R8/sweep/r8sw1 $R8/sweep/r8sw1p $R8/sweep/r8sw1f $S/r9kept $S/r10kept; do roots="$roots --root $r"; done
rm -rf $S/a/*
python3 -X utf8 $W/round10/agents/ref10/check_regress10.py --base $S/base/tools/caselaw2/ref $roots --out $S/a --jobs ${JOBS:-8} > $S/$TAG.txt 2>&1
echo "rc=$?" >> $S/$TAG.txt
cp $S/$TAG.txt $ME/results/$TAG.txt
rm -rf $S/a/*
tail -n 12 $S/$TAG.txt
