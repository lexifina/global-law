#!/bin/bash
# round 13 (lead; = wsl/r12_run.sh with base round12/stage/v12a (mirror base_r13_v12a from data_r12_v12a), frozen round-11 binary s51; a held r12 slot counts against the two): run the Lean
# runner (and optionally the Python reference + diff) on a staged variant.
#   usage: r13_run.sh <name> [ref]    <name> = folder under round13/stage/ on Windows (built by round13/stage13.py)
#   from Windows: MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r13_run.sh <name> [ref]'
#   NOBUILD=1 r13_run.sh <name>        no sync, no build: runs the FROZEN round-11 checker
#                                      ~/caselaw2/r13_bin/caselaw2_r11v11d (a hard link to, or copy of,
#                                      ~/caselaw2/r11_bin/caselaw2_lean11_s51, the binary of the round-11 frozen run v11d
#                                      (round12/out/v12a/RUN.txt), sha1 a1cc4296022b1bd07401cc64b04e50449d0de9b3;
#                                      checked before each run). Allowed without LEAN_READY.
#   R13BIN=<path> NOBUILD=1 r13_run.sh selects another binary (copied aside to ~/caselaw2/r13_bin/run_<name> first).
#   (no NOBUILD)                       refuses unless round13/LEAN_READY exists; syncs the code (wsl/sync.sh code),
#                                      builds LegalProofs.CaseLaw2.Run and the runner under ~/caselaw2/r6_build.lock,
#                                      copies the new runner to ~/caselaw2/r13_bin/caselaw2_<name> and runs that copy.
#   ref                                also runs the Python reference (tools/caselaw2/ref/precedent_ref.py of the
#                                      synced tree) on the same data dir and diffs it, in difftest/r13_<name>/
#                                      (ref/, ref.log, diff.txt, diff.tsv); diff.txt is copied to round13/out/<name>/.
# Disk: prints `df -h /mnt/c` first and refuses (exit 5) when C: has under 8 GB free (WSL's disk lives on C:).
# Machine-wide limit: at most TWO runs at once, round-11 and round-13 together (flock slots ~/caselaw2/r13_slot1.lock,
# r13_slot2.lock; a held ~/caselaw2/r11_slot*.lock counts against the two; a run that finds no room prints that it
# waits and polls every 10 s). One run per variant name at a time (~/caselaw2/r13_name_<name>.lock; a second run of
# the same name is refused, exit 4).
# Base mirror: base_r13_v12a/ in the mirror = round12/stage/v12a (its *.tsv), built once from the round-11 data dir
# data_r12_v12a (a hard link to the real file behind each of its regular files and symlinks: no table is copied; the
# few v11d files that data dir lacks, decisions2_nodes.tsv and nodes_map.tsv, are copied from Windows) and checked
# file by file with cmp against Windows round12/stage/v12a (marker .verified, sha1 of every table in .sha1). The
# variant's data dir is data_r13_<name>: symlinks to base_r13_v12a (except decisions2_nodes.tsv / nodes_map.tsv,
# which are not runner tables), and every table listed in round13/stage/<name>/TABLES.txt put over it: a table whose
# sha1 equals the base mirror's is a symlink to the mirror, any other is copied from Windows; an EMPTY
# history_anchor / history_claim / joined or extra table is left out (earlier-round mode). Lean output goes to
# Windows round13/out/<name>/ (+ RUN.txt). Same runner call as wsl/r11_run.sh (asOf 20261112, 8 shards).
# Node count: round13/stage/<name>/nodes.count (stage13 always writes or links it; v11d's is 6,893,499), else
# ../graph/nodes.count. A stage built with --nodes DIR lists decisions2 in TABLES.txt (how = nodes) and has
# decisions2_nodes.tsv: the data dir's decisions2.tsv is then the first (nodes.count - rows of decisions2_nodes.tsv)
# lines of the mirror's decisions2 (= the corpus rows) + decisions2_nodes.tsv, sha1-checked against TABLES.txt
# (about 0.9 GB in WSL until r13_clean.sh). Without --nodes decisions2 is the mirror's (v11d's, with its 1,045 nodes).
export PATH="$HOME/.elan/toolchains/leanprover--lean4---v4.35.0/bin:$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
LP=~/caselaw2/lean-proofs
FROZEN=~/caselaw2/r13_bin/caselaw2_r11v11d
FROZEN_SRC=~/caselaw2/r11_bin/caselaw2_lean11_s51
FROZEN_SHA=a1cc4296022b1bd07401cc64b04e50449d0de9b3
N=$1; REF=$2
S=$W/round13/stage/$N
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] && [ -d "$S" ] || { echo "no stage $N"; exit 2; }
B=$M/base_r13_v12a
WB=$W/round12/stage/v12a
# ---- disk (C: also holds the WSL disk): refuse under 8 GB free
df -h /mnt/c
AVAIL_KB=$(df -Pk /mnt/c | awk 'NR==2{print $4}')
[ -n "$AVAIL_KB" ] && [ "$AVAIL_KB" -ge $((8*1024*1024)) ] || { echo "refused: C: has under 8 GB free ($((${AVAIL_KB:-0}/1024/1024)) GB); nothing run; tell the lead"; exit 5; }
# ---- one run per variant name (its data dir and difftest dir are its own)
exec 6> ~/caselaw2/r13_name_$N.lock
flock -n 6 || { echo "refused: a run of $N is already active (data_r13_$N / difftest/r13_$N are in use)"; exit 4; }
# ---- a run slot (two machine-wide)
# round 12: a held round-11 slot counts against the two (r11_run.sh runs may still be active)
held () { [ -e "$1" ] && ! flock -n "$1" true 2>/dev/null; }
SLOT=; waited=
while :; do
  for s in 1 2; do
    exec 7> ~/caselaw2/r13_slot$s.lock
    if flock -n 7; then
      busy=0
      for o in ~/caselaw2/r12_slot1.lock ~/caselaw2/r12_slot2.lock ~/caselaw2/r13_slot$((3-s)).lock; do
        held $o && busy=$((busy+1))
      done
      if [ $busy -le 1 ]; then SLOT=$s; break 2; fi
      exec 7>&-
    fi
  done
  exec 7>&-
  [ -z "$waited" ] && { echo "two runs (round 11 / round 12) are active: $N waits for a run slot ($(date '+%T'))"; waited=1; }
  sleep 10
