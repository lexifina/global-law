#!/bin/bash
# round 8 (lean8 agent): the final checks after the lock: build, audit check, the round-8 fixture, the round-7
# fixture, the round-4/5/6 regressions (r7_lean_base.sh a a2 b c), and the round-7 v3 reproduction with the new
# binary (r8_run.sh on stage lean8_v3 = a hard-linked copy of round8/stage/base) compared with round7/out/v3.
#   usage: r8_final.sh [skipbase]
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
rc=0
echo "== build $(date '+%T')"; bash $W/wsl/do.sh build | tail -3 || rc=1
mkdir -p ~/caselaw2/r8_bin
cp $M/runner/.lake/build/bin/caselaw2 ~/caselaw2/r8_bin/caselaw2_lean8
echo "binary sha1 $(sha1sum < ~/caselaw2/r8_bin/caselaw2_lean8 | cut -c1-40)"
echo "== audit check $(date '+%T')"; bash $W/wsl/do.sh audit check | head -3 || rc=1
echo "== round-8 fixture $(date '+%T')"; bash $W/wsl/r8_bridge_fixture.sh || rc=1
echo "== round-7 fixture $(date '+%T')"; bash $W/wsl/r7_joined_fixture.sh | tail -8 || rc=1
if [ "$1" != skipbase ]; then
  echo "== regressions a a2 b c $(date '+%T')"; bash $W/wsl/r7_lean_base.sh a a2 b c || rc=1
fi
echo "== v3 reproduction $(date '+%T')"
NOBUILD=1 R8BIN=$HOME/caselaw2/r8_bin/caselaw2_lean8 bash $W/wsl/r8_run.sh lean8_v3 > ~/caselaw2/r8_lean8_v3.log 2>&1 || { tail -20 ~/caselaw2/r8_lean8_v3.log; rc=1; }
head -3 ~/caselaw2/r8_lean8_v3.log
E=$W/round7/out/v3; G=$W/round8/out/lean8_v3
for f in $(cd $E && ls *.tsv); do
  if [ ! -f $G/$f ]; then echo "v3 MISSING $f"; rc=1
  elif [ $f = summary.tsv ]; then
    if cmp -s <(grep -v '_ms	' $E/$f) <(grep -v '_ms	' $G/$f); then echo "v3 byte-identical $f (timing lines aside)"
    else echo "v3 DIFFERENT $f"; rc=1; diff <(grep -v '_ms	' $E/$f) <(grep -v '_ms	' $G/$f) | head; fi
  elif cmp -s $E/$f $G/$f; then echo "v3 byte-identical $f $(wc -l < $G/$f) lines $(sha1sum < $G/$f | cut -c1-12)"
  else echo "v3 DIFFERENT $f"; rc=1; fi
done
for f in $(cd $G && ls *.tsv); do [ -f $E/$f ] || { echo "v3 EXTRA $f"; rc=1; }; done
echo "FINAL rc=$rc $(date '+%T')"
exit $rc
