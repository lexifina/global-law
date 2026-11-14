#!/bin/bash
# round 5: Lean vs Python reference on generated universes (round-5 generator: witness rows, class claims) and on the
# regression set.   usage: r5_drt.sh [seed] [rounds] [tag]
export PATH="$HOME/.elan/bin:$PATH"
W=/mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
SEED=${1:-65000}; ROUNDS=${2:-300}; TAG=${3:-a}
bash $W/wsl/sync.sh code >/dev/null
( cd ~/caselaw2/lean-proofs && lake build LegalProofs.CaseLaw2.Run > ~/caselaw2/r5_build.log 2>&1 ) || { grep -A12 '^error' ~/caselaw2/r5_build.log | head -40; echo BUILD FAILED; exit 1; }
( cd $M/runner && lake build caselaw2 > ~/caselaw2/r5_build_runner.log 2>&1 ) || { tail -20 ~/caselaw2/r5_build_runner.log; echo RUNNER BUILD FAILED; exit 1; }
cd $M
rm -rf difftest/r5_regress_$TAG difftest/r5_drt_$TAG
( dirs=$(ls -d fixtures/regress/*/ | sed 's|/$||' | sed "s|^|$M/|" | paste -sd,)
  python3 $T/ref/drt.py --dirs "$dirs" --out $M/difftest/r5_regress_$TAG --jobs 8 --batches 8 > difftest/r5_regress_$TAG.txt 2>&1 ) &
python3 $T/ref/drt.py --seed $SEED --rounds $ROUNDS --out $M/difftest/r5_drt_$TAG --jobs 14 --batches 14 > difftest/r5_drt_$TAG.txt 2>&1
wait
echo "== regress"; tail -14 difftest/r5_regress_$TAG.txt
echo "== sweep seed $SEED rounds $ROUNDS"; tail -30 difftest/r5_drt_$TAG.txt
mkdir -p $W/difftest/wsl; cp difftest/r5_regress_$TAG.txt difftest/r5_drt_$TAG.txt $W/difftest/wsl/
echo "DRT $TAG done"
