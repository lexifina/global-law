#!/bin/bash
# runs after the written-determination sample (sequential fetching); verification copies for findings
cd ${IRS_AUDIT:-$HOME/irs-audit}
while pgrep -f 'irm/harvest.py|wd/probe.py' > /dev/null; do sleep 30; done
python3 tools/fetch.py https://www.irs.gov/pub/irs-drop/rp-09-21.pdf https://www.irs.gov/pub/irs-irbs/irb09-16.pdf https://www.irs.gov/pub/irs-drop/rr-17-02.pdf https://www.irs.gov/pub/irs-drop/rr-17-01.pdf
for f in irs-drop/rp-09-21 irs-irbs/irb09-16 irs-drop/rr-17-02 irs-drop/rr-17-01; do [ -f cache/www.irs.gov/pub/$f.pdf ] && pdftotext -layout cache/www.irs.gov/pub/$f.pdf cache/www.irs.gov/pub/$f.txt; done
echo FINAL_FETCH_DONE
