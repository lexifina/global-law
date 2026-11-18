#!/bin/bash
# Rerun every part of the comparison with the current exes of all five models. Log: logs/final_run_<n>.log
set -u
cd "$(dirname "$0")"
C=US,FR,UK,DE,JP
echo "start $(date -Is)"
export CMP_FROZEN=$(python3 freeze.py)
echo "frozen: $CMP_FROZEN"; cat "$CMP_FROZEN/frozen.json" | python3 -c "import json,sys; d=json.load(sys.stdin); [print(k, v['ok'], (v['sha256'] or '')[:12], v['source_mtime']) for k,v in d.items()]"
python3 -u oecd_check.py --countries $C > /dev/null && echo "oecd_check ok"
python3 -u oecd_check.py --countries JP --age 39 --out oecd_check_jp_age39.json > /dev/null && echo "oecd_check JP age 39 ok"
python3 -u oecd_marginal.py $C > /dev/null && echo "oecd_marginal ok"
python3 -u oecd_error_effects.py > /dev/null && echo "oecd_error_effects ok"
python3 -u analyses.py all --countries $C
python3 -u jp_dividend_regimes.py
python3 -u cliff_summary.py | grep -v "^   " | grep -v "^bands"
python3 -u complexity.py > /dev/null && echo "complexity ok"
python3 -u report.py > /dev/null && echo "report ok"
python3 -u blog_numbers.py > /dev/null && echo "blog_numbers ok"
echo "end $(date -Is)"
