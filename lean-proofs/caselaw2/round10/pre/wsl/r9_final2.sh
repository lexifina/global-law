#!/bin/bash
# round 9 (lean9 agent), batch 2 (DESIGN9 sections 5, 6, 7, 8): the final checks after the lock, with the four
# regressions as two parallel pairs beside the v8e reproduction (lead's Q5 answer, 02:56: at most 3 runs, PAR=4 each):
# build, keep the binary (~/caselaw2/r9_bin/caselaw2_lean9; section 4's kept as caselaw2_lean9_s4), audit check,
# the batch-2 fixture, the zone fixture, the round-8 and round-7 fixtures (copies that write nothing back), then in
# parallel: r7_lean_base.sh a a2 | r7_lean_base.sh b c | the v8e reproduction (stage lean9_base) vs round8/out/v8e.
#   usage: r9_final2.sh
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
L=~/caselaw2/r9_final2_logs
mkdir -p $L
rc=0
echo "== build $(date '+%T')"; bash $W/wsl/do.sh build | tail -3 || rc=1
mkdir -p ~/caselaw2/r9_bin
[ -f ~/caselaw2/r9_bin/caselaw2_lean9_s4 ] || cp ~/caselaw2/r9_bin/caselaw2_lean9 ~/caselaw2/r9_bin/caselaw2_lean9_s4
cp $M/runner/.lake/build/bin/caselaw2 ~/caselaw2/r9_bin/caselaw2_lean9
echo "binary sha1 $(sha1sum < ~/caselaw2/r9_bin/caselaw2_lean9 | cut -c1-40) (section 4: $(sha1sum < ~/caselaw2/r9_bin/caselaw2_lean9_s4 | cut -c1-12))"
echo "== audit check $(date '+%T')"; bash $W/wsl/do.sh audit check | head -3 || rc=1
echo "== round-9 batch-2 fixture $(date '+%T')"; bash $W/wsl/r9_farimplicit_fixture.sh | grep -v '^ *[0-9]* atRisk\|^t9:\|^id' || rc=1
echo "== round-9 zone fixture $(date '+%T')"; bash $W/wsl/r9_zone_fixture.sh | grep -v '^\[.\] classes\|^[<>-]\|^[0-9]' || rc=1
echo "== round-8 fixture $(date '+%T')"; bash $W/wsl/r9_r8fixture.sh || rc=1
echo "== round-7 fixture $(date '+%T')"; bash $W/wsl/r9_r7fixture.sh | tail -8 || rc=1
echo "== in parallel: regressions a a2 | b c | v8e reproduction (PAR=4 each) $(date '+%T')"
( PAR=4 bash $W/wsl/r7_lean_base.sh a a2 > $L/reg_a.log 2>&1; echo "rc=$?" >> $L/reg_a.log ) &
sleep 30
( PAR=4 bash $W/wsl/r7_lean_base.sh b c > $L/reg_b.log 2>&1; echo "rc=$?" >> $L/reg_b.log ) &
sleep 30
( PAR=4 NOBUILD=1 R9BIN=$HOME/caselaw2/r9_bin/caselaw2_lean9 bash $W/wsl/r9_run.sh lean9_base > $L/v8e.log 2>&1; echo "rc=$?" >> $L/v8e.log ) &
wait
for f in reg_a reg_b; do grep -v 'byte-identical\|^assembled\|^real\|^user\|^sys\|^$' $L/$f.log | head -20; echo "$f: $(grep -c byte-identical $L/$f.log) byte-identical files, $(tail -1 $L/$f.log)"; grep -q 'rc=0' $L/$f.log || rc=1; done
grep -q 'rc=0' $L/v8e.log || { tail -20 $L/v8e.log; rc=1; }
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
