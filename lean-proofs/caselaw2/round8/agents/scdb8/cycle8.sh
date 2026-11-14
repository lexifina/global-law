#!/bin/sh
# scdb8: one full cycle (resumable; each step rewrites its own outputs). Usage: sh cycle8.sh <variant name>
set -e
export PYTHONUTF8=1
cd "$(dirname "$0")"
B=$(pwd)
C2=$(cd ../../.. && pwd)
V=${1:-scdb8_x}
python -X utf8 sc8.py run --procs 10 > work/run.log 2>&1
python -X utf8 sc8.py run --procs 10 --off d1,d2,d3,r4,a5,s6,t1 --tag _off > work/run_off.log 2>&1
if [ -z "$SKIP_LOO" ]; then
python -X utf8 sc8.py run --procs 10 --on aw --tag _aw > work/run_aw.log 2>&1
python -X utf8 sc8.py run --procs 10 --off d1,d2,d3 --tag _noD > work/run_noD.log 2>&1
python -X utf8 sc8.py run --procs 10 --off a5,s6 --tag _noA > work/run_noA.log 2>&1
python -X utf8 sc8.py run --procs 10 --off t1 --tag _noT > work/run_noT.log 2>&1
python -X utf8 sc8.py run --procs 10 --off r4 --tag _noR > work/run_noR.log 2>&1
fi
python -X utf8 select8.py > work/select.log
python -X utf8 select8.py --wide > work/select_w.log
python -X utf8 recert8.py > work/recert.log
python -X utf8 -c "
import json
rows=[json.loads(l) for l in open('rows8.jsonl',encoding='utf-8')]
rows+=[r for r in map(json.loads,open('rows_recert.jsonl',encoding='utf-8')) if '_r5_' in r['rule']]
open('rows_c.jsonl','w',encoding='utf-8',newline='\n').write(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
print(len(rows))"
cd "$C2"
python -X utf8 round8/certify8.py --rows round8/agents/scdb8/rows_c.jsonl --out round8/agents/scdb8/cert_c --procs 10 > "$B/work/cert_c.log" 2>&1
rm -rf round8/agents/scdb8/cert_w
python -X utf8 round8/agents/scdb8/certify8w.py --rows round8/agents/scdb8/rows8_w.jsonl --out round8/agents/scdb8/cert_w --procs 10 > "$B/work/cert_w.log" 2>&1
cd "$B"
rm -f work/guard/w_*
cp cert_w/history_delta.tsv work/guard/w_delta.tsv
python -X utf8 gfeat8.py --base work/guard/w_delta.tsv --tag w_ --procs 10 > work/guard/w_gfeat.log 2>&1
python -X utf8 guard8.py w work/guard/w_delta.tsv > work/guard/w_guard.log 2>&1
rm -rf delta_w_*
python -X utf8 deltas8.py cert_w work/guard/w_drop_ids.txt delta_w
rm -f work/guard/c_*
cp cert_c/history_delta.tsv work/guard/c_delta.tsv
python -X utf8 gfeat8.py --base work/guard/c_delta.tsv --tag c_ --procs 10 > work/guard/c_gfeat.log 2>&1
python -X utf8 guard8.py c work/guard/c_delta.tsv > work/guard/c_guard.log 2>&1
rm -rf delta_c_*
python -X utf8 deltas8.py cert_c work/guard/c_drop_ids.txt delta_c
python -X utf8 -c "
by={l.split('\t')[2] for l in open('delta_c_r4/history_delta.tsv',encoding='utf-8') if 'r4rep' in l.split('\t')[12]} if __import__('os').path.exists('delta_c_r4/history_delta.tsv') else set()
rem=[i.strip() for i in open('remove_r4.txt') if i.split(':')[1] in by]
open('delta_c_remove_r4.txt','w',newline='\n').write(''.join(i+'\n' for i in rem)); print('remove',len(rem))"
cd "$C2"
python -X utf8 round8/stage8.py "$V" --delta round8/agents/scdb8/delta_c_all --remove round8/agents/scdb8/delta_c_remove_r4.txt > "$B/work/stage_$V.log" 2>&1
echo cycle-done "$V"
