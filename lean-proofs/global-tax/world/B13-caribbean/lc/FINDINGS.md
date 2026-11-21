# Saint Lucia (LC) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 The NIC ceiling of EC$60,000 a year is still the statute's own figure
- kind: gov-error
- NIC Act Schedule 3 para. 1: remuneration 'in excess of $60,000 per annum or such other maximum limit as may be fixed in accordance with section 30(d)'; no regulation fixing another limit is in the 2023 revision. Above 60,000 the employee contribution stops (marginal rate falls by 5 points).
- provisions: NIC Act s. 29, s. 30(d), Schedule 3
- Lean: LcTax.nicAnnual
- status: modelled

### F2 The spouse allowance (EC$1,500) is withdrawn dollar for dollar above EC$1,500 of the spouse's income
- kind: loophole-known
- s. 46(2): 'reduced where the spouse has assessable income in excess of $1,500 by $1 for each dollar of the excess': a 100 % withdrawal band for the second earner between 1,500 and 3,000 (below the personal allowance, so it costs the main earner up to 1,500 x his marginal rate).
- provisions: ITA s. 46
- Lean: LcTax.person
- status: modelled

### F3 NIC and life premiums share a deduction capped at the lower of 10 % of assessable income or EC$8,000
- kind: loophole-known
- s. 53(1)(b), (2): with NIC at 5 % the cap binds only for those buying life cover or deferred annuities; it is a shelter up to 8,000.
- provisions: ITA s. 53
- Lean: LcTax.person
- status: modelled (NIC part)

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Mortgage interest, property tax and home insurance on an owner-occupied home | not modelled: input needed | ITA s. 54 |
| K2 | Life assurance and deferred annuity premiums within the s. 53 cap | not modelled | ITA s. 53 |
| K3 | Education and child maintenance deductions | not modelled | ITA ss. 48-50 |
| K4 | Individual taxation of a married woman's income: split income within the couple | recreated: filing-unit scanner | ITA s. 13 |

## Step 5: what was searched

- kernel scanners with scale 60,000 (NIC ceiling)
- Revised Laws section pages of the ITA and NIC Act (letters i and n listings)

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and technical-assistance reports for the Caribbean (tax policy diagnostics, CARTAC papers)
- CARICOM / OECS / ECCB papers on income-tax harmonisation and social-security reform in the Eastern Caribbean
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Inter-American Development Bank and CIAT/ECLAC (CEPAL) studies of personal income tax in Latin America and the Caribbean
- Academic work on Caribbean PAYE design, social-security contribution ceilings and the effect of thresholds on low earners
- Official tax calculators and withholding tables (referee material for the dataset phase: deliberately not read)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Round D7 (improvement agent, 2026-11-20)

### D7-1 The IRD calculator's 25,400 is its tax-code convention, not the Act: `--ird-code` flag, statute unchanged
- kind: convention
- Statute: Income Tax Act Cap. 15.02 s. 45, Schedule 6: "2023 | $ 25,000 effective 1 January, 2023" (Act 21 of 2022);
  ss. 44-59 (Revised Edition, law as at 31 December 2023) contain no further fixed 400 allowance. No later Act raising
  the allowance was found. The model's 25,000 stays.
- The IRD's published method (its PAYE calculator, irdstlucia.gov.lc/payecalculator, law/d7/ird_paye_calculator_page.html,
  sha256 23b3acad..., the same file the test registered): "const allowance = digits * 100", default code "254M", and the
  note "the allowance code itself changed alongside the rate change (184M -> 254M)". The code carries 400 above Schedule 6
  in both periods (18,000 -> 184; 25,000 -> 254): an IRD coding convention whose basis the page does not state.
- Change: `--ird-code` (allowance 25,400), declared per dataset for the two IRD calculator grids with the citation (rule 8).
  Dev (local rerun, D7 exe vs current): statute 57 / 209 / 272 (unchanged); convention 272 / 272 / 272. Statute outputs
  unchanged on 300 random households. Finding: PAYE withheld with the default code under-withholds by the tax on 400 a year
  (60 / 80 / 120) relative to the Act, settled on assessment.
- status: convention flag added

### W5S4-1 caribbean-payroll (oecstrading), LC config: PAYE without the NIC deduction; NIC from age 60 (reading) (W5 review pass 4, 2026-11-20)
- kind: software-error
- `lc_open_caribbean_payroll_oecstrading_grid`: bands and allowance are the statute's, but the PAYE base deducts no NIC: Income Tax Act s. 53(1)(b), (2) (contributions under the NIC Act with life premiums, up to the lower of 10 % or 8,000), dev -900 = 30 % x 3,000; NIC Act s. 27(1)(b): persons over 60 do not contribute, the tool charges them (dev -3,000). Reading: s. 53 is an allowance on assessment; a PAYE table may ignore it (P2-2 if the tool is read as withholding).
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | gov-error | explained | Ceiling unchanged (builder). |
| F2 | loophole | model-proved | 450 XCD more tax on the main earner when the spouse's income rises from 1,500 to 3,000 (100 % withdrawal at the 30 % rate). exe and #guard L1LC.F2; s. 46 text not located by pattern (the hit was s. 52, dependent relatives). Evidence: exe + Lean `L1LC.F2` (`world/loopholes/rest/lean/L1LC.lean`, 1 #guard): it(b)-it(a) = 450. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F3 | fact | explained | Cap (fact). |
| D7-1 | record | explained | Record (convention): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/LC.json`): notches of 1 = rounding; marriage bonus 450 = F2; income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
