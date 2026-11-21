# Malawi (MW): findings, B09 build phase (2026-11-20T06:18Z)

Malawi modelled only for the rates in force from 30 December 2025 (MRA notice on Act 36/2025): employment income 0/30/35/40 %, other income 0/30 %, so K120 m of self-employment income pays 35 388 000 against 40 446 000 as wages.

Scale for scanner numbers: 18,840,000 MWK = threshold of the 35 % PAYE band (K2 040 000 + K16 800 000) (MRA public notice on the Taxation (Amendment) (No. 2) Act 36 of 2025, item VI (official secondary)); a statutory threshold, not an average wage.

### F1 Two schedules: employment income up to 40 %, other personal income at most 30 %
- kind: loophole-new
- MRA notice items V and VI: 'Personal Income Tax Rates ... First K2,040,000 0% / Excess of K2,040,000 30%' and PAYE rates on employment income 0/30/35/40 %. K120 000 000 as wages: 40 446 000; as self-employment income: 35 388 000 (gain 5 058 000). Whether a person with both kinds of income gets two zero bands is not said in the notice (the model applies each schedule on its own). Not found in the sources searched (only the notice was available).
- provisions: Taxation Act Eleventh Schedule as amended by Act 36 of 2025 (MRA notice items V-VI)
- Lean: MwTax.empSched, MwTax.persSched
- status: found by the scanner (income_type +4.7 %) and pair

### F2 The year's rates changed on 30 December 2025 and the earlier rates are not public in the sources reached
- kind: gov-error
- The MRA notice says the measures apply 'with effect from 30th December 2025'; the instrument that set the rates for January-December 2025 (Taxation (Amendment) Act 2024 / Bill 2024) is only on MalawiLII, which refuses scripts. A model of 2025 therefore covers two days of the calendar year.
- provisions: -
- Lean: -
- status: access

### F3 Exemption for gains on listed shares held 12 months removed
- kind: fact
- Notice item III: 'all gains from sales of shares are now subject to income tax regardless of the holding period.' The model taxes capital gains on the personal schedule.
- provisions: First Schedule (Act 36 of 2025)
- Lean: MwTax.out
- status: modelled

## Step 4: known loopholes, catalogued from the statute (blind to referees)

- employment vs other income schedules (40 % vs 30 % top): recreated
- exempt gains on shares held 12 months (removed 30 Dec 2025): catalogued
- tax-free betting winnings thresholds (removed): not modelled
- fringe benefits taxed on the employer (FBT): not modelled
- 0.05 % levy on transfers: not modelled

Literature not checked (no web-search budget this session): IMF Article IV / FAD reports, ATAF African Tax Outlook, ICTD/ITC working papers, World Bank PER chapters, Big-4 country tax guides, academic papers on the country's PIT; the catalogue above is therefore limited to what the statute and the official pages read here make visible.

## Step 5: searches run
- `tools/scan.py` (fine grid 0-2.5 x scale, single / couple 1 earner + 2 children / couple 60-40 + 2 children): {"single": {"maxMETR": 0.35, "netIncomeFalls": 0}, "couple1earner2kids": {"maxMETR": 0.35, "netIncomeFalls": 0}, "couple60_40_2kids": {"maxMETR": 0.33, "netIncomeFalls": 0}}
- `world/tools/scan_world.py MW` (METR, phase-outs, timing, edges, filing unit, income type): `results/search/SUMMARY.md`. Scanner gains for income types the model marks unsupported are artefacts, not loopholes.

## Unsupported (listed in every output line where it applies)
- rates before 30 December 2025
- combination of PAYE and personal schedules
- pension contributions
- WHT on interest and dividends

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: Pension Act No. 6 of 2023 s. 12 (1) (b), s. 2 "pensionable emoluments"
- Pension Act 2023 employee minimum 5 % of pensionable emoluments (no ceiling); not deducted (Taxation Act not reached). Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/MwTax/Verify.lean` (imported by the `MwTax` library and built; each guard evaluates `MwTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/MW.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | Two schedules: employment income 0/30/35/40 %, other personal income 0/30 %: K120 M as self-employment pays 5,058,000 less income tax than as wages. Whether one person gets two zero bands is open. G: f1_two_schedules_tax. S: law/mw_measures_2026.txt (MRA notice items V-VI, as cited; :49 'In excess of K5 billion 40%' is the company table). |
| F2 | explained | Rates changed on 30 December 2025: access record. |
| F3 | explained | Gains on listed shares now taxed: design. |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan self-employment wedge +9.2 % = F1. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Two schedules: employment income to 40 %, other personal income at most 30 % | income-type gap | **known**: The separate non-employment schedule (0 % on the first K1.8 M, then 30 %) is printed in the Taxation Amendment Bill 2024 (MalawiLII, found by web search) and the MRA notice; the gap follows directly. | 2026-11-20: OpenAlex queries 'Malawi personal income tax rates non-employment income 30% PAYE 40%'; 'Malawi Taxation Act 2025 amendment income tax rates' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Malawi tax policy' (8325 records, titles only); web search: WebSearch 2026-11-20 'Malawi 2025 personal income tax non-employment income 30% PAYE 40%': MRA/Sage notices of Act 36 of 2025; malawilii.org Taxation Amendment Bill 2024 (0 % on K1.8 M non-employment income, 30 % above). Record: world/loopholes/africa_mena/search/MW-F1.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- mix.py (wage vs fee split): explained: the model taxes wages and other income on separate schedules because its source does not say how they combine (`unsupported`).
<!-- R2-SCANNERS:END -->
