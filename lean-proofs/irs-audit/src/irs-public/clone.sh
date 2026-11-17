#!/bin/bash
cd ${IRS_AUDIT:-$HOME/irs-audit}/src/irs-public
for r in direct-file tax-withholding-estimator eitc-assistant fact-graph; do
  [ -d $r ] || git clone -q --depth 1 https://github.com/IRS-Public/$r.git && echo cloned $r
done
echo CLONE DONE
