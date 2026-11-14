#!/bin/bash
# round 6 (same-case history): run the Lean runner (and optionally the Python reference + diff) on a staged variant.
#   usage: r6_run.sh <name> [ref]      <name> = folder under round6/history/stage/ on Windows (built by
#                                      round6/history/stage6.py)
#   from Windows: MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r6_run.sh <name> [ref]'
# The variant's data dir in the mirror is data_r6_<name>: symlinks to the files of data_r5_final (the frozen round-5
# build) with the five staged tables copied over (history, history_anchor, cert_text, window_sha, cite_index; an
# empty history_anchor.tsv is left out, which the runner reads as "no anchors"). Lean output is copied back to
# Windows round6/history/out/<name>/.
# It refuses to build while round6/history/LEAN_READY is missing (the Lean tree has one writer; a build in the
# middle of an edit would break).
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
N=$1; REF=$2
S=$W/round6/history/stage/$N
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] && [ -d "$S" ] || { echo "no stage $N"; exit 2; }
[ -f $W/round6/history/LEAN_READY ] || { echo "round6/history/LEAN_READY is missing: the Lean tree is being edited; nothing built or run"; exit 3; }
[ -d $M/data_r5_final ] || { echo "no $M/data_r5_final (the round-5 final mirror; wsl/r5_run.sh final)"; exit 2; }
cmp -s $M/data_r5_final/treatments.tsv $W/round5/stage/final/treatments.tsv || echo "WARNING: the mirror's data_r5_final/treatments.tsv differs from round5/stage/final"
# one build at a time (several agents may call this script)
exec 9> ~/caselaw2/r6_build.lock
flock 9
bash $W/wsl/sync.sh code >/dev/null
( cd ~/caselaw2/lean-proofs && lake build LegalProofs.CaseLaw2.Run > ~/caselaw2/r6_build.log 2>&1 ) || { grep -A12 '^error' ~/caselaw2/r6_build.log | head -40; echo BUILD FAILED; exit 1; }
( cd $M/runner && lake build caselaw2 > ~/caselaw2/r6_build_runner.log 2>&1 ) || { tail -20 ~/caselaw2/r6_build_runner.log; echo RUNNER BUILD FAILED; exit 1; }
flock -u 9
cd $M
D=data_r6_$N
rm -rf $D; mkdir -p $D
for f in data_r5_final/*.tsv; do ln -s "$(realpath $f)" $D/$(basename $f); done
for t in history history_anchor cert_text window_sha cite_index; do
  rm -f $D/$t.tsv
  [ -s $S/$t.tsv ] && cp $S/$t.tsv $D/$t.tsv
done
[ -f $D/history.tsv ] || { echo "stage $N has no history.tsv"; exit 2; }
R=difftest/r6_$N
rm -rf $R; mkdir -p $R
if [ "$REF" = ref ]; then python3 $T/ref/precedent_ref.py run --data $D --edges ../lean-in-v3 --out $R/ref > $R/ref.log 2>&1 & fi
( time PAR=${PAR:-8} bash run_lean.sh 8 $D ../lean-in-v3 $R/lean ) > $R/lean.log 2>&1
tail -4 $R/lean.log | head -2
wait
[ -f $R/lean/certs.tsv ] || { tail -20 $R/lean.log; echo "RUN $N FAILED"; exit 1; }
grep -h 'rows_admitted\|rows_rejected\|bad_rows\|anchor\|hist' $R/lean/summary.tsv | sort | uniq -c | sort -rn | head -12
echo "history verdicts, all rows:"
awk -F'\t' '$1=="history"{c[$3]++} END{for(k in c) print c[k] "\t" k}' $R/lean/certs.tsv | sort -rn | head -20
echo "history verdicts, round-6 rows (h6:):"
awk -F'\t' '$1=="history" && $2 ~ /^h6:/{c[$3]++} END{for(k in c) print c[k] "\t" k}' $R/lean/certs.tsv | sort -rn | head -20
mkdir -p $W/round6/history/out/$N
if [ "$REF" = ref ]; then
  tail -2 $R/ref.log
  python3 $T/ref/diff.py $R/lean $R/ref --info --tsv $R/diff.tsv > $R/diff.txt 2>&1
  tail -30 $R/diff.txt
  cp $R/diff.txt $W/round6/history/out/$N/ 2>/dev/null
fi
cp $R/lean/*.tsv $W/round6/history/out/$N/
ls -la $W/round6/history/out/$N | head -12
echo "RUN $N done"
