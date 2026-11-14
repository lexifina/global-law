#!/bin/bash
# round 11, ref11: the current reference (snapshot ~/caselaw2/r11ref/cur) on the round-10 frozen data v10d (WSL mirror
# base_r11_v10d, edges lean-in-v3, as wsl/r11_run.sh) and diff.py against the round-10 frozen Lean output
# round10/out/v10d (Windows, read only). Output ~/caselaw2/r11ref/real/<tag> (ref/ deleted after the diff).
#   realv10d.sh [tag] [data dir under the mirror, default base_r11_v10d] [lean out dir, default round10/out/v10d]
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
ME=$W/round11/agents/ref11
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
S=~/caselaw2/r11ref
TAG=${1:-v10d}; DATA=${2:-base_r11_v10d}; LEAN=${3:-$W/round10/out/v10d}
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
rm -rf $O/ref
