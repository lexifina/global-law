#!/bin/bash
# round 11 (lean11; copy of r10_repro.sh with round-11 run slots and names): reproduce a frozen Lean output with a given runner binary, writing nothing on Windows but a log.
#   usage: R11BIN=<binary> r11_repro.sh <label> <base mirror dir> <expected Windows out dir>
#     e.g. R11BIN=~/caselaw2/r11_bin/caselaw2_lean11 r11_repro.sh v9c base_r10_v9c round9/out/v9c
#          R11BIN=~/caselaw2/r11_bin/caselaw2_lean11 r11_repro.sh v8e base_r9_v8e round8/out/v8e
# The data dir data_r11_lean11_<label> is symlinks to the verified base mirror (round9/stage/v9c = base_r10_v9c,
# round8/stage/v8e = base_r9_v8e; built and checked by infra10 / lean9); an EMPTY optional table is left out as
# r9_run.sh / r10_run.sh do (treatments, treatment_witness, treatment_class, history, cert_text, window_sha,
# cite_index are kept even when empty). The run is run_direct of r9_run.sh (asOf 20261112, 8 shards). It holds one
# round-11 run slot (~/caselaw2/r11_slot{1,2}.lock). Every output table is compared with cmp against the expected
# dir (summary.tsv: timing lines aside); the WSL output and data dir are deleted afterwards (disk rule).
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
LP=~/caselaw2/lean-proofs
N=$1; B=$M/$2; E=$W/$3
[[ "$N" =~ ^[A-Za-z0-9_.-]+$ ]] && [ -f $B/.verified ] && [ -d $E ] || { echo "usage: r11_repro.sh <label> <base> <expected>"; exit 2; }
[ -x "$R11BIN" ] || { echo "no binary R11BIN=$R11BIN"; exit 2; }
avail=$(df --output=avail -BG /mnt/c | tail -1 | tr -dc 0-9); echo "C: free ${avail} GB"
[ "$avail" -ge 8 ] || { echo "C: under 8 GB: refusing"; exit 5; }
EXE=~/caselaw2/r11_bin/run_lean11_$N
cp "$R11BIN" $EXE
SLOT=; waited=
while :; do
  for s in 1 2; do
    exec 7> ~/caselaw2/r11_slot$s.lock
    if flock -n 7; then SLOT=$s; break 2; fi
  done
  exec 7>&-
  [ -z "$waited" ] && { echo "two round-11 runs are active: lean11_$N waits ($(date '+%T'))"; waited=1; }
  sleep 10
done
echo "lean11_$N: slot $SLOT, binary $(sha1sum < $EXE | cut -c1-40), $(date '+%T')"
cd $M
D=data_r11_lean11_$N
rm -rf $D; mkdir -p $D
left=
for f in $B/*.tsv; do
  t=$(basename $f .tsv)
  case $t in
    treatments|treatment_witness|treatment_class|history|cert_text|window_sha|cite_index) keep=1 ;;
    *) keep= ;;
  esac
  if [ -z "$keep" ] && [ ! -s $f ]; then left="$left $t"; continue; fi
  ln -s "$(realpath $f)" $D/$t.tsv
done
echo "data dir $D: $(ls $D | wc -l) tables; left out (empty):${left:- none}"
R=difftest/r11_lean11_$N
rm -rf $R; mkdir -p $R
DATA=$(realpath $D); EDGES=$(realpath ../lean-in-v3); OUT=$(mkdir -p $R/lean && realpath $R/lean)
NODES=$(tr -d ' \n' < ../graph/nodes.count)
t0=$(date +%s)
( cd $LP && seq 0 7 | xargs -P ${PAR:-8} -I{} $EXE "$DATA" "$EDGES" {} 8 "$OUT" "$NODES" 20261112 ) > $R/lean.log 2>&1 || { tail -20 $R/lean.log; echo "RUN FAILED"; exit 1; }
merge () { { printf '%s\n' "$2"; cat "$OUT"/"$1"-*.tsv 2>/dev/null; } > "$OUT/$1.tsv"; }
OC=; [ -f "$DATA/treatment_class.tsv" ] && OC=$'\toclass'
merge status  $'node\tissue\tholding\tfrom\tto\tstatus\tclass\tfirm\twitness_row\tactor\tpath'"$OC"
merge findings $'finding\tciting\tcited\tissue\tdetail\tfirm\tpath'"$OC"
merge certs   $'table\tid\tresult_all\tresult_firm'
merge splits  $'kind	issue\tcourt1\tcourt2\tanswers1\tanswers2\tholdings1\tholdings2\tasOf\tfirm'
merge status_lines $'node	issue	holding	from	to	status	class	firm	witness_row	actor	path	line'"$OC"
if [ -n "$OC" ]; then merge classes $'id\tclass\tclaim\tverdict\tfield_limit\tdoctrine\twitness'; rm -f "$OUT"/classes-*.tsv; fi
merge horty   $'family	court	verdict	cases	firm'
cat "$OUT"/summary-*.tsv > "$OUT/summary.tsv"
rm -f "$OUT"/status_lines-*.tsv "$OUT"/horty-*.tsv "$OUT"/status-*.tsv "$OUT"/findings-*.tsv "$OUT"/certs-*.tsv "$OUT"/splits-*.tsv "$OUT"/summary-*.tsv
echo "run done in $(( $(date +%s) - t0 )) s"
exec 7>&-
rc=0
for f in $(cd $E && ls *.tsv); do
  if [ ! -f $OUT/$f ]; then echo "$N MISSING $f"; rc=1
  elif [ $f = summary.tsv ]; then
    if cmp -s <(grep -v '_ms	' $E/$f) <(grep -v '_ms	' $OUT/$f); then echo "$N byte-identical $f (timing lines aside)"
    else echo "$N DIFFERENT $f"; rc=1; diff <(grep -v '_ms	' $E/$f) <(grep -v '_ms	' $OUT/$f) | head; fi
  elif cmp -s $E/$f $OUT/$f; then echo "$N byte-identical $f $(wc -l < $OUT/$f) lines $(sha1sum < $OUT/$f | cut -c1-12)"
  else echo "$N DIFFERENT $f"; rc=1; fi
done
for f in $(cd $OUT && ls *.tsv); do [ -f $E/$f ] || { echo "$N EXTRA $f"; rc=1; }; done
if [ $rc = 0 ]; then rm -rf $R $D $EXE; else echo "kept $M/$R for diagnosis"; fi
echo "REPRO $N rc=$rc $(date '+%T')"
exit $rc
