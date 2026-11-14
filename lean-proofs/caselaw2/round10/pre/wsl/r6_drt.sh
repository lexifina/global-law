#!/bin/bash
# round 6 (anchored history certificate): Lean runner against the Python reference on generated universes.
# Run INSIDE WSL Ubuntu:
#   MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r6_drt.sh <cmd> ...'
#
#   setup                          snapshot the Windows Lean tree, tools and runner into ~/caselaw2/r6ref and build
#                                  LegalProofs.CaseLaw2.Run there (refuses while round6/history/LEAN_READY is missing)
#   regress <tag>                  (a) the regression set fixtures/regress/* (no anchor table)
#   fixed <tag>                    (b) the kept round-6 universes round6/history/difftest/universes/*
#   sweep <tag> <seed> <rounds> [probe] [r5]
#                                  (b) fresh round-6 universes: make_r6.py gen, the reference's own self-check, the run
#   base <tag> <seed> <rounds>     the same seeds without the round-6 overlay (gen.py --no-r5), to tell an old
#                                  disagreement class from a round-6 one
#   emptyanchor <tag>              the Lean runner on the kept universes with history_anchor.tsv absent / zero bytes
#                                  / blank lines only: its outputs must be identical in the three
#   real <stage name | final>      (c) real data: round6/history/stage/<name> over the round-5 frozen tables
#   (sweep also takes fuzz=K: K byte-level mutations of history_anchor.tsv per universe)
#
# Everything runs in the snapshot ~/caselaw2/r6ref (its own .lake), so a build or a sync by another agent in the
# main mirror cannot change the code under a run. Summaries are copied to round6/history/difftest/results/<tag>.txt
# (+ .report.txt: disagreements by case), disagreeing universes to round6/history/difftest/fail/<tag>/.
export PATH="$HOME/.elan/bin:$PATH"
WIN=/mnt/c/Users/$USER/Documents
W=$WIN/us-caselaw-lean-work/caselaw-lean-2
H=$W/round6/history
S=~/caselaw2/r6ref
LP=$S/lp
export CASELAW2_REF=$LP/tools/caselaw2/ref
BATCH=$S/runner/RunBatch.lean
RES=$H/difftest/results
cmd=$1; shift
mkdir -p $S $RES

