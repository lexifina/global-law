#!/bin/bash
# Generate households and run PolicyEngine on them (the slow part); Lean runs are instant and redone by compare.
cd ~/cmp/uk
for spec in "mixed 5000 101" "invest 3000 202" "edges 3000 303" "simple 2000 404"; do
  set -- $spec
  name=r_$1
  python3 -I harness/gen_households.py $2 $3 runs/$name.jsonl $1
  venv-pe/bin/python -I harness/pe_run.py runs/$name.jsonl runs/$name.pe.jsonl 500 2> logs/pe_$name.log
  echo "$name done $(date +%T)"
done
echo ALLDONE
