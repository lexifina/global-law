#!/bin/bash
cd ${IRS_AUDIT:-$HOME/irs-audit}
for x in "irs.gov/pub/irs-wd/ wd" "irs.gov/pub/irs-ccdm/ ccdm" "irs.gov/pub/irs-lafa/ lafa" "irs.gov/pub/irs-utl/ utl" "irs.gov/pub/irs-aod/ aod" "irs.gov/pub/lanoa/ lanoa" "irs.gov/pub/irs-counsel/ counsel" "irs.gov/pub/irs-sgml/ sgml" "irs.gov/pub/irs-ats/ ats"; do
  python3 tools/cdx.py $x || { echo "cdx stopped at $x"; exit 1; }
  sleep 6
done
echo ALL CDX DONE
