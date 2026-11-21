# Lesotho (LS): findings, B09 build phase (2026-11-20T06:18Z)

Lesotho built from the Income Tax Act 1993 (2012 consolidation) with the RSL's 2025/26 amounts: 20 % / 30 % and a M970-a-month credit (no tax up to M4 850 a month); the official consolidation still prints 2010 amounts.

Scale for scanner numbers: 74,040 LSL = threshold of the 30 % band (12 x M6 170) (RSL Guide on Taxation of Employment Income 25-26 s. 3.1 (official secondary) under ITA 1993 s. 9); a statutory threshold, not an average wage.

### F1 The official consolidation is 13 years old and prints superseded amounts
- kind: gov-error
- RSL serves 'Income Tax Act 1993 Updated up to 1 April 2012': Second Schedule 'First M40,368 22% / Over M40,368 35%', s. 73 personal credit M5 184. Its own 2025/26 guide gives 20 %/30 %, M6 170 a month and M970 a month. The instruments that changed them are not served with the Act.
- provisions: ITA 1993 s. 9, 73, Second Schedule
- Lean: LsTax.sched, LsTax.credit
- status: access

### F2 Non-refundable credit wasted below the threshold
- kind: fact
- s. 73 credit is non-refundable: below M58 200 a year the unused credit is lost (kernel applyCredits_waste); checked by #guard at M4 850 a month.
- provisions: ITA s. 4 (2), 73
- Lean: LsTax.personTax
- status: modelled

### F3 Interest exemption for one nominated savings account
- kind: fact
- s. 27 (1): 'The first M500 of interest derived from one savings account ... is exempt'.
- provisions: ITA s. 27
- Lean: LsTax.out
- status: modelled

## Step 4: known loopholes, catalogued from the statute (blind to referees)

- one-account M500 interest exemption: recreated
- non-refundable personal credit: recreated
- pension contributions deductible (cap not read): not modelled
- fringe benefits taxed on the employer (Fourth Schedule): not modelled
- minors' property income at a separate rate (s. 9 (2)): not modelled

Literature not checked (no web-search budget this session): IMF Article IV / FAD reports, ATAF African Tax Outlook, ICTD/ITC working papers, World Bank PER chapters, Big-4 country tax guides, academic papers on the country's PIT; the catalogue above is therefore limited to what the statute and the official pages read here make visible.

## Step 5: searches run
- `tools/scan.py` (fine grid 0-2.5 x scale, single / couple 1 earner + 2 children / couple 60-40 + 2 children): {"single": {"maxMETR": 0.3043, "netIncomeFalls": 0}, "couple1earner2kids": {"maxMETR": 0.3043, "netIncomeFalls": 0}, "couple60_40_2kids": {"maxMETR": 0.2717, "netIncomeFalls": 0}}
- `world/tools/scan_world.py LS` (METR, phase-outs, timing, edges, filing unit, income type): `results/search/SUMMARY.md`. Scanner gains for income types the model marks unsupported are artefacts, not loopholes.

## Unsupported (listed in every output line where it applies)
- the regulation / Finance Act setting the 2025/26 band and credit
- pension contribution cap
- dividends, capital gains

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | 13-year-old consolidation: gov record. |
| F2 | explained | Non-refundable credit wasted: kernel applyCredits_waste. |
| F3 | explained | M500 interest exemption: design. |
| Leads | explained | Rescan: no notch. |

<!-- L1-VERIFICATION END -->
