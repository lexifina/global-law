#!/bin/bash
# round 9 (lean9 agent): the final checks after the lock: build, keep the binary (~/caselaw2/r9_bin/caselaw2_lean9),
# audit check, the round-9 zone fixture, the round-8 and round-7 fixtures (copies that write nothing back), the
# round-4/5/6 regressions (r7_lean_base.sh a a2 b c), and the round-8 v8e reproduction with the new binary
# (r9_run.sh on stage round9/stage/lean9_base = hard links to round9/stage/base, R9BIN) compared with round8/out/v8e.
#   usage: r9_final.sh [skipbase]
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
rc=0
echo "== build $(date '+%T')"; bash $W/wsl/do.sh build | tail -3 || rc=1
mkdir -p ~/caselaw2/r9_bin
cp $M/runner/.lake/build/bin/caselaw2 ~/caselaw2/r9_bin/caselaw2_lean9
echo "binary sha1 $(sha1sum < ~/caselaw2/r9_bin/caselaw2_lean9 | cut -c1-40)"
echo "== audit check $(date '+%T')"; bash $W/wsl/do.sh audit check | head -3 || rc=1
echo "== round-9 zone fixture $(date '+%T')"; bash $W/wsl/r9_zone_fixture.sh | grep -v '^\[.\] classes\|^[<>-]\|^[0-9]' || rc=1
echo "== round-8 fixture $(date '+%T')"; bash $W/wsl/r9_r8fixture.sh || rc=1
echo "== round-7 fixture $(date '+%T')"; bash $W/wsl/r9_r7fixture.sh | tail -8 || rc=1
if [ "$1" != skipbase ]; then
  echo "== regressions a a2 b c $(date '+%T')"; bash $W/wsl/r7_lean_base.sh a a2 b c || rc=1
fi
echo "== v8e reproduction $(date '+%T')"
NOBUILD=1 R9BIN=$HOME/caselaw2/r9_bin/caselaw2_lean9 bash $W/wsl/r9_run.sh lean9_base > ~/caselaw2/r9_lean9_base.log 2>&1 || { tail -20 ~/caselaw2/r9_lean9_base.log; rc=1; }
head -3 ~/caselaw2/r9_lean9_base.log
E=$W/round8/out/v8e; G=$W/round9/out/lean9_base
for f in $(cd $E && ls *.tsv); do
  if [ ! -f $G/$f ]; then echo "v8e MISSING $f"; rc=1
  elif [ $f = summary.tsv ]; then
    if cmp -s <(grep -v '_ms	' $E/$f) <(grep -v '_ms	' $G/$f); then echo "v8e byte-identical $f (timing lines aside)"
    else echo "v8e DIFFERENT $f"; rc=1; diff <(grep -v '_ms	' $E/$f) <(grep -v '_ms	' $G/$f) | head; fi
  elif cmp -s $E/$f $G/$f; then echo "v8e byte-identical $f $(wc -l < $G/$f) lines $(sha1sum < $G/$f | cut -c1-12)"
  else echo "v8e DIFFERENT $f"; rc=1; fi
done
for f in $(cd $G && ls *.tsv); do [ -f $E/$f ] || { echo "v8e EXTRA $f"; rc=1; }; done
echo "FINAL rc=$rc $(date '+%T')"
exit $rc
