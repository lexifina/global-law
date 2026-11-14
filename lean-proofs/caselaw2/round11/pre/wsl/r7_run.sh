#!/bin/bash
# round 7: run the Lean runner (and optionally the Python reference + diff) on a staged variant.
#   usage: r7_run.sh <name> [ref]      <name> = folder under round7/stage/ on Windows (built by round7/stage7.py)
#   from Windows: MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r7_run.sh <name> [ref]'
#   NOBUILD=1 r7_run.sh <name>         no sync, no build: runs the runner binary already built in the mirror
#                                      (runner/.lake/build/bin/caselaw2, copied aside for the run) — the round-6
#                                      checker until the `lean` agent builds round 7. Allowed without LEAN_READY.
# Base mirror: base_r7_final2/ in the mirror = round6/history/stage/final2 (symlinks to the real files behind
# data_r6_final2 and copies of its staged tables; built once and checked file by file against Windows final2 with
# cmp; marker .verified). The variant's data dir is data_r7_<name>: symlinks to base_r7_final2 with every staged table
# of round7/stage/<name>/ copied over (treatments, treatment_witness, treatment_class, history, history_anchor,
# history_claim, joined, cert_text, window_sha, cite_index); an EMPTY history_anchor / history_claim / joined file is
# left out (the runner reads that as "no lines": round-6 mode). Lean output goes to Windows round7/out/<name>/.
# Without NOBUILD it refuses to sync or build while round7/LEAN_READY is missing (the Lean tree has one writer).
# Sync + build are serialised with ~/caselaw2/r6_build.lock (the same lock as r6_run.sh: one build at a time).
export PATH="$HOME/.elan/toolchains/leanprover--lean4---v4.35.0/bin:$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
LP=~/caselaw2/lean-proofs
N=$1; REF=$2
S=$W/round7/stage/$N
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] && [ -d "$S" ] || { echo "no stage $N"; exit 2; }
B=$M/base_r7_final2
WB=$W/round6/history/stage/final2
# ---- the base mirror (once)
exec 8> ~/caselaw2/r7_base.lock
flock 8
if [ ! -f $B/.verified ]; then
  [ -d $M/data_r6_final2 ] || { echo "no $M/data_r6_final2 to build the base mirror from (wsl/r6_run.sh final2)"; exit 2; }
  echo "building the base mirror $B"
  rm -rf $B.tmp; mkdir -p $B.tmp
  for f in $WB/*.tsv; do
    b=$(basename $f); m=$M/data_r6_final2/$b
    if [ -e $m ] && cmp -s $m $f; then
      if [ -L $m ]; then ln -s "$(realpath $m)" $B.tmp/$b; else cp $m $B.tmp/$b; fi
    else
      echo "  $b: not in data_r6_final2 or different; copied from Windows"; cp $f $B.tmp/$b
    fi
  done
  for f in $WB/*.tsv; do cmp -s $f $B.tmp/$(basename $f) || { echo "base mirror check failed: $(basename $f)"; exit 1; }; done
  date > $B.tmp/.verified
  rm -rf $B; mv $B.tmp $B
  echo "base mirror built and checked: $(ls $B/*.tsv | wc -l) tables"
fi
flock -u 8
# ---- build (or not)
if [ "$NOBUILD" = 1 ]; then
  SRC=$M/runner/.lake/build/bin/caselaw2
  [ -x $SRC ] || { echo "no runner binary at $SRC"; exit 2; }
  mkdir -p ~/caselaw2/r7_bin
  EXE=~/caselaw2/r7_bin/caselaw2_$N
  cp $SRC $EXE
  echo "NOBUILD: runner $(sha1sum < $EXE | cut -c1-12) built $(date -r $SRC '+%F %T') (no sync, no build)"
else
  [ -f $W/round7/LEAN_READY ] || { echo "round7/LEAN_READY is missing: the Lean tree is being edited; nothing synced, built or run (NOBUILD=1 runs the binary already built)"; exit 3; }
  exec 9> ~/caselaw2/r6_build.lock
  flock 9
  bash $W/wsl/sync.sh code >/dev/null
  ( cd $LP && lake build LegalProofs.CaseLaw2.Run > ~/caselaw2/r7_build.log 2>&1 ) || { grep -A12 '^error' ~/caselaw2/r7_build.log | head -40; echo BUILD FAILED; exit 1; }
  ( cd $M/runner && lake build caselaw2 > ~/caselaw2/r7_build_runner.log 2>&1 ) || { tail -20 ~/caselaw2/r7_build_runner.log; echo RUNNER BUILD FAILED; exit 1; }
  mkdir -p ~/caselaw2/r7_bin
  EXE=~/caselaw2/r7_bin/caselaw2_$N
  cp $M/runner/.lake/build/bin/caselaw2 $EXE
  flock -u 9
fi
# ---- the variant's data dir
cd $M
D=data_r7_$N
rm -rf $D; mkdir -p $D
for f in $B/*.tsv; do ln -s "$(realpath $f)" $D/$(basename $f); done
for t in treatments treatment_witness treatment_class history history_anchor history_claim joined cert_text window_sha cite_index; do
  [ -e $S/$t.tsv ] || continue
  rm -f $D/$t.tsv
  case $t in
    history_anchor|history_claim|joined) [ -s $S/$t.tsv ] && cp $S/$t.tsv $D/$t.tsv ;;
    *) cp $S/$t.tsv $D/$t.tsv ;;
  esac
done
[ -f $D/history.tsv ] && [ -f $D/treatments.tsv ] || { echo "stage $N has no history.tsv / treatments.tsv"; exit 2; }
echo "data dir $D: $(ls $D | wc -l) tables; copied: $(find $D -maxdepth 1 -type f -name '*.tsv' -printf '%f ' )"
R=difftest/r7_$N
rm -rf $R; mkdir -p $R
if [ "$REF" = ref ]; then python3 $T/ref/precedent_ref.py run --data $D --edges ../lean-in-v3 --out $R/ref > $R/ref.log 2>&1 & fi
# ---- the run: run_lean.sh's steps, with the binary copied above (no lake call, so nothing is rebuilt mid-run)
run_direct () {  # data out
  local DATA=$(realpath $1) EDGES=$(realpath ../lean-in-v3) OUT=$(mkdir -p $2 && realpath $2) NODES
  NODES=$(tr -d ' \n' < ../graph/nodes.count)
  ( cd $LP && rm -f "$OUT"/*.tsv && seq 0 7 | xargs -P ${PAR:-8} -I{} $EXE "$DATA" "$EDGES" {} 8 "$OUT" "$NODES" 20261112 ) || return 1
  merge () { { printf '%s\n' "$2"; cat "$OUT"/"$1"-*.tsv 2>/dev/null; } > "$OUT/$1.tsv"; }
  local OC=; [ -f "$DATA/treatment_class.tsv" ] && OC=$'\toclass'
  merge status  $'node\tissue\tholding\tfrom\tto\tstatus\tclass\tfirm\twitness_row\tactor\tpath'"$OC"
  merge findings $'finding\tciting\tcited\tissue\tdetail\tfirm\tpath'"$OC"
  merge certs   $'table\tid\tresult_all\tresult_firm'
  merge splits  $'kind	issue\tcourt1\tcourt2\tanswers1\tanswers2\tholdings1\tholdings2\tasOf\tfirm'
  merge status_lines $'node	issue	holding	from	to	status	class	firm	witness_row	actor	path	line'"$OC"
  if [ -n "$OC" ]; then merge classes $'id\tclass\tclaim\tverdict\tfield_limit\tdoctrine\twitness'; rm -f "$OUT"/classes-*.tsv; fi
  merge horty   $'family	court	verdict	cases	firm'
  cat "$OUT"/summary-*.tsv > "$OUT/summary.tsv"
  rm -f "$OUT"/status_lines-*.tsv "$OUT"/horty-*.tsv "$OUT"/status-*.tsv "$OUT"/findings-*.tsv "$OUT"/certs-*.tsv "$OUT"/splits-*.tsv "$OUT"/summary-*.tsv
  echo LEANDONE
}
if [ "$NOBUILD" = 1 ]; then
  ( time run_direct $D $R/lean ) > $R/lean.log 2>&1
else
  # the Lean agent's run_lean.sh (its lake build of the runner is a no-op after the build above)
  ( time PAR=${PAR:-8} bash run_lean.sh 8 $D ../lean-in-v3 $R/lean ) > $R/lean.log 2>&1
fi
tail -4 $R/lean.log | head -2
wait
[ -f $R/lean/certs.tsv ] && grep -q LEANDONE $R/lean.log || { tail -20 $R/lean.log; echo "RUN $N FAILED"; exit 1; }
grep -h 'rows_admitted\|rows_rejected\|bad_rows\|anchor\|joined\|hclaim\|class_\|doctrine\|orderhead\|setaside' $R/lean/summary.tsv | sort | uniq -c | sort -rn | head -24
echo "history verdicts, round-7 rows (h7:):"
awk -F'\t' '$1=="history" && $2 ~ /^h7:/{c[$3]++} END{for(k in c) print c[k] "\t" k}' $R/lean/certs.tsv | sort -rn | head -20
echo "treatment verdicts, round-7 rows (t7:):"
awk -F'\t' '$1=="treatment" && $2 ~ /^t7:/{c[$3]++} END{for(k in c) print c[k] "\t" k}' $R/lean/certs.tsv | sort -rn | head -20
mkdir -p $W/round7/out/$N
rm -f $W/round7/out/$N/*.tsv $W/round7/out/$N/diff.txt
if [ "$REF" = ref ]; then
  tail -2 $R/ref.log
  python3 $T/ref/diff.py $R/lean $R/ref --info --tsv $R/diff.tsv > $R/diff.txt 2>&1
  tail -30 $R/diff.txt
  cp $R/diff.txt $W/round7/out/$N/ 2>/dev/null
fi
cp $R/lean/*.tsv $W/round7/out/$N/
cp $R/lean.log $W/round7/out/$N/lean.log
[ "$NOBUILD" = 1 ] && echo "NOBUILD run (binary $(sha1sum < $EXE | cut -c1-12))" > $W/round7/out/$N/RUN.txt || echo "built run" > $W/round7/out/$N/RUN.txt
ls -la $W/round7/out/$N | head -14
echo "RUN $N done"