done
echo "$N: run slot $SLOT${waited:+ (after waiting, $(date '+%T'))}"
# ---- the base mirror (once)
exec 8> ~/caselaw2/r13_base.lock
flock 8
if [ ! -f $B/.verified ]; then
  [ -d $M/data_r12_v12a ] || { echo "no $M/data_r12_v12a to build the base mirror from"; exit 2; }
  echo "building the base mirror $B from data_r12_v12a (hard links)"
  rm -rf $B.tmp; mkdir -p $B.tmp
  for f in $WB/*.tsv; do
    b=$(basename $f); m=$M/data_r12_v12a/$b
    if [ -e $m ] && cmp -s $m $f; then
      ln "$(realpath $m)" $B.tmp/$b 2>/dev/null || ln -s "$(realpath $m)" $B.tmp/$b
    else
      echo "  $b: not in data_r12_v12a or different; copied from Windows"; cp $f $B.tmp/$b
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
mkdir -p ~/caselaw2/r13_bin
if [ "$NOBUILD" = 1 ]; then
  if [ -n "$R13BIN" ]; then
    [ -x "$R13BIN" ] || { echo "no runner binary at $R13BIN"; exit 2; }
    EXE=~/caselaw2/r13_bin/run_$N
    cp "$R13BIN" $EXE
    HOW="NOBUILD R13BIN=$R13BIN"
  else
    EXE=$FROZEN
    if [ ! -x $EXE ] && [ -x $FROZEN_SRC ] && [ "$(sha1sum < $FROZEN_SRC | cut -c1-40)" = $FROZEN_SHA ]; then
      ln $FROZEN_SRC $EXE 2>/dev/null || { cp $FROZEN_SRC $EXE.tmp && mv $EXE.tmp $EXE; }
    fi
    [ -x $EXE ] || { echo "no frozen runner at $EXE"; exit 2; }
    [ "$(sha1sum < $EXE | cut -c1-40)" = $FROZEN_SHA ] || { echo "frozen runner $EXE does not hash to $FROZEN_SHA"; exit 2; }
    HOW="NOBUILD frozen r11v11d"
  fi
  echo "$HOW: runner $(sha1sum < $EXE | cut -c1-12) (no sync, no build)"
else
  [ -f $W/round13/LEAN_READY ] || { echo "round13/LEAN_READY is missing: the Lean tree is being edited; nothing synced, built or run (NOBUILD=1 runs the frozen round-11 binary)"; exit 3; }
  exec 9> ~/caselaw2/r6_build.lock
  flock 9
  bash $W/wsl/sync.sh code >/dev/null
  ( cd $LP && lake build LegalProofs.CaseLaw2.Run > ~/caselaw2/r13_build.log 2>&1 ) || { grep -A12 '^error' ~/caselaw2/r13_build.log | head -40; echo BUILD FAILED; exit 1; }
  ( cd $M/runner && lake build caselaw2 > ~/caselaw2/r13_build_runner.log 2>&1 ) || { tail -20 ~/caselaw2/r13_build_runner.log; echo RUNNER BUILD FAILED; exit 1; }
  EXE=~/caselaw2/r13_bin/caselaw2_$N
  cp $M/runner/.lake/build/bin/caselaw2 $EXE
  flock -u 9
  HOW="built"
  echo "built: runner $(sha1sum < $EXE | cut -c1-12)"
fi
# ---- the variant's data dir
cd $M
D=data_r13_$N
rm -rf $D; mkdir -p $D
for f in $B/*.tsv; do
  case $(basename $f) in decisions2_nodes.tsv|nodes_map.tsv) continue ;; esac  # stage files, not runner tables
  ln -s "$(realpath $f)" $D/$(basename $f)
done
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
  how=$(awk -F'\t' -v t=$t '$1==t{print $4}' $S/TABLES.txt 2>/dev/null | tr -d '\r')
  if [ "$t" = decisions2 ] && [ "$how" = nodes ] && [ -s $S/decisions2_nodes.tsv ] && [ -n "$want" ]; then
    # round 11 (DESIGN13 section 4, stage13.py --nodes): decisions2 = the base mirror's file + the order-node rows,
    # built here (no 915 MB copy over /mnt/c) and checked against the sha1 TABLES.txt records
    # round 12: the mirror's decisions2 is v11d's (corpus + its 1,045 nodes): take its corpus rows only
    NC=$(tr -d ' \r\n' < $S/nodes.count); NN=$(wc -l < $S/decisions2_nodes.tsv | tr -d ' ')
    [[ "$NC" =~ ^[0-9]+$ ]] && [ "$NC" -gt "$NN" ] || { echo "bad nodes.count / decisions2_nodes.tsv in $S"; exit 2; }
    { head -n $((NC - NN)) $B/decisions2.tsv; cat $S/decisions2_nodes.tsv; } > $D/decisions2.tsv
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
R=difftest/r13_$N
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
echo "history verdicts, round-13 rows (h13:):"
awk -F'\t' '$1=="history" && $2 ~ /^h13:/{c[$3]++} END{for(k in c) print c[k] "\t" k}' $R/lean/certs.tsv | sort -rn | head -20
echo "treatment verdicts, round-13 rows (t13:):"
awk -F'\t' '$1=="treatment" && $2 ~ /^t13:/{c[$3]++} END{for(k in c) print c[k] "\t" k}' $R/lean/certs.tsv | sort -rn | head -20
mkdir -p $W/round13/out/$N
rm -f $W/round13/out/$N/*.tsv $W/round13/out/$N/diff.txt
if [ "$REF" = ref ]; then
  tail -2 $R/ref.log
  python3 $T/ref/diff.py $R/lean $R/ref --info --tsv $R/diff.tsv > $R/diff.txt 2>&1
  tail -30 $R/diff.txt
  cp $R/diff.txt $W/round13/out/$N/ 2>/dev/null
fi
cp $R/lean/*.tsv $W/round13/out/$N/
cp $R/lean.log $W/round13/out/$N/lean.log
{ echo "$HOW run, binary sha1 $(sha1sum < $EXE | cut -c1-40), $(date '+%F %T %Z'), slot $SLOT"
  echo "stage round13/stage/$N; data dir $D; staged = base mirror:${linked:- none}; copied:${copied:- none}; left out:${left:- none}"; } > $W/round13/out/$N/RUN.txt
ls -la $W/round13/out/$N | head -16
echo "RUN $N done"
