# RS findings (Serbia (porez na zarade, porez na prihode od kapitala, doprinosi; godišnji porez na dohodak građana), 2025)

Batch B04-europe-rest, built 2026-11-20 02:40 UTC. Status: built (no referee values used). Scanner output: `results/search/SUMMARY.md` (statutory scale 1 364 304 RSD = 12 × 4 × the monthly non-taxable amount 28 423); leads: no METR band above 100 % and no notch above 0.1 % of the scale

### F1 Monthly salary tax without annual reconciliation
- kind: loophole-known (structure)
- status: proved

Each month's 28 423 RSD non-taxable amount is lost if not used: 600 000 RSD paid evenly pays 25 896 RSD, paid in one month 57 158 RSD (`RsTax.uneven_costs_more`).

### F2 The annual tax is an overlay without credit, with a young-taxpayer reduction
- kind: observation (structure)
- status: proved (structure)

Čl. 87-89: 10 %/15 % on net income above 3 average annual salaries, after personal deductions (40 % + 15 % per dependant of the average salary, at most 50 % of the income); under-40s deduct a further 3 average salaries from pay (čl. 87 st. 4). Lean `annual_zero_below_3A`, `annual_under40_zero_below_6A` (illustrative average). Computed only when `rs_avgAnnualSalary` is given.

### F3 Global law prints the indexed dinar amounts in the text with their dates
- kind: lesson (source)
- status: noted

The publisher's note dates every harmonised amount (e.g. 8/2025 from 1 February 2025); čl. 15a (28 423) was set by 94/2024 and unchanged until 109/2025 (2026).

### F4 Unsupported 2025 amounts
- kind: model limitation
- status: open

The 2025 average annual salary (čl. 87-89) and the minimum/maximum monthly contribution bases (Zakon o doprinosima čl. 37-42) are published amounts that were not reached; listed in `unsupported` for every household.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | loophole | proved | 31,262 RSD: 600,000 paid in one month pays 57,158, evenly 25,896. Model theorem. Known pattern. Evidence: model Lean: RsTax.uneven_costs_more. Known/new: **unclear**: pattern: final (non-cumulative) withholding penalises uneven pay; no description found in the Crossref record (hits on withholding were unrelated). |
| F2 | fact | proved | Model theorems (illustrative average). Evidence: model Lean: RsTax.annual_zero_below_3A, annual_under40_zero_below_6A. |
| F3 | record | explained | Record (lesson (source)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| F4 | record | explained | Record (model limitation): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/RS.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
