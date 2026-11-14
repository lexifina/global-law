#!/bin/sh
# scdb9: select -> certify9 -> round-6 guard -> delta folders by class (+ remove list). Runs after the sc9.py runs.
# Usage: sh cycle9.sh
set -e
export PYTHONUTF8=1
cd "$(dirname "$0")"
B=$(pwd)
C2=$(cd ../../.. && pwd)
[ -n "$SKIP_SELECT" ] || python -X utf8 select9.py > work/select9.log
cd "$C2"
rm -rf round9/agents/scdb9/cert9
python -X utf8 round9/certify9.py --rows round9/agents/scdb9/rows9.jsonl --out round9/agents/scdb9/cert9 --procs 8 > "$B/work/cert9.log" 2>&1
cd "$B"
rm -f work/guard/c_*
cp cert9/history_delta.tsv work/guard/c_delta.tsv
python -X utf8 gfeat8.py --base work/guard/c_delta.tsv --tag c_ --procs 8 > work/guard/c_gfeat.log 2>&1
python -X utf8 guard8.py c work/guard/c_delta.tsv > work/guard/c_guard.log 2>&1
rm -rf delta9_*
python -X utf8 deltas9.py cert9 work/guard/c_drop_ids.txt delta9
python -X utf8 -c "
import os
keep={l.split('\t')[2] for l in open('delta9_all/history_delta.tsv',encoding='utf-8') if l.strip()}
rem=[]
import json
for l in open('rows9.jsonl',encoding='utf-8'):
    pass
rm=[i.strip() for i in open('remove9.txt') if i.strip()]
open('delta9_remove.txt','w',newline='\n').write(''.join(i+'\n' for i in rm if i.split(':')[1] in keep)); print('remove', len(rm))"
echo cycle9-done
