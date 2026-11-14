#!/bin/bash
# round 12 lead: the Python reference (tools/caselaw2/ref, read-only snapshot) on a staged variant's WSL data dir,
# diffed against that variant's Lean output (as round11/agents/ref11/realv10d.sh).   usage: ref_real12.sh <name>
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
S=~/caselaw2/r12ref
N=$1; DATA=data_r12_$N; LEAN=$W/round12/out/$N
AVAIL_KB=$(df -Pk /mnt/c | awk 'NR==2{print $4}')
[ "$AVAIL_KB" -ge $((8*1024*1024)) ] || { echo "refused: C: under 8 GB"; exit 5; }
mkdir -p $S/cur/tools/caselaw2
rsync -a --delete --exclude __pycache__ /mnt/c/Users/$USER/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref/ $S/cur/tools/caselaw2/ref/
rsync -a --delete /mnt/c/Users/$USER/Documents/global-law-lean/lean-proofs/tools/caselaw2/cues/ $S/cur/tools/caselaw2/cues/
export PYTHONDONTWRITEBYTECODE=1
O=$S/real/$N; rm -rf $O; mkdir -p $O
sha1sum $S/cur/tools/caselaw2/ref/precedent_ref.py | tee $O/ref.sha1
cd $M
( time python3 $S/cur/tools/caselaw2/ref/precedent_ref.py run --data $DATA --edges ../lean-in-v3 --out $O/ref ) > $O/ref.log 2>&1
tail -3 $O/ref.log
python3 $S/cur/tools/caselaw2/ref/diff.py $LEAN $O/ref --info --tsv $O/diff.tsv > $O/diff.txt 2>&1
cp $O/diff.txt $W/round12/lead/ref_$N.diff.txt
head -14 $O/diff.txt
rm -rf $O/ref
