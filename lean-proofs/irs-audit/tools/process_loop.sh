#!/bin/bash
# Every 10 minutes: text for new written determinations and CB volumes, then the checkers. Stops by itself
# when no harvester is running any more (after one last pass).
cd ${IRS_AUDIT:-$HOME/irs-audit}; mkdir -p logs
while true; do
  nice python3 wd/wd_text.py > logs/wd_text.log 2>&1
  nice python3 wd/check_docs.py > logs/check_docs.log 2>&1
  nice python3 wd/amounts_scan.py > logs/amounts_scan.log 2>&1
  pgrep -f cb_process.py > /dev/null || nice python3 src/govinfo/cb_process.py > logs/cb_process.log 2>&1
  echo "pass $(date +%H:%M) $(head -c 300 logs/check_docs.log)"
  pgrep -f 'irs_harvest.py|govinfo_cb.py' > /dev/null || { echo "harvesters done"; break; }
  sleep 600
done
