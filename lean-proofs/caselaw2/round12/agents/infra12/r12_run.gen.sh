#!/bin/bash
# round 11 (agent infra11; = wsl/r10_run.sh on round-12 paths, base v10d, frozen round-10 binary): run the Lean runner (and optionally the
# Python reference + diff) on a staged variant.
#   usage: r12_run.sh <name> [ref]    <name> = folder under round12/stage/ on Windows (built by round12/stage12.py)
#   from Windows: MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r12_run.sh <name> [ref]'
#   NOBUILD=1 r12_run.sh <name>        no sync, no build: runs the FROZEN round-10 checker
#                                      ~/caselaw2/r12_bin/caselaw2_r10v10d (a copy of ~/caselaw2/r10_bin/run_v10d, the
#                                      binary of the round-10 frozen run v10d (round11/out/v11d/RUN.txt),
#                                      sha1 e7e32592cc6c6393506e25dc9654d4254af218ea; checked before each run), so a
#                                      build by `lean11` cannot change it mid-round. Allowed without LEAN_READY.
#   R12BIN=<path> NOBUILD=1 r12_run.sh selects another binary (copied aside to ~/caselaw2/r12_bin/run_<name> first).
#   (no NOBUILD)                       refuses unless round12/LEAN_READY exists; syncs the code (wsl/sync.sh code),
#                                      builds LegalProofs.CaseLaw2.Run and the runner under ~/caselaw2/r6_build.lock,
#                                      copies the new runner to ~/caselaw2/r12_bin/caselaw2_<name> and runs that copy.
#   ref                                also runs the Python reference (tools/caselaw2/ref/precedent_ref.py of the
#                                      synced tree) on the same data dir and diffs it (as r9_run.sh), in
#                                      difftest/r12_<name>/ (ref/, ref.log, diff.txt, diff.tsv); diff.txt is copied
#                                      to round12/out/<name>/.
# Disk: prints `df -h /mnt/c` first and refuses (exit 5) when C: has under 8 GB free (WSL's disk lives on C:).
# Machine-wide limit: at most TWO round-12 runs at once (flock slots ~/caselaw2/r12_slot1.lock, r12_slot2.lock; a
# third run prints that it waits and polls every 10 s until a slot is free). One run per variant name at a time
# (~/caselaw2/r12_name_<name>.lock; a second run of the same name is refused, exit 4): data_r12_<name> and
# difftest/r12_<name> belong to that name only (round 9 had a collision of two runs of one name).
# Base mirror: base_r12_v10d/ in the mirror = round11/stage/v11d, built once from the round-10 data dir data_r10_v10d
# (a hard link to the real file behind each of its regular files and symlinks: no table is copied, and the mirror
# does not depend on earlier data dirs staying) and checked file by file with cmp against Windows round11/stage/v11d
# (marker .verified, with the sha1 of every table in .sha1). The variant's data dir is data_r12_<name>: symlinks to
# base_r12_v10d, and every table listed in round12/stage/<name>/TABLES.txt (stage12.py: the ten staged tables +
# EXTRA_TABLES history_bridge, part_zone, history_remand, history_tbridge + adoption, succession) put over it: a table whose sha1
# equals the base mirror's is a symlink to the mirror, any other is copied from Windows; an EMPTY history_anchor /
# history_claim / joined or extra table (e.g. history_remand) is left out (the runner reads that as "no lines":
# earlier-round mode). Lean output goes to Windows round12/out/<name>/ (+ RUN.txt). Same runner call as
# wsl/r10_run.sh (asOf 20261112, 8 shards). Node count: round12/stage/<name>/nodes.count when present (a stage
# with DESIGN12 section-4 order nodes, stage12.py --nodes), else ../graph/nodes.count (the corpus's).
# Such a stage lists decisions2 in TABLES.txt (how = nodes) and has decisions2_nodes.tsv: the data dir's decisions2.tsv
# is then cat(base mirror decisions2, decisions2_nodes.tsv), sha1-checked (about 0.9 GB in WSL until r12_clean.sh).
export PATH="$HOME/.elan/toolchains/leanprover--lean4---v4.35.0/bin:$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
LP=~/caselaw2/lean-proofs
FROZEN=~/caselaw2/r12_bin/caselaw2_r10v10d
FROZEN_SRC=~/caselaw2/r10_bin/run_v10d
FROZEN_SHA=e7e32592cc6c6393506e25dc9654d4254af218ea
N=$1; REF=$2
S=$W/round12/stage/$N
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] && [ -d "$S" ] || { echo "no stage $N"; exit 2; }
B=$M/base_r12_v10d
WB=$W/round11/stage/v11d
# ---- disk (C: also holds the WSL disk): refuse under 8 GB free
df -h /mnt/c
AVAIL_KB=$(df -Pk /mnt/c | awk 'NR==2{print $4}')
[ -n "$AVAIL_KB" ] && [ "$AVAIL_KB" -ge $((8*1024*1024)) ] || { echo "refused: C: has under 8 GB free ($((${AVAIL_KB:-0}/1024/1024)) GB); nothing run; tell the lead"; exit 5; }
# ---- one run per variant name (its data dir and difftest dir are its own)
exec 6> ~/caselaw2/r12_name_$N.lock
flock -n 6 || { echo "refused: a run of $N is already active (data_r12_$N / difftest/r12_$N are in use)"; exit 4; }
# ---- a run slot (two machine-wide)
SLOT=; waited=
while :; do
  for s in 1 2; do
    exec 7> ~/caselaw2/r12_slot$s.lock
    if flock -n 7; then SLOT=$s; break 2; fi
  done
  exec 7>&-
  [ -z "$waited" ] && { echo "two round-12 runs are active: $N waits for a run slot ($(date '+%T'))"; waited=1; }
  sleep 10
