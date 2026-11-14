#!/bin/bash
# round 9: run the Lean runner (and optionally the Python reference + diff) on a staged variant.
#   usage: r9_run.sh <name> [ref]      <name> = folder under round9/stage/ on Windows (built by round9/stage9.py)
#   from Windows: MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r9_run.sh <name> [ref]'
#   NOBUILD=1 r9_run.sh <name>         no sync, no build: runs the FROZEN round-8 checker
#                                      ~/caselaw2/r9_bin/caselaw2_r8v8e (a copy of ~/caselaw2/r8_bin/caselaw2_lean8,
#                                      the binary of the round-8 frozen run v8e, sha1
#                                      3b8d3e4d45fb60a84c5cfb00c2f6729ebc2bfa6b; checked before each run), so a build
#                                      by `lean9` cannot change it mid-round. Allowed without LEAN_READY.
#   R9BIN=<path> NOBUILD=1 r9_run.sh   selects another binary (copied aside to ~/caselaw2/r9_bin/run_<name> first).
#   (no NOBUILD)                       refuses unless round9/LEAN_READY exists; syncs the code (wsl/sync.sh code),
#                                      builds LegalProofs.CaseLaw2.Run and the runner under ~/caselaw2/r6_build.lock,
#                                      copies the new runner to ~/caselaw2/r9_bin/caselaw2_<name> and runs that copy.
# Machine-wide limit: at most TWO round-9 runs at once (flock slots ~/caselaw2/r9_slot1.lock, r9_slot2.lock; a third
# run prints that it waits and polls every 10 s until a slot is free).
# Base mirror: base_r9_v8e/ in the mirror = round8/stage/v8e, built once from the round-8 mirror data_r8_v8e (hard
# links for its regular files, symlinks for its symlinks) and checked file by file with cmp against Windows
# round8/stage/v8e (incl. history_bridge; marker .verified, with the sha1 of every table in .sha1). The variant's data
# dir is data_r9_<name>: symlinks to base_r9_v8e, and every table listed in round9/stage/<name>/TABLES.txt (stage9.py:
# the ten staged tables + EXTRA_TABLES history_bridge, part_zone) put over it: a table whose sha1 equals the base
# mirror's is a symlink to the mirror, any other is copied from Windows; an EMPTY history_anchor / history_claim /
# joined or extra table (e.g. part_zone) is left out (the runner reads that as "no lines": earlier-round mode).
# Lean output goes to Windows round9/out/<name>/ (+ RUN.txt). Same runner call as wsl/r8_run.sh (asOf 20261112,
# 8 shards).
export PATH="$HOME/.elan/toolchains/leanprover--lean4---v4.35.0/bin:$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
LP=~/caselaw2/lean-proofs
FROZEN=~/caselaw2/r9_bin/caselaw2_r8v8e
FROZEN_SRC=~/caselaw2/r8_bin/caselaw2_lean8
FROZEN_SHA=3b8d3e4d45fb60a84c5cfb00c2f6729ebc2bfa6b
N=$1; REF=$2
S=$W/round9/stage/$N
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] && [ -d "$S" ] || { echo "no stage $N"; exit 2; }
B=$M/base_r9_v8e
WB=$W/round8/stage/v8e
# ---- a run slot (two machine-wide)
SLOT=; waited=
while :; do
  for s in 1 2; do
    exec 7> ~/caselaw2/r9_slot$s.lock
    if flock -n 7; then SLOT=$s; break 2; fi
  done
  exec 7>&-
  [ -z "$waited" ] && { echo "two round-9 runs are active: $N waits for a run slot ($(date '+%T'))"; waited=1; }
  sleep 10
