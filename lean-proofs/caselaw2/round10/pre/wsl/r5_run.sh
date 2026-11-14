#!/bin/bash
# round 5: run the Lean runner (and optionally the Python reference + diff) on a staged variant.
#   usage: r5_run.sh <name> [ref]      <name> = folder under round5/stage/ on Windows (built by round5/stage.py)
# The variant's data dir in the mirror is data_r5_<name>: symlinks to data_r4 (the frozen round-4 tables) with the
# six staged tables copied over. Lean output is copied back to Windows round5/out/<name>/.
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
N=$1; REF=$2
[ -d $W/round5/stage/$N ] || { echo "no stage $N"; exit 2; }
bash $W/wsl/sync.sh code >/dev/null
( cd ~/caselaw2/lean-proofs && lake build LegalProofs.CaseLaw2.Run > ~/caselaw2/r5_build.log 2>&1 ) || { grep -A12 '^error' ~/caselaw2/r5_build.log | head -40; echo BUILD FAILED; exit 1; }
( cd $M/runner && lake build caselaw2 > ~/caselaw2/r5_build_runner.log 2>&1 ) || { tail -20 ~/caselaw2/r5_build_runner.log; echo RUNNER BUILD FAILED; exit 1; }
cd $M
D=data_r5_$N
rm -rf $D; mkdir -p $D
for f in data_r4/*.tsv; do ln -s ../$f $D/$(basename $f); done
for t in treatments treatment_witness treatment_class cert_text window_sha cite_index; do
  rm -f $D/$t.tsv
  [ -f $W/round5/stage/$N/$t.tsv ] && cp $W/round5/stage/$N/$t.tsv $D/$t.tsv
done
R=difftest/r5_$N
rm -rf $R; mkdir -p $R
if [ "$REF" = ref ]; then python3 $T/ref/precedent_ref.py run --data $D --edges ../lean-in-v3 --out $R/ref > $R/ref.log 2>&1 & fi
( time PAR=${PAR:-8} bash run_lean.sh 8 $D ../lean-in-v3 $R/lean ) > $R/lean.log 2>&1
tail -4 $R/lean.log | head -2
wait
grep -h 'class_rows\|class_bad_rows\|recognised_rows\|operative_rows\|rows_admitted\|bad_rows' $R/lean/summary.tsv | sort | uniq -c | sort -rn | head -12
if [ "$REF" = ref ]; then
  tail -2 $R/ref.log
  python3 $T/ref/diff.py $R/lean $R/ref --info --tsv $R/diff.tsv > $R/diff.txt 2>&1
  tail -30 $R/diff.txt
  mkdir -p $W/round5/out/$N && cp $R/diff.txt $W/round5/out/$N/ 2>/dev/null
fi
mkdir -p $W/round5/out/$N && cp $R/lean/*.tsv $W/round5/out/$N/
ls -la $W/round5/out/$N | head -12
echo "RUN $N done"
