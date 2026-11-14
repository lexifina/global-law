#!/bin/bash
# round 6 (lean agent): "no history_anchor.tsv, no change". Build everything, then run the new runner on
#   (a) the round-5 frozen build (round5/stage/final, assembled as r5_run.sh does) -> compare with round5/out/final
#   (b) the same data plus an EMPTY history_anchor.tsv                             -> compare with round5/out/final
#   (c) the round-4 tables (data_r4)                                               -> compare with difftest/real20/lean
# byte for byte, every output file (summary.tsv without its two timing lines).
#   usage: r6_lean_base.sh [a|b|c ...]   (default: a b c)
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
WHAT="${*:-a b c}"
bash $W/wsl/sync.sh code >/dev/null
cd ~/caselaw2/lean-proofs && lake build LegalProofs.CaseLaw2 LegalProofs.CaseLaw2.Run > ~/caselaw2/r6_build.log 2>&1 || { grep -A12 '^error' ~/caselaw2/r6_build.log | head -60; echo BUILD FAILED; exit 1; }
cd $M/runner && lake build caselaw2 > ~/caselaw2/r6_build_runner.log 2>&1 || { tail -30 ~/caselaw2/r6_build_runner.log; echo RUNNER BUILD FAILED; exit 1; }
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
assemble () {  # the round-5 frozen build, as wsl/r5_run.sh assembles it
  local D=$1 f t
  rm -rf $D; mkdir -p $D
  for f in data_r4/*.tsv; do ln -s ../$f $D/$(basename $f); done
  for t in treatments treatment_witness treatment_class cert_text window_sha cite_index; do
    rm -f $D/$t.tsv
    [ -f $W/round5/stage/final/$t.tsv ] && cp $W/round5/stage/final/$t.tsv $D/$t.tsv
    # the staged tables are the frozen ones (MANIFEST.txt)
    want=$(grep "^$t.tsv	" $W/round5/stage/final/MANIFEST.txt | sed 's/.*sha1 //')
    got=$(sha1sum < $D/$t.tsv | cut -d' ' -f1)
    [ "$want" = "$got" ] || { echo "MANIFEST MISMATCH $t"; rc=1; }
  done
  # the tables not staged are the round-4 ones: the two tables this round rewrites must equal the stage's
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
    a) assemble data_r6_base5
       [ -e data_r6_base5/history_anchor.tsv ] && { echo "anchor table present"; exit 2; }
       run data_r6_base5 r6_base5
       compare $W/round5/out/final difftest/r6_base5/lean "(a) round-5 final, no anchor file:"
       compare difftest/r5_final/lean difftest/r6_base5/lean "(a') mirror r5_final:" | grep -c byte-identical ;;
    b) assemble data_r6_base5e
       : > data_r6_base5e/history_anchor.tsv
       run data_r6_base5e r6_base5e
       compare $W/round5/out/final difftest/r6_base5e/lean "(b) round-5 final, empty anchor file:" ;;
    c) [ -e data_r4/history_anchor.tsv ] && { echo "anchor table present in data_r4"; exit 2; }
       [ -e data_r4/treatment_class.tsv ] && { echo "class table present in data_r4"; exit 2; }
       run data_r4 r6_base4
       compare difftest/real20/lean difftest/r6_base4/lean "(c) round-4 tables:" ;;
  esac
done
echo "R6 BASE rc=$rc"
exit $rc
