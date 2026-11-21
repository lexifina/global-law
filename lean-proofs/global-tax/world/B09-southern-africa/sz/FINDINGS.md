# Eswatini (SZ): findings, B09 build phase (2026-11-20T06:18Z)

Eswatini built from the Income Tax Order 1975 and Act 20 of 2023: 20-33 % with an E8 200 rebate (tax starts above E41 000); the 2023 rate table stops at E250 000 and is dated to the year ending 30 June 2023.

Scale for scanner numbers: 200,000 SZL = threshold of the top (33 %) band (Income Tax Order 1975 Third Schedule Part II (Act 20 of 2023 s. 39; 2013 text)); a statutory threshold, not an average wage.

### F1 Rate table with no rate above E250 000
- kind: statute-fault
- Act 20/2023 s. 39, Third Schedule Part II (checked on the page image): last row 'Exceeds 200 000 / Does not exceed 250 000 / 47 500 + 33% of taxable income in excess of 200 000'. Taxable income above E250 000 has no printed rate; the 2013 text and the ERS page have an open top row. The model uses 33 % without a ceiling.
- provisions: Income Tax Order Third Schedule Part II (Act 20 of 2023)
- Lean: SzTax.sched
- status: found by reading

### F2 Rate clause dated to a past year
- kind: statute-fault
- Part I para 1: 'the rates of tax to be levied for the year of assessment ending 30 June 2023 are as follows'. No later year is named; the 2013 text said 'commencing 1st July 2013'. The Act itself starts 'on a date to be determined by the Minister by Notice' (s. 1 (2)), not reached.
- provisions: Third Schedule Part I para 1; Act 20/2023 s. 1 (2)
- Lean: -
- status: found by reading

### F3 Over-60 rebate printed as E2 007 in the 2013 consolidation
- kind: gov-error
- The ERS consolidation of the Order (to 2013) reads 'an additional amount not exceeding two thousand seven emalangeni'; Act 20/2023 reads 'two thousand seven hundred Emalangeni', as does the ERS rates page (E2 700). The model uses E2 700.
- provisions: Third Schedule Part I (b) (ii)
- Lean: SzTax.rebate
- status: found by reading

### F4 Dividends and interest at 10 %
- kind: loophole-known
- Third Schedule Part I (e)-(f): 10 % on dividend and taxable interest income. E600 000 wages: 171 300; E500 000 wages + E100 000 dividends: 148 300.
- provisions: Third Schedule Part I (e), (f)
- Lean: SzTax.out
- status: recreated

## Step 4: known loopholes, catalogued from the statute (blind to referees)

- 10 % rate on dividends and interest: recreated
- E20 000 interest/dividend exemption (s. 12 (1) (qq)): not modelled
- concessionary rates for redundancy / retirement lump sums (Part III): not modelled
- 10 % mortgage-interest and insurance rebates (s. 8 (1) (b)): not modelled
- small business turnover tax (Sixth Schedule): not modelled

Literature not checked (no web-search budget this session): IMF Article IV / FAD reports, ATAF African Tax Outlook, ICTD/ITC working papers, World Bank PER chapters, Big-4 country tax guides, academic papers on the country's PIT; the catalogue above is therefore limited to what the statute and the official pages read here make visible.

## Step 5: searches run
- `tools/scan.py` (fine grid 0-2.5 x scale, single / couple 1 earner + 2 children / couple 60-40 + 2 children): {"single": {"maxMETR": 0.332, "netIncomeFalls": 0}, "couple1earner2kids": {"maxMETR": 0.332, "netIncomeFalls": 0}, "couple60_40_2kids": {"maxMETR": 0.32, "netIncomeFalls": 0}}
- `world/tools/scan_world.py SZ` (METR, phase-outs, timing, edges, filing unit, income type): `results/search/SUMMARY.md`. Scanner gains for income types the model marks unsupported are artefacts, not loopholes.

## Unsupported (listed in every output line where it applies)
- ENPF contributions
- s. 12 (1) (qq) exemption
- Act 20/2023 commencement notice

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: ENPF (Statutory Contributions) Regulations 2025 (LN 5/2025) reg. 2 (1) (a)-(b), as reproduced by the Fund; rate 5 % + 5 % (Fund notice); Income Tax Order s. 2 "pension fund", s. 14 (1) (i), Fourth Schedule para 2 (4)
- ENPF employee 5 % of wages up to E4,000 / month (2025) and E4,300 (2026); deducted (s. 14 (1) (i)). Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/SzTax/Verify.lean` (imported by the `SzTax` library and built; each guard evaluates `SzTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/SZ.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1, F2 | explained | No printed rate above E250,000; rate clause dated 2023: statute faults (the model uses 33 % open-ended). |
| F3 | explained | E2,007 vs E2,700 rebate: gov record. |
| F4 | confirmed | Dividends and interest at 10 %: 100,000 moved from wages to dividends keeps 23,000 more at 600,000. G: f4_dividends_10pct. S: Third Schedule Part I (e)-(f) as cited by the model; law/IncomeTaxAmendmentAct2023.ocr.txt:576-584 (withholding on interest or dividend). |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: interest/dividend wedge +20.5 % = F4. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F4: Dividends and interest at 10 % against wage rates to 33 % | income-type gap | **known**: PwC Eswatini: 'A withholding tax (WHT) is payable at a rate of 10% for dividends received'. | 2026-11-20: OpenAlex specific queries 'Eswatini dividends interest 10% individuals income tax' (325 hits, titles checked); OpenAlex broad 'Eswatini personal income tax', 'Eswatini income tax wages', 'Eswatini tax system reform' (75 records, titles and abstracts grepped, 0 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (eswatini, 5 individual pages): 5 passages with the item's terms. Record: world/loopholes/africa_mena/search/SZ-F4.json |

<!-- L1-VERIFICATION END -->


### D9R-1 ENPF caps applied month by month (D9 review, 2026-11-20)
- Model correction from the statute: LN 5/2025 reg. 2 (1) caps contributory wages per calendar month (E4,000 in 2025,
  E4,300 in 2026) and reg. 2 (2) disregards the excess month by month. The W5 fix used one annual cap of E49,800
  (5 % of min (wage, 49,800)), which overstates the contribution for annual wages between 48,000 and 51,600 (even monthly
  pay; at 49,800: 2,490 against 2,445). Now `enpfMonthly` = 5 % x (min (w, 48,000) + min (w, 51,600)) / 2; #guards at
  48,000 / 49,800 / 51,600 / 120,000 and equality with the old rule outside the band. Input `"szEnpfAnnualCap": true`
  restores the old rule: `w5/review4/check4.py SZ` with it 0 / 300 differ from the pre-change exe (5 / 300 change
  without). Rescanned (`logs/d9_review_scan_SZ.log`).
- Found on `sz_official_ers_paye_calculator_enpf_grid` (D9 review rebuild of the ERS calculator grid; ENPF entered as
  the page's Deductions by the statutory monthly rule): 274 / 277 dev within 1 before, 277 / 277 after. The ERS page
  itself displays ENPF but does not subtract it from the tax base (the user must enter it as a deduction): not an error
  of the page, a declared input of the grid.
- provisions: ENPF (Statutory Contributions) Regulations 2025 (LN 5/2025) reg. 2 (1) (a)-(b), (2)

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: ceiling at 0.25 AW (contribution rate 5.0 -> 0.0 %, combined marginal 18 -> 20 %); floor at low pay AW (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
