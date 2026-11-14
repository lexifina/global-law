#!/bin/bash
# round-5 fuzz, inside WSL. The fuzzer and the Lean tree it runs are the snapshot ~/caselaw2/r5fuzz/lp (setup.sh).
#   bash .../round5/fuzz/run.sh sync                  copy the fuzz tools into the snapshot (no build)
#   bash .../round5/fuzz/run.sh all <n> <seed> <name> gen + Lean (dump, runner, round-4 runner) + reference + check
#   bash .../round5/fuzz/run.sh oracle <n> <seed> <name>   reference against the oracle only (no Lean)
#   bash .../round5/fuzz/run.sh directed              the hand-built cases
#   bash .../round5/fuzz/run.sh check <name>          check again
# Cases: ~/caselaw2/r5fuzz/cases/<name>; report.json and the printed summary are copied to round5/fuzz/out/<name>/.
export PATH="$HOME/.elan/bin:$PATH"
WIN=/mnt/c/Users/$USER/Documents
OUT=$WIN/us-caselaw-lean-work/caselaw-lean-2/round5/fuzz/out
S=~/caselaw2/r5fuzz
FZ=$S/lp/tools/caselaw2/fuzz
export FUZZ_W=$S/w FUZZ_LP4=$S/lp4
cmd=$1; shift
sync_tools () {
  rsync -a --exclude __pycache__ $WIN/global-law-lean/lean-proofs/tools/caselaw2/fuzz/ $S/lp/tools/caselaw2/fuzz/
  rsync -a --exclude __pycache__ $WIN/global-law-lean/lean-proofs/tools/caselaw2/fuzz/ $S/lp4/tools/caselaw2/fuzz/
  # (the reference, the cue table and the Lean sources are one snapshot: setup.sh refreshes them together)
}
keep () {  # name
  mkdir -p $OUT/$1
  cp $S/cases/$1/report.json $OUT/$1/ 2>/dev/null
  cp $S/cases/$1/check.txt $OUT/$1/ 2>/dev/null
  cp $S/cases/$1/dump_stderr.txt $OUT/$1/ 2>/dev/null
}
case "$cmd" in
  sync) sync_tools; echo SYNCED ;;
  all)  sync_tools; N=$1; SEED=$2; NAME=$3; D=$S/cases/$NAME
        python3 -X utf8 $FZ/fuzz5.py gen --n $N --seed $SEED --dir $D --jobs 12 || exit 1
        ( time python3 -X utf8 $FZ/fuzz5.py run --dir $D --jobs ${JOBS:-12} ) 2>&1 | tail -4
        python3 -X utf8 $FZ/fuzz5.py check --dir $D --jobs 12 > $D/check.txt 2>&1; tail -n +2 $D/check.txt | cut -c1-330
        keep $NAME ;;
  oracle) sync_tools; N=$1; SEED=$2; NAME=$3; D=$S/cases/$NAME
        python3 -X utf8 $FZ/fuzz5.py oracle --n $N --seed $SEED --dir $D --jobs 12 > $S/oracle_$NAME.txt 2>&1
        cp $S/oracle_$NAME.txt $D/check.txt; tail -n +2 $D/check.txt | cut -c1-330
        keep $NAME ;;
  directed) sync_tools; D=$S/cases/directed
        python3 -X utf8 $FZ/fuzz5.py directed --dir $D --jobs 8 > $S/directed.txt 2>&1
        cp $S/directed.txt $D/check.txt; tail -n +2 $D/check.txt | cut -c1-330
        keep directed ;;
  check) sync_tools; NAME=$1; D=$S/cases/$NAME
        python3 -X utf8 $FZ/fuzz5.py check --dir $D --jobs 12 > $D/check.txt 2>&1; tail -n +2 $D/check.txt | cut -c1-330
        keep $NAME ;;
  sh)   cd $S && bash -c "$*" ;;
  *) echo "usage: run.sh sync|all|oracle|directed|check|sh ..." >&2; exit 2 ;;
esac
