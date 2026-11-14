#!/bin/bash
# round 9, agent ref9: the current reference (no round-9 table) on the earlier rounds' universes, against the stored
# round-8 reference output (bytes) and the stored round-8 Lean output (canonical diff). Run INSIDE WSL Ubuntu:
#   MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round9/agents/ref9/check_regress9.sh [tag]'
# Snapshot of the reference and cue table: ~/caselaw2/r9ref/lp/tools/caselaw2/{ref,cues}. Universes (read only):
# ~/caselaw2/r8ref/regress/* (435: 267 round-6 + 18 round-7 kept + 150 round-7 sweep), ~/caselaw2/r8ref/kept (9 round-8
# kept), ~/caselaw2/r8ref/sweep/r8sw1* (90 round-8 sweep).
WIN=/mnt/c/Users/$USER/Documents
W=$WIN/us-caselaw-lean-work/caselaw-lean-2
ME=$W/round9/agents/ref9
S=~/caselaw2/r9ref
R8=~/caselaw2/r8ref
mkdir -p $S/lp/tools/caselaw2 $S/a $ME/results
rsync -a --delete --exclude __pycache__ $WIN/global-law-lean/lean-proofs/tools/caselaw2/ref/ $S/lp/tools/caselaw2/ref/
rsync -a --delete $WIN/global-law-lean/lean-proofs/tools/caselaw2/cues/ $S/lp/tools/caselaw2/cues/
export CASELAW2_REF=$S/lp/tools/caselaw2/ref PYTHONDONTWRITEBYTECODE=1
sha1sum $CASELAW2_REF/precedent_ref.py $CASELAW2_REF/diff.py $S/lp/tools/caselaw2/cues/cue_table.json
TAG=${1:-regress9}
roots=""; for r in $R8/regress/* $R8/kept $R8/sweep/r8sw1 $R8/sweep/r8sw1p $R8/sweep/r8sw1f; do roots="$roots --root $r"; done
rm -rf $S/a/*
python3 -X utf8 $ME/check_regress9.py $roots --out $S/a --jobs ${JOBS:-10} > $S/$TAG.txt 2>&1
echo "rc=$?" >> $S/$TAG.txt
cp $S/$TAG.txt $ME/results/$TAG.txt
tail -n 25 $S/$TAG.txt
