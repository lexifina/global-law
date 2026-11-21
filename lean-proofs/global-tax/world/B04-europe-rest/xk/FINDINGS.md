# XK findings (Kosovo (tatimi në të ardhurat personale; kontributi pensional i punonjësit), 2025)

Batch B04-europe-rest, built 2026-11-20 02:40 UTC. Status: built (no referee values used). Scanner output: `results/search/SUMMARY.md` (statutory scale 10 800 EUR = 2 × the start of the 10 % band); leads: single|none: max 14.8 %, average 14.8 % (top 13.9 %) from 5,994 to 6,048 (0.555-0.56 AW); causes: taxableIncome, pensionContribution; single|none: max 14.8 %, average 14.8 % (top 13.9 %) from 6,372 to 6,426 (0.59-0.595 AW); causes: taxableIncome, pensionContribution; single|none: max 16.7 %, average 16.7 % (top 13.9 %) from 6,804 to 6,858 (0.63-0.635 AW); causes: taxableIncome, pensionContribution

### F1 The printed rate table is exact
- kind: observation (statute check)
- status: proved

08/L-142 prints 192 € at 5 400 (8 % of 2 400): `XkTax.printed_eq_bands`, `printed_no_jumps`.

### F2 The 2024 reform is worth 81,60 € to every taxpayer above 3 000 € and never raises tax
- kind: observation (reform)
- status: proved

Removing the 4 % band (960-3 000) and the zero band below 960: `reform_never_worse`, `reform_gain_above_3000`.

### F3 Withholding refers to the annual table
- kind: reading
- status: reading

Neni 38 (2) withholds 'në përputhje me shkallët parapara në nenin 6' (the annual table) each payroll period; the model applies the annual table to the year, which equals monthly withholding at 1/12 of the bands for equal monthly pay. The administrative instruction (UA 01/2016) that sets the monthly amounts was not read.

### F4 Global law: file names offset from article numbers
- kind: lesson (source)
- status: noted

In kosovo/national/acts/ligje/05-l-028 the file neni-007.md holds 'Neni 9' (and so on): cite the heading printed in the text, not the file name.

### F5 Model limits
- kind: model limitation
- status: open

Dividends exempt (neni 8 (1) 1.26) and Government pensions exempt (1.13) are modelled; rent at 90 % (neni 27 lump sum), interest and capital gains in the annual base; the presumptive regime for small businesses, the minimum-wage floor of the pension contribution (minimum wage not cited) are not modelled.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | fact | proved | Model theorems. Evidence: model Lean: XkTax.printed_eq_bands, printed_no_jumps. |
| F2 | fact | proved | Model theorems. Evidence: model Lean: XkTax.reform_never_worse, reform_gain_above_3000. |
| F3 | reading | explained | Fresh scan: bands 14.8-16.7 % above the 13.9 % top are whole-euro rounding of the pension contribution and tax (no notch). |
| F4 | record | explained | Record (lesson (source)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| F5 | record | explained | Record (model limitation): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/XK.json`): bands 14.8-16.7 % above 13.9 % = whole-euro rounding (F3); no notch.
