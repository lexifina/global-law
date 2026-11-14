#!/bin/sh
# fjc9: rows_<tag>.jsonl -> certify9 -> round-6 guard (fjc8 copies) -> delta_<tag>/ (resumable; each step rewrites).
#   sh round9/agents/fjc9/cycle9.sh <tag>
set -e
cd "$(dirname "$0")"
B=$(pwd)
C2=$(cd ../../.. && pwd)
T=${1:-w1}
mkdir -p work/guard
cd "$C2"
python -X utf8 round9/certify9.py --rows "round9/agents/fjc9/rows_$T.jsonl" --out "round9/agents/fjc9/cert_$T" --procs 8 > "$B/work/cert_$T.log" 2>&1
cd "$B"
cp "cert_$T/history_delta.tsv" "work/guard/${T}_delta.tsv"
rm -f work/guard/${T}_feat.*.jsonl.gz work/guard/${T}_features.jsonl.gz
python -X utf8 gfeat8.py --base "work/guard/${T}_delta.tsv" --tag "${T}_" --procs 8 > "work/guard/${T}_gfeat.log" 2>&1
python -X utf8 guard8.py "$T" "work/guard/${T}_delta.tsv" > "work/guard/${T}_guard.log" 2>&1
python -X utf8 deltas.py "delta_$T" "cert_$T" --drop "work/guard/${T}_drop_ids.txt"
echo cycle-done
