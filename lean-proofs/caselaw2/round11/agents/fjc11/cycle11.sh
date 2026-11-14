#!/bin/sh
# fjc11: rows_<tag>.jsonl -> certify11 -> round-6 guard (fjc8/fjc9/fjc10b copies) -> delta_<tag>/
#   sh round11/agents/fjc11/cycle11.sh <tag>
set -e
cd "$(dirname "$0")"
B=$(pwd)
C2=$(cd ../../.. && pwd)
T=${1:-x2}
mkdir -p work/guard
cd "$C2"
python -X utf8 round11/certify11.py --rows "round11/agents/fjc11/rows_$T.jsonl" --out "round11/agents/fjc11/cert_$T" --procs 8 > "$B/work/cert_$T.log" 2>&1
cd "$B"
cp "cert_$T/history_delta.tsv" "work/guard/${T}_delta.tsv"
rm -f work/guard/${T}_feat.*.jsonl.gz work/guard/${T}_features.jsonl.gz
python -X utf8 gfeat8.py --base "work/guard/${T}_delta.tsv" --tag "${T}_" --procs 8 > "work/guard/${T}_gfeat.log" 2>&1
python -X utf8 guard8.py "$T" "work/guard/${T}_delta.tsv" > "work/guard/${T}_guard.log" 2>&1
python -X utf8 deltas.py "delta_$T" "cert_$T" --drop "work/guard/${T}_drop_ids.txt"
echo cycle-done
