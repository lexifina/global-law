#!/bin/bash
# round 9 (part zones DESIGN9 §4, later sections by INBOX): the round-9 Lean runner against the Python reference.
# (copy of round8/agents/ref8/difftest8.sh with the round-9 generator.) Run INSIDE WSL Ubuntu:
#   MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/round9/agents/ref9/difftest9.sh <cmd> ...'
#
#   setup                     snapshot the Windows Lean tree (with the reference and the cue table), the batch runner
#                             and the drivers into ~/caselaw2/r9ref and build LegalProofs.CaseLaw2.Run there
#                             (refuses while round9/LEAN_READY is missing)
#   refsync                   copy only the reference and the drivers into the snapshot (the Lean stays as built)
#   regress <tag>             the 435 earlier universes + 9 round-8 kept + 90 round-8 sweep universes (copied from
#                             ~/caselaw2/r8ref), both engines rerun with round-9 code, no round-9 table
#   kept <tag>                the kept round-9 universes round9/agents/ref9/universes/*
#   sweep <tag> <seed> <rounds> [probe|fuzz=K]
#                             fresh round-9 universes: make_r9.py gen, the reference's self-check, the run
#   all                       setup + regress + kept + three sweeps (main, probe, fuzz)
# Summaries: round9/agents/ref9/results/<tag>.txt (+ .report.txt by case, .selfcheck.txt); disagreeing universes:
# round9/agents/ref9/fail/<tag>/.
export PATH="$HOME/.elan/toolchains/leanprover--lean4---v4.35.0/bin:$HOME/.elan/bin:$PATH"
WIN=/mnt/c/Users/$USER/Documents
W=$WIN/us-caselaw-lean-work/caselaw-lean-2
ME=$W/round9/agents/ref9
S=~/caselaw2/r9ref
LP=$S/lp
R8=~/caselaw2/r8ref
export CASELAW2_REF=$LP/tools/caselaw2/ref PYTHONDONTWRITEBYTECODE=1 MAKE_R7_DIR=$S/drivers MAKE_R8_DIR=$S/drivers
BATCH=$S/runner/RunBatch.lean
RES=$ME/results
cmd=$1; shift
mkdir -p $S/out $RES

