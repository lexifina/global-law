#!/bin/bash
# Pending verification (DIFFTEST.md §7), run inside the WSL mirror. usage: verify.sh fixtures|regress|sweep|fuzz|real [name]
export PATH="$HOME/.elan/bin:$PATH"
M=~/caselaw2/us-caselaw-lean-work/caselaw-lean-2
T=~/caselaw2/lean-proofs/tools/caselaw2
cd $M
case "$1" in
  fixtures) bash run_lean.sh 2 fixtures/data fixtures/edges fixtures/out > difftest/fixtures.log 2>&1
            python3 $T/ref/precedent_ref.py run --data fixtures/data --edges fixtures/edges --out fixtures/ref_out >> difftest/fixtures.log 2>&1
            python3 $T/ref/diff.py fixtures/out fixtures/ref_out --info > difftest/fixtures_diff.txt 2>&1; tail -15 difftest/fixtures_diff.txt; cat fixtures/out/summary.tsv | grep -i "horty\|bad" ; grep -i horty fixtures/out/findings.tsv ;;
  regress)  dirs=$(ls -d fixtures/regress/*/ | sed 's|/$||' | sed "s|^|$M/|" | paste -sd,)
            python3 $T/ref/drt.py --dirs "$dirs" --out $M/difftest/${2:-regress5} --jobs 6 --batches 6 > difftest/${2:-regress5}.txt 2>&1; tail -25 difftest/${2:-regress5}.txt ;;
  sweep)    python3 $T/ref/drt.py --seed ${2:-51000} --rounds ${3:-1000} --out $M/difftest/${4:-drt5k} --jobs 8 --batches 8 > difftest/${4:-drt5k}.txt 2>&1; tail -40 difftest/${4:-drt5k}.txt ;;
  fuzz)     # regenerate the 5,000 cases (seed 7) inside WSL, then dump + round trip + runner + reference, then check
            rm -rf ~/caselaw2/fz/s7
            python3 -X utf8 $T/fuzz/fuzz.py gen --n 5000 --seed 7 --dir ~/caselaw2/fz/s7 > difftest/fuzz_gen.txt 2>&1
            python3 -X utf8 $T/fuzz/fuzz.py run --dir ~/caselaw2/fz/s7 --jobs ${2:-12} > difftest/fuzz_run.txt 2>&1
            python3 -X utf8 $T/fuzz/fuzz.py check --dir ~/caselaw2/fz/s7 > difftest/fuzz_check.txt 2>&1; tail -60 difftest/fuzz_check.txt ;;
  real)     R=difftest/${2:-real14}; mkdir -p $R
            ( time PAR=8 bash run_lean.sh 8 data ../lean-in-v3 $R/lean ) > $R/lean.log 2>&1
            [ -d $R/ref ] || python3 $T/ref/precedent_ref.py run --data data --edges ../lean-in-v3 --out $R/ref > $R/ref.log 2>&1
            python3 $T/ref/diff.py $R/lean $R/ref --info --tsv $R/diff.tsv > $R/diff.txt 2>&1
            python3 $T/ref/real_report.py $R --sample 100 > $R/report.log 2>&1
            tail -5 $R/lean.log; tail -40 $R/diff.txt ;;
esac
