#!/bin/sh
# fjc8: linker -> certify8 -> round-6 guard -> delta folder (resumable; each step rewrites its outputs).
#   sh round8/agents/fjc8/cycle.sh <tag>      (tag names cert_<tag>/, delta_<tag>/, work/guard/<tag>_*)
set -e
cd "$(dirname "$0")"
B=$(pwd)
C2=$(cd ../../.. && pwd)
T=${1:-f12}
[ -f work/base_by_trial.json ] || python -X utf8 fjc_link.py base
python -X utf8 fjc_link.py run --procs 10 > work/link_run.log 2>&1
cp rows_f1.jsonl "rows_$T.jsonl"
cd "$C2"
python -X utf8 round8/certify8.py --rows "round8/agents/fjc8/rows_$T.jsonl" --out "round8/agents/fjc8/cert_$T" --procs 10 > "$B/work/cert_$T.log" 2>&1
cd "$B"
cp "cert_$T/history_delta.tsv" "work/guard/${T}_delta.tsv"
rm -f work/guard/${T}_feat.*.jsonl.gz work/guard/${T}_features.jsonl.gz
python -X utf8 gfeat8.py --base "work/guard/${T}_delta.tsv" --tag "${T}_" --procs 10 > "work/guard/${T}_gfeat.log" 2>&1
python -X utf8 guard8.py "$T" "work/guard/${T}_delta.tsv" > "work/guard/${T}_guard.log" 2>&1
python -X utf8 deltas.py "delta_$T" "cert_$T" --drop "work/guard/${T}_drop_ids.txt"
echo cycle-done
