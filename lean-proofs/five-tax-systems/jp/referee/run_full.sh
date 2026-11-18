#!/bin/bash
# Referee A on the full and rich profiles (all contract fields).
cd ~/cmp/jp/referee
R=../runs
for spec in "full 11" "full 12" "full 13" "full 14" "full 15" "rich 21" "rich 22"; do
  set -- $spec
  python3 -I gen_households.py 10000 $2 $1 > $R/hh_$1_$2.jsonl
  ../lean/.lake/build/bin/jptax $R/hh_$1_$2.jsonl > $R/lean_$1_$2.jsonl
  python3 -I nta_referee.py $R/hh_$1_$2.jsonl > $R/ref_$1_$2.jsonl
  echo "== $1 seed $2"; python3 -I compare_full.py $R/hh_$1_$2.jsonl $R/lean_$1_$2.jsonl $R/ref_$1_$2.jsonl
done
python3 -I - <<'P'
import json
n=0; m=0
for seed in (21,22):
    for l in open('$HOME/cmp/jp/runs/lean_rich_%d.jsonl'%seed):
        d=json.loads(l); n+=1
        m+=any(p['minimumTax_41no19']>0 for p in d['detail']['persons'])
print('rich households with a 41条の19 minimum tax:', m, 'of', n)
P
echo DONE
