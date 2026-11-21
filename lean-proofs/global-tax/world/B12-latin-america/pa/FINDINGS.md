# Panama (PA) 2025: findings (B12-latin-america, build phase 2026-11-20 07:15 UTC)

Model only from the statute; no referee values seen. Scanner scale: 50,000 PAB (Codigo Fiscal art. 700 (Ley 8/2010 art. 10): the B/. 50.000 limit of the 15 % band).

### PA-F1 Art. 700: 0 % to B/. 11.000, 15 % to B/. 50.000, B/. 5.850 + 25 % above; the column is exact
- kind: loophole-known
- provisions: Codigo Fiscal art. 700
- Lean: PaTax.art700_no_jump
- note: No notch; individual taxation.
- status: proved in Lean / recorded (build phase)

## Step 4: known ways of paying less, catalogued from the statute

- B/. 11.000 exempt band (recreated)
- territorial taxation of foreign income (not modelled: source rule not read)

## Step 5: what was searched

Literature not checked (web-search budget 0 this session): IMF Article IV and FAD reports, IDB/CIAT tax expenditure and evasion studies, ECLAC Panorama Fiscal, national tax-administration reports, academic papers on the country's income tax. Searched instead: the statute and its amendment notes (provisions listed in the Lean docstrings), the generic scanners (results/search/SUMMARY.md, scale = scale.json), and decide-proofs of every statute-visible threshold.

Generic scanners (quick grid, 0-4 scale): single: peak METR none at 25.2 % scale, bands >100 % 1.0, largest notch 0; single_parent_2: peak METR none at 25.2 % scale, bands >100 % 1.0, largest notch 0; couple_1earner_2: peak METR none at 25.2 % scale, bands >100 % 1.0, largest notch 0.

## Model limitations (also in each output's `unsupported`)
See the `unsupported` list in the exe output and results/summary.json.

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: Ley 462 de 18/03/2025 (G.O. 30238) art. 84 replacing Ley 51/2005 art. 101 (1)
- CSS employee 9.75 % of wages (no ceiling); not deducted (Codigo Fiscal deductions not read). Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| PA-F1 | fact | proved | Model theorem. Evidence: model Lean: PaTax.art700_no_jump. |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/PA.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
