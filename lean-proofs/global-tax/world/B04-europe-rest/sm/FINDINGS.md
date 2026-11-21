# SM findings (San Marino (imposta generale sui redditi, Titolo II, 2025 wording), 2025)

Batch B04-europe-rest, built 2026-11-20 02:40 UTC. Status: built (no referee values used). Scanner output: `results/search/SUMMARY.md` (statutory scale 40 000 EUR = the end of the Allegato C C1 c. 3 deduction taper); leads: single|none: max 60.5 %, average 60.5 % (top 35.0 %) from 16,000 to 16,200 (0.4-0.405 AW); causes: taxableIncome, credits, taxBeforeCredits; single|dividends_1AW: max 60.5 %, average 60.5 % (top 35.0 %) from 16,000 to 16,200 (0.4-0.405 AW); causes: taxableIncome, credits, taxBeforeCredits; single_parent_2|none: max 60.5 %, average 60.5 % (top 35.0 %) from 16,000 to 16,200 (0.4-0.405 AW); causes: taxableIncome, credits, taxBeforeCredits

### F1 The 9 000 € deduction is withdrawn between 9 000 and 40 000 €
- kind: observation (structure)
- status: proved

Allegato C C1 c. 3 (2013 text): 9 000 € × (40 000 − income)/31 000, ratio truncated to 4 decimals; each euro inside the band removes 0,29 € of deduction, so the marginal rate is the band rate × 1,29 (`SmTax.c3_points`, `taper_marginal_above_band`).

### F2 The 100 € credit for incomes up to 15 000 € is a cliff
- kind: loophole-new (structure; not found in the sources read)
- status: lead checked against the statute

Art. 16 c. 9 (2025 wording): 100 € off the tax for art. 24-26 taxable income 'fino ad euro 15.000,00', nothing above. Scanner (scale 40 000): METR 60,5 % on gross pay 16 000-16 200 € (the taxable income crosses 15 000 € there after the 7 % abatement).

### F3 Reading R1: which text applied in 2025
- kind: reading
- status: reading

Art. 148 c. 8 keeps the old wording of arts. 13, 16, 17, 25, 102-104 to 31 December 2025; Allegato C c. 3 and the old art. 14 (spending deduction) are read as in force for 2025 too, because the new art. 16 c. 8 bis SMaC credit that replaces them is itself kept out of 2025 by art. 148 c. 8. The general commencement article of Legge 141/2025 was not reached.

### F4 Assumptions and gaps
- kind: model limitation
- status: open

SMaC / electronic spending in San Marino (art. 14 c. 1 a) is an optional input `sm_smacSpending`, default none (assumption recorded in `unsupported`). Employee social-security contributions (deductible under art. 24 c. 4) are not in the Global law record: input `sm_employeeContributions`, default not computed. A spouse counts as dependent only with no income (the social-pension limit of art. 16 c. 3 was not cited). Separate taxation (art. 13), withholding on capital income (arts. 102-104) and rent not modelled.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | fact | proved | Model theorems. Evidence: model Lean: SmTax.c3_points, taper_marginal_above_band. |
| F2 | loophole | confirmed | 100 EUR for one euro at 16,129-16,130 of pay (taxable income crossing 15,000). exe and #guard L1SM.F2. Evidence: exe + Lean `L1SM.F2` (`world/loopholes/rest/lean/L1SM.lean`, 1 #guard): tot(b)-tot(a) = 100; statute re-read: `src/igr_166-2013_current.md`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F3 | reading | lead | Reading (reading): open as the builder left it; no amount depends on it in L1. |
| F4 | record | explained | Record (model limitation): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/SM.json`): notches 99 at 16,129 / 26,882 / 40,323 = F2 (couples); notch 399 at the second earner's first euro = the model's dependent-spouse test (spouse dependent only with no income, F4 assumption); bands 61-63.5 % = F1 taper.
