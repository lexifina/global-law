#!/bin/bash
# D4 on the real data: run the Lean runner and the Python reference on one data directory, diff them canonically,
# and write per-file/per-rule rates and a stratified triage sample.
#   usage: difftest/run_real.sh <run-name> [data-dir]     (output in difftest/<run-name>/)
# Other agents may rewrite data/ during a run: pass a snapshot (cp -p data/*.tsv difftest/snapN/) so that both
# sides read the same files.
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
REF="$HERE/../tools/caselaw2/ref"
R="$HERE/difftest/${1:-real}"
DATA="${2:-data}"
mkdir -p "$R"
cd "$HERE"
echo "$DATA" > "$R/data_dir.txt"
bash run_lean.sh 8 "$DATA" ../lean-in-v3 "$R/lean" > "$R/lean.log" 2>&1
python "$REF/precedent_ref.py" run --data "$DATA" --edges ../lean-in-v3 --out "$R/ref" > "$R/ref.log" 2>&1
python "$REF/diff.py" "$R/lean" "$R/ref" --info --tsv "$R/diff.tsv" > "$R/diff.txt" 2>&1 || true
python "$REF/real_report.py" "$R" --sample 100
