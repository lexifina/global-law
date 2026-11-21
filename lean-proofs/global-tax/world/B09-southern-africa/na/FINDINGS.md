# Namibia (NA): findings, B09 build phase (2026-11-20T06:18Z)

Namibia built from the Income Tax Act (Global law, Act 4 of 2024 schedule): N$100 000 zero band, 18-37 %; bank interest bears a final 10 % (s. 34A) and dividends are exempt, so N$100 000 of interest instead of wages saves N$27 000 and of dividends N$37 000 at the top rate.

Scale for scanner numbers: 350,000 NAD = threshold of the 28 % band (Income Tax Act 24 of 1981 Sch. 4 para 1 (d) as substituted by Act 4 of 2024); a statutory threshold, not an average wage.

### F1 Bank interest at a final 10 % and exempt dividends beside a 37 % wage rate
- kind: loophole-known
- s. 34A (1)-(2): 10 % withholding on bank / unit-trust interest is 'a final tax ... not added to ... any other income'; s. 16 (1) (n) (i) exempts dividends; s. 1 'gross income' excludes 'receipts or accruals of a capital nature'. Single person with N$1 700 000 wages pays 484 500; with N$1 600 000 wages + N$100 000 bank interest 457 500 (gain 27 000); with N$100 000 dividends instead 447 500 (gain 37 000). Scanner (income_type, scale N$350 000 = 28 % band threshold): dividends/capital gains +28.7 % of income at 5 x scale.
- provisions: ITA s. 1, 16 (1) (n), 34A
- Lean: NaTax.out
- status: recreated (scanner + pair)

### F2 Company rate clause for 2025 reads as two rates at once
- kind: statute-fault
- Sch. 4 para 3 (1) (a): '(i) 31 cents in respect of the year of assessment on or after 1 January 2024; and (ii) 30 cents in respect of any year of assessment on or after 1 January 2025'. A year beginning on or after 1 January 2025 is also on or after 1 January 2024, so both items literally apply to it (para 4, 'shall be payable in addition to the tax determined in accordance with any other of the said subparagraphs', speaks of subparagraphs, so the overlap is one of items, not an addition). The intended reading (30 cents from 2025) needs 'before 1 January 2025' in (i). Also para 1 (d) 'does not of exceed'. Company side only (owner-manager), not used by the individual model.
- provisions: ITA Sch. 4 paras 3 (1) (a), 4 (Act 4 of 2024)
- Lean: -
- status: found by reading

### F3 Combined retirement / education-policy deduction cap
- kind: fact
- s. 17 (2): deductions under (n), (q), (qA) and (w) together 'shall not ... exceed the sum of N$150 000' (years from 1 March 2022). The model caps the contract's pensionContributions at N$150 000.
- provisions: ITA s. 17 (2)
- Lean: NaTax.personTI
- status: modelled

### F4 Social security split not public in the sources reached
- kind: model-fix
- The SSC publishes the MSD Fund rate as a single 1.8 % (N$500 to N$11 000 a month from 1 March 2025; N$12 500 from 1 September 2026). The employee's share sits in regulations under s. 21 (2) that were not reached, so employeeSocial = 0 and the combined amount is in detail.msdCombinedEmployerEmployee.
- provisions: Social Security Act 1994 s. 21 (2)
- Lean: NaTax.msdCombinedMonthly
- status: open

## Step 4: known loopholes, catalogued from the statute (blind to referees)

- final 10 % WHT on bank interest (s. 34A): recreated
- dividend exemption (s. 16 (1) (n)): recreated
- no capital gains tax (capital receipts outside gross income): recreated
- retirement-fund deduction up to N$150 000 (s. 17 (2)): recreated
- income from a spouse's business reattributed (Sch. 4 para 2 anti-avoidance): not modelled
- foreign-source income outside the source-based tax (s. 1, s. 15): not modelled

Literature not checked (no web-search budget this session): IMF Article IV / FAD reports, ATAF African Tax Outlook, ICTD/ITC working papers, World Bank PER chapters, Big-4 country tax guides, academic papers on the country's PIT; the catalogue above is therefore limited to what the statute and the official pages read here make visible.

## Step 5: searches run
- `tools/scan.py` (fine grid 0-2.5 x scale, single / couple 1 earner + 2 children / couple 60-40 + 2 children): {"single": {"maxMETR": 0.3219, "netIncomeFalls": 0}, "couple1earner2kids": {"maxMETR": 0.3219, "netIncomeFalls": 0}, "couple60_40_2kids": {"maxMETR": 0.2694, "netIncomeFalls": 0}}
- `world/tools/scan_world.py NA` (METR, phase-outs, timing, edges, filing unit, income type): `results/search/SUMMARY.md`. Scanner gains for income types the model marks unsupported are artefacts, not loopholes.

## Unsupported (listed in every output line where it applies)
- employee share of the MSD contribution (combined 1.8 % on N$500-11 000 a month reported in detail)
- foreign-source income (source basis)
- non-bank interest at Schedule 4 rates

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: Regulations under SSA 1994 s. 47, GN 198 of 1995 (GG 1181) reg. 8 (a)
- MSD employee 0.9 % of monthly remuneration in the N$500-11,000 band; not deductible. Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/NaTax/Verify.lean` (imported by the `NaTax` library and built; each guard evaluates `NaTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/NA.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | Bank interest at a final 10 % (and exempt dividends): 100,000 moved from wages to interest keeps 27,000 more at 1.7 M. G: f1_interest_final_10pct. S: law/gl_sec-034a.txt:14 (s. 34A (2): 'a final tax as the interest on which it is paid is not added to or set-off against any other income'). |
| F2 | explained | Company-rate clause reads as two rates: statute fault (company side). |
| F3 | explained | Combined N$150,000 deduction cap: design. |
| F4 | explained | MSD split not public: record. |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: interest wedge +18.9 % = F1; dividends +28.8 % (exempt). |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Final 10 % on bank and unit-trust interest, exempt dividends, against 37 % | income-type gap | **unclear**: Nothing found (no PwC page for the country under 'namibia'; OpenAlex: nothing); the rule is a standard published final withholding, so absence from the search says little. | 2026-11-20: OpenAlex specific queries 'Namibia withholding tax on interest final 10% individuals unit trusts' (541 hits, titles checked); OpenAlex broad 'Namibia personal income tax', 'Namibia income tax wages', 'Namibia tax system reform' (75 records, titles and abstracts grepped, 2 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country. Record: world/loopholes/africa_mena/search/NA-F1.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: ceiling at 0.29 AW (contribution rate 1.0 -> 0.0 %, combined marginal 2 -> 19 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
