#!/bin/bash
# round 11 (lean11): the gates after the lock, one Lean run at a time (DESIGN11 0.10): build, keep the binary
# (~/caselaw2/r11_bin/caselaw2_lean11), audit check, the round-11 tribunal fixture and the earlier fixtures (copies that
# write nothing into round10/ / round9/), then in turn: the regressions a a2 b c (r7_lean_base.sh) and the
# reproductions of round10/out/v10d, round9/out/v9c and round8/out/v8e (r11_repro.sh, a round-11 run slot each).
# Prints the sha1 of every CaseLaw2 source in the mirror before and after (nothing may change mid-gate).
#   usage: r11_final.sh [skipbuild]   (the binary is built into caselaw2_lean11_cand and promoted on FINAL rc=0)
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
LP=~/caselaw2/lean-proofs
L=~/caselaw2/r11_final_logs
mkdir -p $L ~/caselaw2/r11_bin
rc=0
srcsum () { (cd $LP && find LegalProofs/CaseLaw2 LegalProofs/CaseLaw2.lean tools/caselaw2/cues -type f -name '*.lean' -o -type f -name '*.json' -o -type f -name '*.py' | sort | xargs sha1sum; cd $M && sha1sum runner/*.lean audit/statements.lock) | sha1sum | cut -c1-40; }
avail=$(df --output=avail -BG /mnt/c | tail -1 | tr -dc 0-9); echo "C: free ${avail} GB $(date '+%T')"
[ "$avail" -ge 8 ] || { echo "C: under 8 GB: stop"; exit 5; }
if [ "$1" != skipbuild ]; then
  echo "== build $(date '+%T')"; bash $W/wsl/do.sh build | tail -3 || rc=1
fi
S0=$(srcsum); echo "mirror sources sha1 (after sync) $S0"
# the candidate binary; promoted to ~/caselaw2/r11_bin/caselaw2_lean11 only when every gate passed
cp $M/runner/.lake/build/bin/caselaw2 ~/caselaw2/r11_bin/caselaw2_lean11_cand
BIN=~/caselaw2/r11_bin/caselaw2_lean11_cand
echo "binary sha1 $(sha1sum < $BIN | cut -c1-40)"
echo "== audit check $(date '+%T')"; (cd $M && python3 audit/audit.py check | head -3) || rc=1
for fx in r11_identity_fixture r11_tribunal_fixture r11_r10tbridge_fixture r11_r10remand_fixture r10_r9farimplicit_fixture r10_r9zone_fixture r9_r8fixture r9_r7fixture; do
  echo "== $fx $(date '+%T')"
  bash $W/wsl/$fx.sh > $L/$fx.log 2>&1; frc=$?
  grep -v '^ *[0-9]* atRisk\|^t9:\|^id\|^\[.\] classes\|^[<>-]\|^[0-9]' $L/$fx.log | tail -12
  [ $frc = 0 ] && grep -q 'FIXTURE rc=0\|rc=0' $L/$fx.log || { echo "$fx FAILED (exit $frc)"; rc=1; }
done
for g in "a a2" "b c"; do
  avail=$(df --output=avail -BG /mnt/c | tail -1 | tr -dc 0-9); echo "== regressions $g $(date '+%T') (C: free ${avail} GB)"
  [ "$avail" -ge 8 ] || { echo "C: under 8 GB: stop"; exit 5; }
  f=reg_$(echo $g | tr -d ' ')
  PAR=8 bash $W/wsl/r7_lean_base.sh $g > $L/$f.log 2>&1; echo "rc=$?" >> $L/$f.log
  grep -v 'byte-identical\|^assembled\|^real\|^user\|^sys\|^$' $L/$f.log | head -20
  echo "$f: $(grep -c byte-identical $L/$f.log) byte-identical files, $(tail -1 $L/$f.log)"; grep -q 'rc=0' $L/$f.log || rc=1
done
for x in "v10d base_r11_v10d round10/out/v10d" "v9c base_r10_v9c round9/out/v9c" "v8e base_r9_v8e round8/out/v8e"; do
  set -- $x
  echo "== repro $1 $(date '+%T')"
  PAR=8 R11BIN=$BIN bash $W/wsl/r11_repro.sh $1 $2 $3 > $L/$1.log 2>&1
  cat $L/$1.log; grep -q "REPRO $1 rc=0" $L/$1.log || rc=1
done
S1=$(srcsum); echo "mirror sources sha1 (end) $S1"; [ "$S0" = "$S1" ] || { echo "MIRROR SOURCES CHANGED DURING THE GATES"; rc=1; }
if [ $rc = 0 ]; then cp $BIN ~/caselaw2/r11_bin/caselaw2_lean11; echo "promoted: ~/caselaw2/r11_bin/caselaw2_lean11 = $(sha1sum < ~/caselaw2/r11_bin/caselaw2_lean11 | cut -c1-40)"; fi
echo "FINAL rc=$rc $(date '+%T')"
exit $rc
