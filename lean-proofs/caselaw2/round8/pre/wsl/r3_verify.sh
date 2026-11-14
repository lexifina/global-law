#!/bin/bash
# round 3 verification with all cores.
# usage: r3_verify.sh failing <old sweep> <name>   re-run the universes of <old sweep> that disagreed (kept r<seed> dirs)
#        r3_verify.sh regress <name>                the regression set fixtures/regress/*
#        r3_verify.sh sweep <seed> <rounds> <name>  a fresh generated sweep
#        r3_verify.sh keep <sweep> <seed> <label>   copy a universe's data + edges into fixtures/regress/<label>
export PATH="$HOME/.elan/bin:$PATH"
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
cd $M
case "$1" in
  failing) dirs=$(ls -d difftest/$2/r*/ | sed 's|/$||' | sed "s|^|$M/|" | paste -sd,)
           python3 $T/ref/drt.py --dirs "$dirs" --out $M/difftest/$3 --jobs 24 --batches 8 > difftest/$3.txt 2>&1; tail -22 difftest/$3.txt ;;
  regress) dirs=$(ls -d fixtures/regress/*/ | sed 's|/$||' | sed "s|^|$M/|" | paste -sd,)
           python3 $T/ref/drt.py --dirs "$dirs" --out $M/difftest/$2 --jobs 24 --batches 24 > difftest/$2.txt 2>&1; tail -25 difftest/$2.txt ;;
  sweep)   python3 $T/ref/drt.py --seed $2 --rounds $3 --out $M/difftest/$4 --jobs 24 --batches 24 > difftest/$4.txt 2>&1; tail -40 difftest/$4.txt ;;
  keep)    mkdir -p fixtures/regress/$4 && cp -r difftest/$2/r$3/data difftest/$2/r$3/edges fixtures/regress/$4/ && ls fixtures/regress/$4 ;;
esac