done
echo "$N: run slot $SLOT${waited:+ (after waiting, $(date '+%T'))}"
# ---- the base mirror (once)
exec 8> ~/caselaw2/r9_base.lock
flock 8
if [ ! -f $B/.verified ]; then
  [ -d $M/data_r8_v8e ] || { echo "no $M/data_r8_v8e to build the base mirror from"; exit 2; }
  echo "building the base mirror $B"
  rm -rf $B.tmp; mkdir -p $B.tmp
  for f in $WB/*.tsv; do
    b=$(basename $f); m=$M/data_r8_v8e/$b
    if [ -e $m ] && cmp -s $m $f; then
      if [ -L $m ]; then ln -s "$(realpath $m)" $B.tmp/$b; else ln $m $B.tmp/$b 2>/dev/null || cp $m $B.tmp/$b; fi
    else
      echo "  $b: not in data_r8_v8e or different; copied from Windows"; cp $f $B.tmp/$b
    fi
  done
  for f in $WB/*.tsv; do cmp -s $f $B.tmp/$(basename $f) || { echo "base mirror check failed: $(basename $f)"; exit 1; }; done
  [ "$(ls $WB/*.tsv | wc -l)" = "$(ls $B.tmp/*.tsv | wc -l)" ] || { echo "base mirror: table count differs"; exit 1; }
  ( cd $B.tmp && for f in *.tsv; do printf '%s\t%s\n' "${f%.tsv}" "$(sha1sum < $f | cut -c1-40)"; done ) > $B.tmp/.sha1
  date > $B.tmp/.verified
  rm -rf $B; mv $B.tmp $B
  echo "base mirror built and checked: $(ls $B/*.tsv | wc -l) tables"
fi
flock -u 8
# ---- the binary (frozen, override, or build)
mkdir -p ~/caselaw2/r9_bin
if [ "$NOBUILD" = 1 ]; then
  if [ -n "$R9BIN" ]; then
    [ -x "$R9BIN" ] || { echo "no runner binary at $R9BIN"; exit 2; }
    EXE=~/caselaw2/r9_bin/run_$N
    cp "$R9BIN" $EXE
    HOW="NOBUILD R9BIN=$R9BIN"
  else
    EXE=$FROZEN
    if [ ! -x $EXE ] && [ -x $FROZEN_SRC ] && [ "$(sha1sum < $FROZEN_SRC | cut -c1-40)" = $FROZEN_SHA ]; then
      cp $FROZEN_SRC $EXE.tmp && mv $EXE.tmp $EXE
    fi
    [ -x $EXE ] || { echo "no frozen runner at $EXE"; exit 2; }
    [ "$(sha1sum < $EXE | cut -c1-40)" = $FROZEN_SHA ] || { echo "frozen runner $EXE does not hash to $FROZEN_SHA"; exit 2; }
    HOW="NOBUILD frozen r8v8e"
  fi
  echo "$HOW: runner $(sha1sum < $EXE | cut -c1-12) (no sync, no build)"
else
  [ -f $W/round9/LEAN_READY ] || { echo "round9/LEAN_READY is missing: the Lean tree is being edited; nothing synced, built or run (NOBUILD=1 runs the frozen round-8 binary)"; exit 3; }
  exec 9> ~/caselaw2/r6_build.lock
  flock 9
  bash $W/wsl/sync.sh code >/dev/null
  ( cd $LP && lake build LegalProofs.CaseLaw2.Run > ~/caselaw2/r9_build.log 2>&1 ) || { grep -A12 '^error' ~/caselaw2/r9_build.log | head -40; echo BUILD FAILED; exit 1; }
  ( cd $M/runner && lake build caselaw2 > ~/caselaw2/r9_build_runner.log 2>&1 ) || { tail -20 ~/caselaw2/r9_build_runner.log; echo RUNNER BUILD FAILED; exit 1; }
  EXE=~/caselaw2/r9_bin/caselaw2_$N
  cp $M/runner/.lake/build/bin/caselaw2 $EXE
  flock -u 9
  HOW="built"
  echo "built: runner $(sha1sum < $EXE | cut -c1-12)"
fi
# ---- the variant's data dir
cd $M
D=data_r9_$N
rm -rf $D; mkdir -p $D
for f in $B/*.tsv; do ln -s "$(realpath $f)" $D/$(basename $f); done
if [ -f $S/TABLES.txt ]; then
  TABLES=$(cut -f1 $S/TABLES.txt | tr -d '\r')
else
  TABLES="treatments treatment_witness treatment_class history history_anchor history_claim joined cert_text window_sha cite_index"
fi
linked=; copied=; left=
for t in $TABLES; do
  [[ "$t" =~ ^[a-z0-9_]+$ ]] || { echo "bad table name $t in TABLES.txt"; exit 2; }
  [ -e $S/$t.tsv ] || continue
  rm -f $D/$t.tsv
  case $t in
    treatments|treatment_witness|treatment_class|history|cert_text|window_sha|cite_index) keepempty=1 ;;
    *) keepempty= ;;
  esac
  if [ -z "$keepempty" ] && [ ! -s $S/$t.tsv ]; then left="$left $t"; continue; fi
  want=$(awk -F'\t' -v t=$t '$1==t{print $3}' $S/TABLES.txt 2>/dev/null | tr -d '\r')
  have=$(awk -F'\t' -v t=$t '$1==t{print $2}' $B/.sha1)
  if [ -n "$want" ] && [ "$want" = "$have" ] && [ -e $B/$t.tsv ]; then
    ln -s "$(realpath $B/$t.tsv)" $D/$t.tsv; linked="$linked $t"
  else
    cp $S/$t.tsv $D/$t.tsv; copied="$copied $t"
  fi
done
[ -e $D/history.tsv ] && [ -e $D/treatments.tsv ] || { echo "stage $N has no history.tsv / treatments.tsv"; exit 2; }
echo "data dir $D: $(ls $D | wc -l) tables; staged = base mirror:${linked:- none}; copied:${copied:- none}; left out (empty):${left:- none}"
R=difftest/r9_$N
rm -rf $R; mkdir -p $R
if [ "$REF" = ref ]; then python3 $T/ref/precedent_ref.py run --data $D --edges ../lean-in-v3 --out $R/ref > $R/ref.log 2>&1 & fi
# ---- the run: run_lean.sh's steps, with the binary chosen above (no lake call, so nothing is rebuilt mid-run)
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
( time run_direct $D $R/lean ) > $R/lean.log 2>&1
tail -4 $R/lean.log | head -2
wait
[ -f $R/lean/certs.tsv ] && grep -q LEANDONE $R/lean.log || { tail -20 $R/lean.log; echo "RUN $N FAILED"; exit 1; }
grep -h 'rows_admitted\|rows_rejected\|bad_rows\|anchor\|joined\|hclaim\|class_\|doctrine\|orderhead\|setaside\|bridge\|zone' $R/lean/summary.tsv | sort | uniq -c | sort -rn | head -30
echo "history verdicts, round-9 rows (h9:):"
awk -F'\t' '$1=="history" && $2 ~ /^h9:/{c[$3]++} END{for(k in c) print c[k] "\t" k}' $R/lean/certs.tsv | sort -rn | head -20
echo "treatment verdicts, round-9 rows (t9:):"
awk -F'\t' '$1=="treatment" && $2 ~ /^t9:/{c[$3]++} END{for(k in c) print c[k] "\t" k}' $R/lean/certs.tsv | sort -rn | head -20
mkdir -p $W/round9/out/$N
rm -f $W/round9/out/$N/*.tsv $W/round9/out/$N/diff.txt
if [ "$REF" = ref ]; then
  tail -2 $R/ref.log
  python3 $T/ref/diff.py $R/lean $R/ref --info --tsv $R/diff.tsv > $R/diff.txt 2>&1
  tail -30 $R/diff.txt
  cp $R/diff.txt $W/round9/out/$N/ 2>/dev/null
fi
cp $R/lean/*.tsv $W/round9/out/$N/
cp $R/lean.log $W/round9/out/$N/lean.log
{ echo "$HOW run, binary sha1 $(sha1sum < $EXE | cut -c1-40), $(date '+%F %T %Z'), slot $SLOT"
  echo "stage round9/stage/$N; data dir $D; staged = base mirror:${linked:- none}; copied:${copied:- none}; left out:${left:- none}"; } > $W/round9/out/$N/RUN.txt
ls -la $W/round9/out/$N | head -16
echo "RUN $N done"
