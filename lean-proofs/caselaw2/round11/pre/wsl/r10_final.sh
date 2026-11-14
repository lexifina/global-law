#!/bin/bash
# round 10 (lean10): the gates after the lock: build, keep the binary (~/caselaw2/r10_bin/caselaw2_lean10), audit
# check, the round-10 remand fixture, the round-9 / round-8 / round-7 fixtures (copies that write nothing back), then
# in parallel: the regressions a a2 | b c (r7_lean_base.sh, PAR=4) and the reproductions of round9/out/v9c and
# round8/out/v8e (r10_repro.sh, one run slot each in turn, PAR=4).
#   usage: r10_final.sh [skipbuild]
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
L=~/caselaw2/r10_final_logs
mkdir -p $L ~/caselaw2/r10_bin
rc=0
avail=$(df --output=avail -BG /mnt/c | tail -1 | tr -dc 0-9); echo "C: free ${avail} GB $(date '+%T')"
[ "$avail" -ge 8 ] || { echo "C: under 8 GB: stop"; exit 5; }
if [ "$1" != skipbuild ]; then
  echo "== build $(date '+%T')"; bash $W/wsl/do.sh build | tail -3 || rc=1
fi
cp $M/runner/.lake/build/bin/caselaw2 ~/caselaw2/r10_bin/caselaw2_lean10
BIN=~/caselaw2/r10_bin/caselaw2_lean10
echo "binary sha1 $(sha1sum < $BIN | cut -c1-40)"
echo "== audit check $(date '+%T')"; bash $W/wsl/do.sh audit check | head -3 || rc=1
for fx in r10_tbridge_fixture r10_remand_fixture r10_r9farimplicit_fixture r10_r9zone_fixture r9_r8fixture r9_r7fixture; do
  echo "== $fx $(date '+%T')"
  bash $W/wsl/$fx.sh > $L/$fx.log 2>&1; frc=$?
  grep -v '^ *[0-9]* atRisk\|^t9:\|^id\|^\[.\] classes\|^[<>-]\|^[0-9]' $L/$fx.log | tail -12
  [ $frc = 0 ] && grep -q 'FIXTURE rc=0\|rc=0' $L/$fx.log || { echo "$fx FAILED (exit $frc)"; rc=1; }
done
echo "== in parallel: regressions a a2 | b c (PAR=4) and the v9c / v8e reproductions (PAR=4) $(date '+%T')"
( PAR=4 bash $W/wsl/r7_lean_base.sh a a2 > $L/reg_a.log 2>&1; echo "rc=$?" >> $L/reg_a.log ) &
sleep 20
( PAR=4 bash $W/wsl/r7_lean_base.sh b c > $L/reg_b.log 2>&1; echo "rc=$?" >> $L/reg_b.log ) &
sleep 20
( PAR=4 R10BIN=$BIN bash $W/wsl/r10_repro.sh v9c base_r10_v9c round9/out/v9c > $L/v9c.log 2>&1
  PAR=4 R10BIN=$BIN bash $W/wsl/r10_repro.sh v8e base_r9_v8e round8/out/v8e > $L/v8e.log 2>&1 ) &
wait
for f in reg_a reg_b; do grep -v 'byte-identical\|^assembled\|^real\|^user\|^sys\|^$' $L/$f.log | head -20; echo "$f: $(grep -c byte-identical $L/$f.log) byte-identical files, $(tail -1 $L/$f.log)"; grep -q 'rc=0' $L/$f.log || rc=1; done
for f in v9c v8e; do cat $L/$f.log; grep -q "REPRO $f rc=0" $L/$f.log || rc=1; done
echo "FINAL rc=$rc $(date '+%T')"
exit $rc
