#!/usr/bin/env bash
# Round 8 ownact: all answers so far -> rows.jsonl -> certify8 (cert/) -> strata.  bash run_batch.sh [--packs 000,001]
set -e
C2=~/Documents/us-caselaw-lean-work/caselaw-lean-2
H=$(cygpath -m $C2/round8/agents/ownact)
cd "$C2"
python -X utf8 "$H/answers_to_rows8.py" --ans "$H/ans" --out "$H/rows.jsonl" "$@" > "$H/rows.log" 2>&1
rm -rf "$H/cert.new"
python -X utf8 round8/certify8.py --rows "$H/rows.jsonl" --out "$H/cert.new" --procs 6 > "$H/certify.log" 2>&1
rm -rf "$H/cert"
mv "$H/cert.new" "$H/cert"
python -X utf8 "$H/strata.py" --cert "$H/cert" --rows "$H/rows.jsonl" > "$H/strata.log" 2>&1
python -X utf8 -c "import json;s=json.load(open('$H/rows_stats.json'));c=json.load(open('$H/cert/stats.json'))['counts'];print('answers',s.get('answers'),'yes',s.get('own_act_true'),'rows',s.get('rows'),'admitted',c.get('admitted'),'rejected',c.get('rejected'))"
