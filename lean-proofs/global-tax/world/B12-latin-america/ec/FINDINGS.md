# Ecuador (EC) 2025: findings (B12-latin-america, build phase 2026-11-20 07:15 UTC)

Model only from the statute; no referee values seen. Scanner scale: 26,422 USD (LRTI art. 36 a) Tabla No. 1 Ano 2025: the 26.422 USD fraccion basica (15 % row)).

### EC-F1 The printed 2025 table's fixed amounts are rounded band sums: steps of +0,72 and -0,55 USD at thresholds
- kind: statute-fault
- provisions: LRTI art. 36 a) (Res. NAC-DGERCGC24-00000041)
- Lean: EcTax.tabla_jumps, EcTax.tabla_close
- note: Immaterial (under one dollar) but the literal table is not monotone at 108.810 USD (falls 0,55).
- status: proved in Lean / recorded (build phase)

### EC-F2 The personal-expense rebate is 18 % of expenses up to 7 canastas, not a deduction
- kind: loophole-known
- provisions: LRTI art. (...) after art. 10
- Lean: EcTax.person (rebate)
- note: Worth the same to every taxpayer with tax to absorb; lost if the tax is smaller (no refund).
- status: proved in Lean / recorded (build phase)

## Step 4: known ways of paying less, catalogued from the statute

- rebate capped at 7 canastas (recreated, needs inputs)
- extra fraccion basica for 65+ (recreated)
- dependants' table of canastas (not reached)

## Step 5: what was searched

Literature not checked (web-search budget 0 this session): IMF Article IV and FAD reports, IDB/CIAT tax expenditure and evasion studies, ECLAC Panorama Fiscal, national tax-administration reports, academic papers on the country's income tax. Searched instead: the statute and its amendment notes (provisions listed in the Lean docstrings), the generic scanners (results/search/SUMMARY.md, scale = scale.json), and decide-proofs of every statute-visible threshold.

Generic scanners (quick grid, 0-4 scale): single: peak METR none at 35.6 % scale, bands >100 % 3.13, largest notch 0; single_parent_2: peak METR none at 35.6 % scale, bands >100 % 3.13, largest notch 0; couple_1earner_2: peak METR none at 35.6 % scale, bands >100 % 3.13, largest notch 0.

## Model limitations (also in each output's `unsupported`)
See the `unsupported` list in the exe output and results/summary.json.

### W5R sweep P2-6: household-total employee-contribution input allotted by wages (W5 review pass 2, 2026-11-20)
- kind: model-fix (cross-country sweep from NI W5R-1)
- The optional household-total employee-contribution input was halved between two adults, so a one-earner couple
  deducted half of the earner's own contributions. The deduction provision this model already cites deducts each
  employee's own contributions from that employee's income; the total is now allotted in proportion to wages (halves
  only when nobody has wages). Checked on 400 random households: outputs change only for two adults with the input and
  unequal wages. Script: world/w5/review2/sweep_alloc.py. Rescanned (scan_world.py).
- status: model changed

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: IESS Resolución C.D. 515 (30 Mar 2016) Anexo Único, Primera (private-sector dependent workers 9,45 / 11,15 / 20,60), replacing C.D. 501; Ley de Seguridad Social (iess.gob.ec)
- personal IESS 9.45 % of wages when ecIessPersonal is not given; deducted (LRTI); now also reported as employeeSocial. Before W5 the model booked no such contribution (or only an optional input); the W5a grids and the pattern A sweep flagged it (IMPROVE_W5 pattern A, `w5/pa/SWEEP.md`). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS. Open: IESS: later C.D. resolutions not checked for the private-sector totals; public-sector table not applied.
- status: fixed

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| EC-F1 | statute-fault | proved | Model theorems; under one dollar. Evidence: model Lean: EcTax.tabla_jumps, tabla_close. |
| EC-F2 | fact | explained | Rebate design (fact). |
| W5R | record | explained | Record (model-fix (cross-country sweep from NI W5R-1)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/EC.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