run_dirs () {   # tag root...
  local tag=$1; shift
  local roots=""; for r in "$@"; do roots="$roots --root $r"; done
  [ -d $LP/.lake ] || { echo "no build in $LP: run setup first"; exit 3; }
  rm -rf $S/out/$tag; mkdir -p $S/out/$tag
  python3 -X utf8 $S/drivers/r7_drt_run.py $roots --out $S/out/$tag --batch $BATCH --jobs ${JOBS:-10} --batches ${BATCHES:-10} > $S/out/$tag.txt 2>&1
  echo "rc=$?" >> $S/out/$tag.txt
  python3 -X utf8 $S/drivers/make_r9.py report "$@" > $S/out/$tag.report.txt 2>&1
  cp $S/out/$tag.txt $RES/$tag.txt; cp $S/out/$tag.report.txt $RES/$tag.report.txt
  cp $S/out/$tag/drt_diff.tsv $RES/$tag.diff.tsv 2>/dev/null
  for r in "$@"; do for d in $r/*/; do
    if [ -s $d/diff.tsv ] || [ ! -f $d/lean/certs.tsv ]; then
      mkdir -p $ME/fail/$tag; rsync -a --exclude 'ref_check' $d $ME/fail/$tag/$(basename $d)/
    fi
  done; done
  tail -n 45 $S/out/$tag.txt
  echo "--- by case"; head -80 $S/out/$tag.report.txt
}

sync_drivers () {
  mkdir -p $S/drivers $S/runner
  cp -p $W/round7/agents/ref/r7_drt_run.py $W/round7/agents/ref/make_r7.py $W/round8/agents/ref8/make_r8.py $ME/make_r9.py $ME/check_regress9.py $S/drivers/
}

case "$cmd" in
  setup)
    [ -f $W/round9/LEAN_READY ] || { echo "round9/LEAN_READY is missing: nothing copied or built"; exit 3; }
    if [ ! -d $LP/.lake ]; then
      mkdir -p $LP
      while pgrep -x lake >/dev/null; do sleep 5; done
      [ -d ~/caselaw2/lean-proofs/.lake ] && cp -a ~/caselaw2/lean-proofs/.lake $LP/.lake
    fi
    rsync -a --delete --exclude .lake --exclude data --exclude video --exclude __pycache__ $WIN/global-law-lean/lean-proofs/ $LP/
    sync_drivers
    cp -p $W/runner/RunBatch.lean $S/runner/
    ( cd $LP && lake build LegalProofs.CaseLaw2.Run > $S/build.log 2>&1 ); rc=$?
    grep -A12 '^error' $S/build.log | head -40
    ( cd $LP && sha1sum tools/caselaw2/ref/precedent_ref.py tools/caselaw2/ref/diff.py tools/caselaw2/cues/cue_table.json; find LegalProofs/CaseLaw2 -name '*.lean' | sort | xargs cat | sha1sum ) > $S/snapshot.sha1
    cat $S/snapshot.sha1; cp $S/snapshot.sha1 $RES/snapshot.sha1
    echo "SETUP rc=$rc $(date +%H:%M:%S)"; exit $rc ;;
  refsync)
    rsync -a --delete --exclude __pycache__ $WIN/global-law-lean/lean-proofs/tools/caselaw2/ref/ $LP/tools/caselaw2/ref/
    rsync -a --delete $WIN/global-law-lean/lean-proofs/tools/caselaw2/cues/ $LP/tools/caselaw2/cues/
    sync_drivers
    ( cd $LP && sha1sum tools/caselaw2/ref/precedent_ref.py tools/caselaw2/ref/diff.py tools/caselaw2/cues/cue_table.json; find LegalProofs/CaseLaw2 -name '*.lean' | sort | xargs cat | sha1sum ) | tee $RES/snapshot_refsync.sha1
    echo REFSYNC done ;;
  regress)
    tag=$1
    rm -rf $S/regress; mkdir -p $S/regress
    for src in regress/regress_regress regress/regress_fixed regress/regress_sweep_r6sw2 regress/regress_sweep_r6sw2p                regress/regress_sweep_r6sw2f regress/kept regress/sweep_r7sw3 regress/sweep_r7sw3p regress/sweep_r7sw3n                regress/sweep_r7sw3f kept sweep/r8sw1 sweep/r8sw1p sweep/r8sw1f; do
      n=$(echo $src | tr / _); mkdir -p $S/regress/$n
      rsync -a --exclude out --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $R8/$src/ $S/regress/$n/
    done
    run_dirs $tag $S/regress/* ;;
  kept)
    tag=$1
    rm -rf $S/kept; mkdir -p $S/kept
    rsync -a --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $ME/universes/ $S/kept/
    run_dirs $tag $S/kept ;;
  sweep)
    tag=$1; seed=$2; rounds=$3; shift 3
    flags=""; for f in "$@"; do flags="$flags --$f"; done
    flags=$(echo "$flags" | sed 's/--fuzz=/--fuzz /')
    sync_drivers
    rm -rf $S/sweep/$tag; mkdir -p $S/sweep/$tag
    python3 -X utf8 $S/drivers/make_r9.py gen --seed $seed --rounds $rounds --out $S/sweep/$tag $flags | tail -1
    python3 -X utf8 $S/drivers/make_r9.py check $S/sweep/$tag > $S/out/$tag.selfcheck.txt 2>&1
    grep -v '^  ' $S/out/$tag.selfcheck.txt | tail -5
    cp $S/out/$tag.selfcheck.txt $RES/$tag.selfcheck.txt
    run_dirs $tag $S/sweep/$tag ;;
  dirs)
    tag=$1; root=$2
    rm -rf $S/dirs/$tag; mkdir -p $S/dirs/$tag
    rsync -a --exclude ref --exclude lean --exclude diff.tsv --exclude ref_check $root/ $S/dirs/$tag/
    run_dirs $tag $S/dirs/$tag ;;
  all)
    bash $0 setup || exit $?
    bash $0 kept r9kept1
    bash $0 sweep r9sw1 94000 40
    bash $0 sweep r9sw1p 95000 20 probe
    bash $0 sweep r9sw1f 96000 30 fuzz=8
    bash $0 regress r9reg1
    echo "ALL done $(date +%H:%M)"; grep -H 'universes,' $RES/r9*.txt ;;
  *) echo "usage: difftest8.sh setup | refsync | regress <tag> | kept <tag> | sweep <tag> <seed> <rounds> [probe|fuzz=K] | dirs <tag> <root> | all" >&2; exit 2 ;;
esac
