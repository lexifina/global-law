#!/bin/bash
# round 10, ref10: the reference's remand verdicts on real data v9c + a remand delta folder (remand_verdicts10.py).
#   realremand.sh <tag> <delta folder (Windows path under caselaw-lean-2)>
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
ME=$W/round10/agents/ref10
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
S=~/caselaw2/r10ref
TAG=$1; DELTA=$W/$2
df -h /mnt/c | tail -1
AVAIL_KB=$(df -Pk /mnt/c | awk 'NR==2{print $4}')
[ "$AVAIL_KB" -ge $((8*1024*1024)) ] || { echo "refused: C: under 8 GB"; exit 5; }
rsync -a --delete --exclude __pycache__ /mnt/c/Users/$USER/Documents/global-law-lean/lean-proofs/tools/caselaw2/ref/ $S/cur/tools/caselaw2/ref/
rsync -a --delete /mnt/c/Users/$USER/Documents/global-law-lean/lean-proofs/tools/caselaw2/cues/ $S/cur/tools/caselaw2/cues/
export CASELAW2_REF=$S/cur/tools/caselaw2/ref PYTHONDONTWRITEBYTECODE=1
mkdir -p $S/real $ME/results
python3 -X utf8 $ME/remand_verdicts10.py --base $M/data_r9_v9c --delta $DELTA --work $S/real/work_$TAG --out $S/real/rv_$TAG.tsv 2> $S/real/rv_$TAG.log | tee $ME/results/rv_$TAG.txt
cp $S/real/rv_$TAG.tsv $ME/results/rv_$TAG.tsv
