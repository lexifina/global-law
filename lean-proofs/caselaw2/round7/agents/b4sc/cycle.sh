#!/bin/sh
# b4sc: one full cycle (resumable; every step rewrites its own outputs). Run from anywhere.
#   final2_rows.py and tokdf.py / bo7.py keys are one-off inputs (work/final2_*.json*, work/tokdf.json,
#   work/inst_tokens.json, work/bo_multi.json); rerun them only if missing.
set -e
cd "$(dirname "$0")"
B=$(pwd)
C2=$(cd ../../.. && pwd)
[ -f work/final2_by.json ] || python -X utf8 final2_rows.py
[ -f work/tokdf.json ] || python -X utf8 tokdf.py --procs 22
[ -f work/bo_multi.json ] || python -X utf8 bo7.py keys --procs 22
python -X utf8 sc7.py run --procs 22 > work/run.log 2>&1
python -X utf8 select7.py > work/select.log
python -X utf8 bo7.py run --procs 22 > work/bo_run.log 2>&1
python -X utf8 bo7.py ev > work/bo_ev.log 2>&1
python -X utf8 work/filt_eo.py > work/filt_eo.log
cd "$C2"
for x in a e e_other; do
  python -X utf8 round7/certify7.py --rows "round7/agents/b4sc/rows_$x.jsonl" --out "round7/agents/b4sc/cert_$x" --procs 22 > "$B/work/cert_$x.log" 2>&1
done
cd "$B"
cat cert_a/history_delta.tsv cert_e/history_delta.tsv > work/guard/ae_delta.tsv
cp cert_e_other/history_delta.tsv work/guard/eo_delta.tsv
rm -f work/guard/*_drop_ids.txt work/guard/*_feat.*.jsonl.gz work/guard/*_features.jsonl.gz
for t in ae eo; do
  python -X utf8 gfeat7.py --base "work/guard/${t}_delta.tsv" --tag "${t}_" --procs 22 > "work/guard/${t}_gfeat.log" 2>&1
  python -X utf8 guard7.py "$t" "work/guard/${t}_delta.tsv" > "work/guard/${t}_guard.log" 2>&1
done
python -X utf8 deltas.py
echo cycle-done
