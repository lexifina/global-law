#!/bin/bash
# round 10, ref10: the current reference (snapshot ~/caselaw2/r10ref/cur) on the round-9 frozen data v9c (WSL mirror
# data_r9_v9c, edges lean-in-v3, as wsl/r10_run.sh) and diff.py against the round-9 frozen Lean output
# round9/out/v9c (Windows, read only). Output ~/caselaw2/r10ref/real/<tag>; diff.txt copied to results/.
#   realv9c.sh [tag] [data dir under the mirror, default data_r9_v9c] [lean out dir, default round9/out/v9c]
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
ME=$W/round10/agents/ref10
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
S=~/caselaw2/r10ref
TAG=${1:-v9c}; DATA=${2:-data_r9_v9c}; LEAN=${3:-$W/round9/out/v9c}
df -h /mnt/c | tail -1
AVAIL_KB=$(df -Pk /mnt/c | awk 'NR==2{print $4}')
[ "$AVAIL_KB" -ge $((8*1024*1024)) ] || { echo "refused: C: under 8 GB"; exit 5; }
rsync -a --delete --exclude __pycache__ /mnt/c/Users/$USER/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref/ $S/cur/tools/caselaw2/ref/
rsync -a --delete /mnt/c/Users/$USER/Documents/global-law-lean/lean-proofs/tools/caselaw2/cues/ $S/cur/tools/caselaw2/cues/
export PYTHONDONTWRITEBYTECODE=1
O=$S/real/$TAG
rm -rf $O; mkdir -p $O
sha1sum $S/cur/tools/caselaw2/ref/precedent_ref.py | tee $O/ref.sha1
cd $M
( time python3 $S/cur/tools/caselaw2/ref/precedent_ref.py run --data $DATA --edges ../lean-in-v3 --out $O/ref ) > $O/ref.log 2>&1
tail -3 $O/ref.log
python3 $S/cur/tools/caselaw2/ref/diff.py $LEAN $O/ref --info --tsv $O/diff.tsv > $O/diff.txt 2>&1
mkdir -p $ME/results
cp $O/diff.txt $ME/results/real_$TAG.diff.txt
head -12 $O/diff.txt
