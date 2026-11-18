#!/bin/bash
# GOV.UK content API (official, machine-readable), sequential and polite
cd ~/cmp/uk/refs/govuk
UA="Mozilla/5.0 (compatible; research-fetch)"
while read path; do
  [ -z "$path" ] && continue
  name=$(echo "$path" | sed 's#^/##; s#/#__#g')
  [ -s "$name.json" ] && continue
  code=$(curl -sS -A "$UA" -o "$name.json" -w "%{http_code}" "https://www.gov.uk/api/content$path")
  echo "$path $code"
  sleep 1.5
done <<'LIST'
/income-tax-rates
/income-tax-rates/income-over-100000
/apply-tax-free-interest-on-savings
/tax-on-dividends
/marriage-allowance
/child-benefit-tax-charge
/child-benefit-rates
/guidance/adjusted-net-income
/capital-gains-tax
/capital-gains-tax/rates
/capital-gains-tax/allowances
/guidance/rates-and-thresholds-for-employers-2025-to-2026
/national-insurance-rates-letters
/self-employed-national-insurance-rates
/donating-to-charity/gift-aid
/tax-on-your-private-pension/pension-tax-relief
/blind-persons-allowance
/government/publications/rates-and-allowances-income-tax/income-tax-rates-and-allowances-current-and-past
/government/publications/rates-and-allowances-national-insurance-contributions/rates-and-allowances-national-insurance-contributions
/government/publications/rates-and-allowances-capital-gains-tax/capital-gains-tax-rates-and-annual-tax-free-allowances
/government/publications/benefit-and-pension-rates-2025-to-2026/benefit-and-pension-rates-2025-to-2026
/government/publications/personal-savings-allowance-factsheet/personal-savings-allowance-factsheet
/government/publications/dividend-allowance-factsheet/dividend-allowance-factsheet
/government/publications/rates-and-allowances-hmrc-pension-schemes/pension-schemes-rates
/hmrc-internal-manuals/savings-and-investment-manual
/hmrc-internal-manuals/pensions-tax-manual/ptm044220
/hmrc-internal-manuals/pensions-tax-manual/ptm044210
/hmrc-internal-manuals/pensions-tax-manual/ptm044200
LIST
echo ALLDONE
