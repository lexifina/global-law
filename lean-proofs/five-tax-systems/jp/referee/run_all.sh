#!/bin/bash
# Referee A, all profiles, after the exact 住民税 dividend-credit fix (2026-11-18 ~05:10).
cd ~/cmp/jp/referee
R=../runs
for spec in "wage 1" "wage 2" "wage 3" "wage 4" "wage 5" "wage 6" "wage 7" "full 11" "full 12" "full 13" "full 14" "full 15" "full 99" "rich 21" "rich 22" "rich 23"; do
  set -- $spec
  [ -f $R/hh_$1_$2.jsonl ] || python3 -I gen_households.py 10000 $2 $1 > $R/hh_$1_$2.jsonl
  ../lean/.lake/build/bin/jptax $R/hh_$1_$2.jsonl > $R/lean_$1_$2.jsonl
  python3 -I nta_referee.py $R/hh_$1_$2.jsonl > $R/ref_$1_$2.jsonl
  echo "== $1 seed $2"; python3 -I compare_full.py $R/hh_$1_$2.jsonl $R/lean_$1_$2.jsonl $R/ref_$1_$2.jsonl
done
echo DONE
