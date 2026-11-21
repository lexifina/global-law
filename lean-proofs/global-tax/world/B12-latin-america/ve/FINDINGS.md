# Venezuela (VE) 2025: findings (B12-latin-america, build phase 2026-11-20 07:15 UTC)

Model only from the statute; no referee values seen. Scanner scale: none (no statutory amount in bolivares).

### VE-F1 Every amount of the ISLR is in unidades tributarias; the U.T. value is set by SENIAT, outside the law
- kind: statute-fault
- provisions: ISLR arts. 50, 58, 59
- Lean: VeTax.tarifa1, optional input veUT
- note: The real tax depends entirely on an administrative value (not reached): the model needs veUT.
- status: proved in Lean / recorded (build phase)

### VE-F2 With the desgravamen unico (774 U.T.) and the 10 U.T. rebate, about 940 U.T. a year are untaxed
- kind: loophole-known
- provisions: ISLR arts. 50, 58, 59
- Lean: VeTax.taxMilliUT guards
- note: Each dependent adds 10 U.T. of rebate (about 167 U.T. of income at 6 %).
- status: proved in Lean / recorded (build phase)

## Step 4: known ways of paying less, catalogued from the statute

- desgravamen unico vs itemised (recreated: unico)
- family rebates (recreated)
- U.T. erosion by inflation (not modelled: no U.T. series)

## Step 5: what was searched

Literature not checked (web-search budget 0 this session): IMF Article IV and FAD reports, IDB/CIAT tax expenditure and evasion studies, ECLAC Panorama Fiscal, national tax-administration reports, academic papers on the country's income tax. Searched instead: the statute and its amendment notes (provisions listed in the Lean docstrings), the generic scanners (results/search/SUMMARY.md, scale = scale.json), and decide-proofs of every statute-visible threshold.

Generic scanners not run: no statutory scale in local currency (scale.json).

## Model limitations (also in each output's `unsupported`)
See the `unsupported` list in the exe output and results/summary.json.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| VE-F1 | statute-fault | explained | U.T. outside the law; no scan (no scale). |
| VE-F2 | fact | explained | Generic allowance; no money claim. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/VE.json`): no current scan: no scale in bolivares.
