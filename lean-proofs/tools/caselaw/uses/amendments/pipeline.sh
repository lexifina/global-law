#!/bin/bash
# Full run: extract (113th-119th), build Lean input (4 shards), run the Lean check, join.
set -e
cd "$HOME/Documents/us-caselaw-lean-work/uses/amendments"
[ "$1" = "skip-extract" ] || python tools/extract.py 113 119 data/instructions.jsonl
python tools/build_input.py data/instructions.jsonl data/lean_in.tsv data/ops.tsv --shards 4
for i in 0 1 2 3; do tools/run_lean.sh data/lean_in.tsv.$i data/lean_out.$i > data/lean_run.$i.log & done
wait
cat data/lean_run.*.log
python tools/join.py data/ops.tsv data/lean_out.0 data/lean_out.1 data/lean_out.2 data/lean_out.3 data/results.tsv
echo done
