#!/bin/bash
# round 7 (lean agent): "no joined line, no claim, no doctrine line: no change". Build everything, then run the new
# runner on
#   (a)  the round-6 frozen build (round6/history/stage/final2, assembled as wsl/r6_run.sh does) -> round6/history/out/final2
#   (a2) the same data plus EMPTY joined.tsv and history_claim.tsv                              -> round6/history/out/final2
#   (b)  the round-5 frozen build (round5/stage/final, as wsl/r6_lean_base.sh assembles it)     -> round5/out/final
#   (c)  the round-4 tables (data_r4)                                                           -> difftest/real20/lean
# byte for byte, every output file (summary.tsv without its two timing lines).
#   usage: r7_lean_base.sh [a|a2|b|c ...]   (default: a a2 b c)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
S6=$W/round6/history/stage/final2
WHAT="${*:-a a2 b c}"
bash $W/wsl/sync.sh code >/dev/null
cd ~/caselaw2/lean-proofs && lake build LegalProofs.CaseLaw2 LegalProofs.CaseLaw2.Run > ~/caselaw2/r7_build.log 2>&1 || { grep -A12 '^error' ~/caselaw2/r7_build.log | head -60; echo BUILD FAILED; exit 1; }
cd $M/runner && lake build caselaw2 > ~/caselaw2/r7_build_runner.log 2>&1 || { tail -30 ~/caselaw2/r7_build_runner.log; echo RUNNER BUILD FAILED; exit 1; }
cd $M
rc=0
compare () {  # <expected dir> <got dir> <label>
  local E=$1 G=$2 L=$3 f
  for f in $(cd $E && ls *.tsv); do
    if [ ! -f $G/$f ]; then echo "$L MISSING $f"; rc=1; continue; fi
    if [ $f = summary.tsv ]; then
      if cmp -s <(grep -v '_ms	' $E/$f) <(grep -v '_ms	' $G/$f); then echo "$L byte-identical $f (timing lines aside) $(wc -l < $G/$f) lines"
      else echo "$L DIFFERENT $f"; rc=1; diff <(grep -v '_ms	' $E/$f) <(grep -v '_ms	' $G/$f) | head -8; fi
    elif cmp -s $E/$f $G/$f; then echo "$L byte-identical $f $(wc -l < $G/$f) lines $(sha1sum < $G/$f | cut -c1-12)"
    else echo "$L DIFFERENT $f"; rc=1; diff <(sort $E/$f) <(sort $G/$f) | head -8; fi
  done
  for f in $(cd $G && ls *.tsv); do [ -f $E/$f ] || { echo "$L EXTRA $f"; rc=1; }; done
}
assemble6 () {  # the round-6 frozen build, as wsl/r6_run.sh assembles it; every table checked against the stage
  local D=$1 f t
  rm -rf $D; mkdir -p $D
  for f in data_r5_final/*.tsv; do ln -s "$(realpath $f)" $D/$(basename $f); done
  for t in history history_anchor cert_text window_sha cite_index; do
    rm -f $D/$t.tsv
    [ -s $S6/$t.tsv ] && cp $S6/$t.tsv $D/$t.tsv
  done
  # the five staged tables: MANIFEST sha1; every other table of the stage: byte-equal to the mirror's
  for t in history history_anchor cert_text window_sha; do
    want=$(grep "^$t.tsv	" $S6/MANIFEST.txt | sed 's/.*sha1 //')
    got=$(sha1sum < $D/$t.tsv | cut -d' ' -f1)
    [ "$want" = "$got" ] || { echo "MANIFEST MISMATCH $t"; rc=1; }
  done
  for f in $(cd $S6 && ls *.tsv); do
    [ "${2:-check}" = check ] || break
    [ -e $D/$f ] || continue
    cmp -s $S6/$f $D/$f || { echo "STAGE/MIRROR MISMATCH $f"; rc=1; }
  done
  [ -e $D/joined.tsv ] || [ -e $D/history_claim.tsv ] && { echo "round-7 table present"; rc=1; }
  grep -q '	doctrine	' $D/treatment_class.tsv && { echo "doctrine class line present"; rc=1; }
  echo "assembled $D: $(ls $D | wc -l) tables (${2:-check})"
}
assemble5 () {  # the round-5 frozen build, as wsl/r6_lean_base.sh assembles it
  local D=$1 f t
  rm -rf $D; mkdir -p $D
  for f in data_r4/*.tsv; do ln -s ../$f $D/$(basename $f); done
  for t in treatments treatment_witness treatment_class cert_text window_sha cite_index; do
    rm -f $D/$t.tsv
    [ -f $W/round5/stage/final/$t.tsv ] && cp $W/round5/stage/final/$t.tsv $D/$t.tsv
    want=$(grep "^$t.tsv	" $W/round5/stage/final/MANIFEST.txt | sed 's/.*sha1 //')
    got=$(sha1sum < $D/$t.tsv | cut -d' ' -f1)
    [ "$want" = "$got" ] || { echo "MANIFEST MISMATCH $t"; rc=1; }
  done
  for t in history decisions2 courts2 holdings; do
    cmp -s $W/round5/stage/final/$t.tsv $D/$t.tsv || { echo "STAGE/MIRROR MISMATCH $t"; rc=1; }
  done
}
run () {  # <data dir> <out name>
  rm -rf difftest/$2; mkdir -p difftest/$2
  ( time PAR=${PAR:-8} bash run_lean.sh 8 $1 ../lean-in-v3 difftest/$2/lean ) > difftest/$2/lean.log 2>&1
  tail -4 difftest/$2/lean.log | head -2
}
for w in $WHAT; do
  case $w in
    a)  assemble6 data_r7_base6
        run data_r7_base6 r7_base6
        compare $W/round6/history/out/final2 difftest/r7_base6/lean "(a) round-6 final2, no round-7 table:" ;;
    a2) assemble6 data_r7_base6e nocheck   # the same tables as (a), already compared with the stage
        : > data_r7_base6e/joined.tsv; : > data_r7_base6e/history_claim.tsv
        run data_r7_base6e r7_base6e
        compare $W/round6/history/out/final2 difftest/r7_base6e/lean "(a2) round-6 final2, empty joined.tsv and history_claim.tsv:" ;;
    b)  assemble5 data_r7_base5
        run data_r7_base5 r7_base5
        compare $W/round5/out/final difftest/r7_base5/lean "(b) round-5 final:" ;;
    c)  [ -e data_r4/joined.tsv ] || [ -e data_r4/treatment_class.tsv ] || [ -e data_r4/history_anchor.tsv ] && { echo "a later table present in data_r4"; exit 2; }
        run data_r4 r7_base4
        compare difftest/real20/lean difftest/r7_base4/lean "(c) round-4 tables:" ;;
  esac
done
echo "R7 BASE rc=$rc"
exit $rc
