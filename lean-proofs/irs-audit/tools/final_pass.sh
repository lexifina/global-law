#!/bin/bash
# Once the harvesters have finished: every extractor and checker over everything held.
cd ${IRS_AUDIT:-$HOME/irs-audit}; export PATH=$HOME/.elan/bin:$PATH
mkdir -p logs; pkill -f process_loop.sh; sleep 2
while pgrep -f 'wd_text.py|check_docs.py|cb_process.py' > /dev/null; do sleep 10; done
echo "start $(date +%T)"
nice python3 wd/wd_text.py; echo "wd_text $(date +%T)"
nice python3 wd/check_docs.py > logs/check_docs.log 2>&1; echo "check_docs $(date +%T) $(head -c 400 logs/check_docs.log)"
nice python3 wd/amounts_scan.py > logs/amounts_scan.log 2>&1; echo "amounts $(head -c 300 logs/amounts_scan.log)"
nice python3 src/govinfo/cb_process.py > logs/cb_process.log 2>&1; echo "cb_process $(date +%T)"
nice python3 src/govinfo/cb_usability.py > logs/cb_usability.log 2>&1
python3 afr/cb_afr2.py && python3 afr/cb_afr_early.py && python3 afr/gen_lean_cb.py > /dev/null && (cd lean/afr && lean --run RunCB.lean > ../../afr/lean_out_cb.tsv 2> ../../afr/lean_err_cb.txt)
python3 afr/gen_lean_cb_mult.py && (cd lean/afr && lean --run RunCBMult.lean > ../../afr/lean_out_cb_mult.tsv 2> ../../afr/lean_err_cb_mult.txt)
python3 q6621/cb_q.py > logs/cb_q.log && (cd lean/q6621 && lean --run RunCB.lean > ../../q6621/lean_out_cb.tsv 2> ../../q6621/lean_err_cb.txt)
python3 indexing/cb_exemption.py > logs/cb_exemption.log; nice python3 src/govinfo/cb_cites.py > logs/cb_cites.log 2>&1
python3 afr/cb_afr_late.py > /dev/null; python3 afr/cb_vs_irb.py > logs/cb_vs_irb.log
python3 prior/std_charts.py > logs/std_charts.log; python3 withholding/p15t_check.py > logs/p15t.log; python3 withholding/p15_arith.py > logs/p15.log 2>/dev/null
echo "FINAL PASS DONE $(date +%T)"
