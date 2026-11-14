#!/bin/bash
# round 2 verification with all cores. usage: r2_verify.sh regress <name> | sweep <seed> <rounds> <name>
export PATH="$HOME/.elan/bin:$PATH"
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
cd $M
case "$1" in
  regress) dirs=$(ls -d fixtures/regress/*/ | sed 's|/$||' | sed "s|^|$M/|" | paste -sd,)
           python3 $T/ref/drt.py --dirs "$dirs" --out $M/difftest/$2 --jobs 24 --batches 24 > difftest/$2.txt 2>&1; tail -25 difftest/$2.txt ;;
  sweep)   python3 $T/ref/drt.py --seed $2 --rounds $3 --out $M/difftest/$4 --jobs 24 --batches 24 > difftest/$4.txt 2>&1; tail -40 difftest/$4.txt ;;
esac