run_dirs () {   # tag root...
  local tag=$1; shift
  local roots=""; for r in "$@"; do roots="$roots --root $r"; done
  rm -rf $S/out/$tag; mkdir -p $S/out/$tag
  python3 -X utf8 $S/difftest/r6_drt_run.py $roots --out $S/out/$tag --batch $BATCH --jobs ${JOBS:-14} --batches ${BATCHES:-14} > $S/out/$tag.txt 2>&1
  echo "rc=$?" >> $S/out/$tag.txt
  python3 -X utf8 $S/difftest/make_r6.py report "$@" > $S/out/$tag.report.txt 2>&1
  cp $S/out/$tag.txt $RES/$tag.txt; cp $S/out/$tag.report.txt $RES/$tag.report.txt; cp $S/out/$tag/drt_diff.tsv $RES/$tag.diff.tsv 2>/dev/null
  # keep the disagreeing universes (data, edges, both outputs, diff.tsv) on Windows
  for r in "$@"; do for d in $r/*/; do
    if [ -s $d/diff.tsv ] || [ ! -f $d/lean/certs.tsv ]; then mkdir -p $H/difftest/fail/$tag; rsync -a --exclude 'ref_check' $d $H/difftest/fail/$tag/$(basename $d)/; fi
  done; done
  tail -n 40 $S/out/$tag.txt
  echo "--- by case"; head -60 $S/out/$tag.report.txt
}

case "$cmd" in
  setup)
    [ -f $H/LEAN_READY ] || { echo "round6/history/LEAN_READY is missing: nothing copied or built"; exit 3; }
    if [ ! -d $LP/.lake ]; then
      mkdir -p $LP
      # the main mirror's build products, copied once and only while no lake process runs there
      while pgrep -x lake >/dev/null; do sleep 5; done
      [ -d ~/caselaw2/lean-proofs/.lake ] && cp -a ~/caselaw2/lean-proofs/.lake $LP/.lake
    fi
    rsync -a --delete --exclude .lake --exclude data --exclude video --exclude __pycache__ $WIN/global-law-lean/lean-proofs/ $LP/
    mkdir -p $S/runner $S/difftest
    cp -p $W/runner/RunBatch.lean $S/runner/
    cp -p $H/difftest/*.py $S/difftest/
    ( cd $LP && lake build LegalProofs.CaseLaw2.Run > $S/build.log 2>&1 ); rc=$?
    grep -A12 '^error' $S/build.log | head -40
    ( cd $LP && sha1sum tools/caselaw2/ref/precedent_ref.py tools/caselaw2/cues/cue_table.json; find LegalProofs/CaseLaw2 -name '*.lean' | sort | xargs cat | sha1sum ) > $S/snapshot.sha1
    cat $S/snapshot.sha1; cp $S/snapshot.sha1 $RES/snapshot.sha1
    echo "SETUP rc=$rc $(date +%H:%M:%S)"; exit $rc ;;
  refsync)
    # copy only the reference (tools/caselaw2/ref) and the round-6 drivers into the snapshot; the Lean stays as built
    rsync -a --exclude __pycache__ $WIN/global-law-lean/lean-proofs/tools/caselaw2/ref/ $LP/tools/caselaw2/ref/
    cp -p $H/difftest/*.py $S/difftest/
    ( cd $LP && sha1sum tools/caselaw2/ref/precedent_ref.py tools/caselaw2/cues/cue_table.json; find LegalProofs/CaseLaw2 -name '*.lean' | sort | xargs cat | sha1sum ) | tee $RES/snapshot_refsync.sha1
    echo REFSYNC done ;;
  regress)
    tag=$1
    rm -rf $S/regress; mkdir -p $S/regress
    rsync -a --exclude out --exclude ref --exclude lean $W/fixtures/regress/ $S/regress/
    run_dirs $tag $S/regress ;;
  fixed)
    tag=$1
    rm -rf $S/fixed; mkdir -p $S/fixed
    rsync -a --exclude ref --exclude lean --exclude diff.tsv $H/difftest/universes/ $S/fixed/
    # the `lean` agent's own fixture, when there is one
    [ -d $H/fixtures/anchor/data ] && mkdir -p $S/fixed/lean-fixture-anchor && cp -r $H/fixtures/anchor/data $H/fixtures/anchor/edges $S/fixed/lean-fixture-anchor/
    run_dirs $tag $S/fixed ;;
  sweep)
    tag=$1; seed=$2; rounds=$3; shift 3
    flags=""; for f in "$@"; do flags="$flags --$f"; done
    rm -rf $S/sweep/$tag; mkdir -p $S/sweep/$tag
    python3 -X utf8 $S/difftest/make_r6.py gen --seed $seed --rounds $rounds --out $S/sweep/$tag $flags | tail -1
    python3 -X utf8 $S/difftest/make_r6.py check $S/sweep/$tag > $S/out/$tag.selfcheck.txt 2>&1; head -3 $S/out/$tag.selfcheck.txt | cut -c1-200; grep 'expectations checked' $S/out/$tag.selfcheck.txt
    cp $S/out/$tag.selfcheck.txt $RES/$tag.selfcheck.txt
    run_dirs $tag $S/sweep/$tag ;;
  base)
    tag=$1; seed=$2; rounds=$3
    rm -rf $S/out/$tag; mkdir -p $S/out/$tag
    python3 -X utf8 -c "
import sys, os
sys.path.insert(0, '$CASELAW2_REF')
import drt
drt.BATCH = '$BATCH'
sys.argv = ['drt.py', '--seed', '$seed', '--rounds', '$rounds', '--out', '$S/out/$tag', '--jobs', '14', '--batches', '14', '--no-r5']
drt.main()
" > $S/out/$tag.txt 2>&1
    cp $S/out/$tag.txt $RES/$tag.txt; tail -n 25 $S/out/$tag.txt ;;
  emptyanchor)
    tag=$1
    rm -rf $S/empty; mkdir -p $S/empty
    for d in $H/difftest/universes/u*/; do
      n=$(basename $d)
      for m in absent zero blank; do
        mkdir -p $S/empty/$n-$m; cp -r $d/data $d/edges $S/empty/$n-$m/
        rm -f $S/empty/$n-$m/data/history_anchor.tsv
        [ $m = zero ] && : > $S/empty/$n-$m/data/history_anchor.tsv
        [ $m = blank ] && printf '\n\r\n\n' > $S/empty/$n-$m/data/history_anchor.tsv
      done
    done
    run_dirs $tag $S/empty > /dev/null
    bad=0; tot=0
    for d in $S/empty/*-absent/; do
      b=${d%-absent/}
      for m in zero blank; do for f in $d/lean/*.tsv; do
        tot=$((tot+1))
        if [ "$(basename $f)" = summary.tsv ]; then cmp -s <(grep -v 'ms\b' $f) <(grep -v 'ms\b' $b-$m/lean/summary.tsv) || { bad=$((bad+1)); echo "DIFFERENT $(basename $b) $m summary.tsv"; diff <(grep -v 'ms\b' $f) <(grep -v 'ms\b' $b-$m/lean/summary.tsv) | head -6; }
        else cmp -s $f $b-$m/lean/$(basename $f) || { bad=$((bad+1)); echo "DIFFERENT $(basename $b) $m $(basename $f)"; }; fi
      done; done
    done
    echo "empty anchor table, Lean outputs: $tot files compared with the no-table run, $bad differ" | tee $RES/$tag.empty.txt
    tail -n 12 $S/out/$tag.txt ;;
  real)
    # (c) real data, in the snapshot: the compiled runner built here, the round-5 frozen tables of the main mirror
    # (data_r5_final, read through symlinks) with the staged round-6 tables of round6/history/stage/<name> copied
    # over; <name> = final runs the round-5 frozen tables alone. Nothing in the main mirror is written.
    name=$1
    C=$S/us-caselaw-lean-work/caselaw-lean-2
    M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
    [ "$name" = final ] || [ -d $H/stage/$name ] || { echo "no stage $name"; exit 2; }
    [ -d $M/data_r5_final ] || { echo "no $M/data_r5_final"; exit 2; }
    mkdir -p $C $S/global-law-lean $S/us-caselaw-lean-work/graph $S/real
    [ -e $S/global-law-lean/lean-proofs ] || ln -s ../lp $S/global-law-lean/lean-proofs
    [ -e $S/us-caselaw-lean-work/lean-in-v3 ] || ln -s ~/caselaw2/us-caselaw-lean-work/lean-in-v3 $S/us-caselaw-lean-work/lean-in-v3
    cp ~/caselaw2/us-caselaw-lean-work/graph/nodes.count $S/us-caselaw-lean-work/graph/
    rsync -a --exclude .lake $W/runner/ $C/runner/; cp -p $W/run_lean.sh $C/
    ( cd $C/runner && lake build caselaw2 > $S/build_runner.log 2>&1 ) || { tail -20 $S/build_runner.log; echo RUNNER BUILD FAILED; exit 1; }
    D=$C/data_r6_$name; rm -rf $D; mkdir -p $D
    for f in $M/data_r5_final/*.tsv; do ln -s "$(realpath $f)" $D/$(basename $f); done
    if [ "$name" != final ]; then
      for t in history history_anchor cert_text window_sha cite_index; do
        rm -f $D/$t.tsv; [ -s $H/stage/$name/$t.tsv ] && cp $H/stage/$name/$t.tsv $D/$t.tsv
      done
    fi
    R=$S/real/$name; rm -rf $R; mkdir -p $R
    python3 $CASELAW2_REF/precedent_ref.py run --data $D --edges $S/us-caselaw-lean-work/lean-in-v3 --out $R/ref > $R/ref.log 2>&1 &
    ( cd $C && time PAR=${PAR:-8} bash run_lean.sh 8 $D ../lean-in-v3 $R/lean ) > $R/lean.log 2>&1
    wait
    tail -4 $R/lean.log | head -2; tail -1 $R/ref.log
    [ -f $R/lean/certs.tsv ] || { tail -20 $R/lean.log; echo "REAL $name FAILED"; exit 1; }
    grep -h 'anchor' $R/lean/summary.tsv | sort | uniq -c | head; grep anchor $R/ref/ref_stats.tsv
    python3 $CASELAW2_REF/diff.py $R/lean $R/ref --info --tsv $R/diff.tsv > $R/diff.txt 2>&1
    cat $R/diff.txt | head -60
    cp $R/diff.txt $RES/real_$name.diff.txt; cp $R/diff.tsv $RES/real_$name.diff.tsv
    echo "REAL $name done" ;;
  *) echo "usage: r6_drt.sh setup | regress <tag> | fixed <tag> | sweep <tag> <seed> <rounds> [probe] [r5] [fuzz=K] | base <tag> <seed> <rounds> | emptyanchor <tag> | real <stage name | final>" >&2; exit 2 ;;
esac