done
echo "$N: run slot $SLOT${waited:+ (after waiting, $(date '+%T'))}"
# ---- the base mirror (once)
exec 8> ~/caselaw2/r12_base.lock
flock 8
if [ ! -f $B/.verified ]; then
  [ -d $M/data_r10_v10d ] || { echo "no $M/data_r10_v10d to build the base mirror from"; exit 2; }
  echo "building the base mirror $B from data_r10_v10d (hard links)"
  rm -rf $B.tmp; mkdir -p $B.tmp
  for f in $WB/*.tsv; do
    b=$(basename $f); m=$M/data_r10_v10d/$b
    if [ -e $m ] && cmp -s $m $f; then
      ln "$(realpath $m)" $B.tmp/$b 2>/dev/null || ln -s "$(realpath $m)" $B.tmp/$b
    else
      echo "  $b: not in data_r10_v10d or different; copied from Windows"; cp $f $B.tmp/$b
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
mkdir -p ~/caselaw2/r12_bin
if [ "$NOBUILD" = 1 ]; then
  if [ -n "$R12BIN" ]; then
    [ -x "$R12BIN" ] || { echo "no runner binary at $R12BIN"; exit 2; }
    EXE=~/caselaw2/r12_bin/run_$N
    cp "$R12BIN" $EXE
    HOW="NOBUILD R12BIN=$R12BIN"
  else
    EXE=$FROZEN
    if [ ! -x $EXE ] && [ -x $FROZEN_SRC ] && [ "$(sha1sum < $FROZEN_SRC | cut -c1-40)" = $FROZEN_SHA ]; then
      cp $FROZEN_SRC $EXE.tmp && mv $EXE.tmp $EXE
    fi
    [ -x $EXE ] || { echo "no frozen runner at $EXE"; exit 2; }
    [ "$(sha1sum < $EXE | cut -c1-40)" = $FROZEN_SHA ] || { echo "frozen runner $EXE does not hash to $FROZEN_SHA"; exit 2; }
    HOW="NOBUILD frozen r10v10d"
  fi
  echo "$HOW: runner $(sha1sum < $EXE | cut -c1-12) (no sync, no build)"
else
  [ -f $W/round12/LEAN_READY ] || { echo "round12/LEAN_READY is missing: the Lean tree is being edited; nothing synced, built or run (NOBUILD=1 runs the frozen round-10 binary)"; exit 3; }
  exec 9> ~/caselaw2/r6_build.lock
  flock 9
  bash $W/wsl/sync.sh code >/dev/null
  ( cd $LP && lake build LegalProofs.CaseLaw2.Run > ~/caselaw2/r12_build.log 2>&1 ) || { grep -A12 '^error' ~/caselaw2/r12_build.log | head -40; echo BUILD FAILED; exit 1; }
  ( cd $M/runner && lake build caselaw2 > ~/caselaw2/r12_build_runner.log 2>&1 ) || { tail -20 ~/caselaw2/r12_build_runner.log; echo RUNNER BUILD FAILED; exit 1; }
  EXE=~/caselaw2/r12_bin/caselaw2_$N
  cp $M/runner/.lake/build/bin/caselaw2 $EXE
  flock -u 9
  HOW="built"
  echo "built: runner $(sha1sum < $EXE | cut -c1-12)"
fi
# ---- the variant's data dir
cd $M
D=data_r12_$N
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
  if [ "$t" = decisions2 ] && [ -s $S/decisions2_nodes.tsv ] && [ -n "$want" ]; then
    # round 11 (DESIGN12 section 4, stage12.py --nodes): decisions2 = the base mirror's file + the order-node rows,
    # built here (no 915 MB copy over /mnt/c) and checked against the sha1 TABLES.txt records
    cat $B/decisions2.tsv $S/decisions2_nodes.tsv > $D/decisions2.tsv
    [ "$(sha1sum < $D/decisions2.tsv | cut -c1-40)" = "$want" ] || { echo "decisions2 (base mirror + decisions2_nodes.tsv) does not hash to TABLES.txt's sha1"; exit 2; }
    copied="$copied decisions2(base+$(wc -l < $S/decisions2_nodes.tsv | tr -d ' ')nodes)"; continue
  fi
  if [ -n "$want" ] && [ "$want" = "$have" ] && [ -e $B/$t.tsv ]; then
    ln -s "$(realpath $B/$t.tsv)" $D/$t.tsv; linked="$linked $t"
  else
    cp $S/$t.tsv $D/$t.tsv; copied="$copied $t"
  fi
done
[ -e $D/history.tsv ] && [ -e $D/treatments.tsv ] || { echo "stage $N has no history.tsv / treatments.tsv"; exit 2; }
echo "data dir $D: $(ls $D | wc -l) tables; staged = base mirror:${linked:- none}; copied:${copied:- none}; left out (empty):${left:- none}"
R=difftest/r12_$N
rm -rf $R; mkdir -p $R
if [ "$REF" = ref ]; then python3 $T/ref/precedent_ref.py run --data $D --edges ../lean-in-v3 --out $R/ref > $R/ref.log 2>&1 & fi
# ---- the run: run_lean.sh's steps, with the binary chosen above (no lake call, so nothing is rebuilt mid-run)
run_direct () {  # data out
  local DATA=$(realpath $1) EDGES=$(realpath ../lean-in-v3) OUT=$(mkdir -p $2 && realpath $2) NODES
  if [ -f $S/nodes.count ]; then NODES=$(tr -d ' \r\n' < $S/nodes.count); else NODES=$(tr -d ' \n' < ../graph/nodes.count); fi
  [[ "$NODES" =~ ^[0-9]+$ ]] || { echo "bad node count '$NODES'"; return 1; }
  echo "node count $NODES"
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
grep -h 'rows_admitted\|rows_rejected\|bad_rows\|anchor\|joined\|hclaim\|class_\|doctrine\|orderhead\|setaside\|bridge\|zone\|remand' $R/lean/summary.tsv | sort | uniq -c | sort -rn | head -30
echo "history verdicts, round-12 rows (h12:):"
awk -F'\t' '$1=="history" && $2 ~ /^h12:/{c[$3]++} END{for(k in c) print c[k] "\t" k}' $R/lean/certs.tsv | sort -rn | head -20
echo "treatment verdicts, round-12 rows (t12:):"
awk -F'\t' '$1=="treatment" && $2 ~ /^t12:/{c[$3]++} END{for(k in c) print c[k] "\t" k}' $R/lean/certs.tsv | sort -rn | head -20
mkdir -p $W/round12/out/$N
rm -f $W/round12/out/$N/*.tsv $W/round12/out/$N/diff.txt
if [ "$REF" = ref ]; then
  tail -2 $R/ref.log
  python3 $T/ref/diff.py $R/lean $R/ref --info --tsv $R/diff.tsv > $R/diff.txt 2>&1
  tail -30 $R/diff.txt
  cp $R/diff.txt $W/round12/out/$N/ 2>/dev/null
fi
cp $R/lean/*.tsv $W/round12/out/$N/
cp $R/lean.log $W/round12/out/$N/lean.log
{ echo "$HOW run, binary sha1 $(sha1sum < $EXE | cut -c1-40), $(date '+%F %T %Z'), slot $SLOT"
  echo "stage round12/stage/$N; data dir $D; staged = base mirror:${linked:- none}; copied:${copied:- none}; left out:${left:- none}"; } > $W/round12/out/$N/RUN.txt
ls -la $W/round12/out/$N | head -16
echo "RUN $N done"
