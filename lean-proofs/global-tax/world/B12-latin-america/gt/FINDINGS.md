# Guatemala (GT) 2025: findings (B12-latin-america, build phase 2026-11-20 07:15 UTC)

Model only from the statute; no referee values seen. Scanner scale: 300,000 GTQ (Decreto 10-2012 art. 73: the Q 300.000 limit of the 5 % band).

### GT-F1 Wages up to Q 48.000 (plus up to Q 12.000 of VAT paid and IGSS) are untaxed; then 5 % to Q 300.000 and 7 % above
- kind: loophole-known
- provisions: Decreto 10-2012 arts. 72, 73
- Lean: GtTax.art73_no_jump, GtTax.art73_is_bands
- note: The printed Q 15.000 is exact: no jump.
- status: proved in Lean / recorded (build phase)

### GT-F2 Capital income 10 % and dividends 5 % beside labour at 5-7 %
- kind: loophole-known
- provisions: arts. 73, 92, 93
- Lean: GtTax.out
- note: For employees capital income is taxed more than labour; the gap runs the other way for owner-managers only through the company tax (not modelled).
- status: proved in Lean / recorded (build phase)

## Step 4: known ways of paying less, catalogued from the statute

- Q 48.000 flat deduction (recreated)
- Q 12.000 VAT deduction (recreated with input)
- aguinaldo/Bono 14 exemption (not modelled)

## Step 5: what was searched

Literature not checked (web-search budget 0 this session): IMF Article IV and FAD reports, IDB/CIAT tax expenditure and evasion studies, ECLAC Panorama Fiscal, national tax-administration reports, academic papers on the country's income tax. Searched instead: the statute and its amendment notes (provisions listed in the Lean docstrings), the generic scanners (results/search/SUMMARY.md, scale = scale.json), and decide-proofs of every statute-visible threshold.

Generic scanners (quick grid, 0-4 scale): single: peak METR none at 7.0 % scale, bands >100 % 1.16, largest notch 0; single_parent_2: peak METR none at 7.0 % scale, bands >100 % 1.16, largest notch 0; couple_1earner_2: peak METR none at 7.0 % scale, bands >100 % 1.16, largest notch 0.

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

### W5R-1 aguinaldo and Bono 14 exemption as an input (art. 70 num. 5, 6; W5 review pass 2, 2026-11-20)
- kind: model-fix (input; default unchanged)
- Decreto 10-2012 art. 70: "Están exentas del impuesto: ... 5. El aguinaldo hasta el cien por ciento (100%) del sueldo o
  salario ordinario mensual. 6. La bonificación anual ... hasta el cien por ciento (100%) del sueldo o salario ordinario
  mensual" (src/d10_2012.txt, sha256 4610b593…). Input `gtFourteenPays` (default false); true = wages are 14 equal
  payments, 2 x wages / 14 exempt. #guard. Default outputs unchanged on 580 households.
- `gt_open_calcular_grid` (14 pays in the app): 60 -> 68 / 280 exact with the input; the remaining misses (constant 400 /
  1,560 without it) are not explained by the exemption alone: open (the app's own withholding method not traced).
- status: model changed (input); grid open

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: IGSS Junta Directiva Acuerdo 410 art. 62 b) (rev. 2018), Acuerdo 1002 art. 46 b), Acuerdo 1124 art. 40 b) (rev. 2021) (igssgt.org)
- IGSS employee 4.83 % of wages (2 % EM + 1 % accidents + 1.83 % IVS) when gtIgss is not given; deducted under art. 72. Before W5 the model booked no such contribution (or only an optional input); the W5a grids and the pattern A sweep flagged it (IMPROVE_W5 pattern A, `w5/pa/SWEEP.md`). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS. Open: IGSS on all fourteen payments with gtFourteenPays (contribution status of aguinaldo / Bono 14 not read).
- status: fixed

### W5S-1 calcular (manu-180): aguinaldo and Bono 14 taxed (W5 review pass 3, 2026-11-20)
- kind: software-error
- `gt_open_calcular_fourteenpays_grid` (rebuild of gt_open_calcular_grid with `gtFourteenPays: true`, the coordinator's
  extra-month rule: the app pays 14): the app taxes the aguinaldo and Bono 14 like monthly salary, so above the ISR
  threshold it is above the model in every case (207 of 292 dev cases, all one side); the gap is about 7 % x 2/14 of the
  gross (1,566,000: app 169,043, model 154,943 = ISR 79,305 + IGSS 75,638), less the constant 1,560 / 400 already seen on
  row 77 (not traced).
- provisions: Decreto 10-2012 art. 70 num. 5 (aguinaldo up to 100 % of the monthly salary) and num. 6 (Bono 14 up to 100 %)
- status: recorded (world/IMPROVE_W5.md pass 3); the 1,560 / 400 constants open

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| GT-F1 | fact | proved | Model theorems. Evidence: model Lean: GtTax.art73_no_jump, art73_is_bands. |
| GT-F2 | fact | model-proved | exe and #guard L1GT.F2 (5 % on dividends). Evidence: exe + Lean `L1GT.F2` (`world/loopholes/rest/lean/L1GT.lean`, 1 #guard): tot(a) = 5000. |
| W5R | record | explained | Record (model-fix (cross-country sweep from NI W5R-1)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5R-1 | record | explained | Record (model-fix (input; default unchanged)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/GT.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
