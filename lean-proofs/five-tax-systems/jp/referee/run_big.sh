#!/bin/bash
# Large differential runs: referee A (NTA procedure) and referee B (OpenFisca-Japan) against jptax.
cd ~/cmp/jp/referee
R=../runs
for seed in 2 3 4 5 6 7; do
  python3 -I gen_households.py 10000 $seed > $R/hh_wage_$seed.jsonl
  ../lean/.lake/build/bin/jptax $R/hh_wage_$seed.jsonl > $R/lean_wage_$seed.jsonl
  python3 -I nta_referee.py $R/hh_wage_$seed.jsonl > $R/ref_wage_$seed.jsonl
  echo "== seed $seed (referee A)"; python3 -I compare.py $R/hh_wage_$seed.jsonl $R/lean_wage_$seed.jsonl $R/ref_wage_$seed.jsonl 4
done
for seed in 2 3; do
  echo "== seed $seed (OpenFisca-Japan, as is)"
  ./venv-ofjp/bin/python -I ofjp_compare.py $R/hh_wage_$seed.jsonl $R/lean_wage_$seed.jsonl | head -14
  echo "== seed $seed (OpenFisca-Japan, like for like)"
  ./venv-ofjp/bin/python -I ofjp_compare.py $R/hh_wage_$seed.jsonl $R/lean_wage_$seed.jsonl likeforlike | sed -n '1,13p;/by cause/,/^$/p;/均等割 differences by cause/,+3p'
done
echo DONE
