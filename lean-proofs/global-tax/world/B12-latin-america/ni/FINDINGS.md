# Nicaragua (NI) 2025: findings (B12-latin-america, build phase 2026-11-20 07:15 UTC)

Model only from the statute; no referee values seen. Scanner scale: 350,000 NIO (Ley 822 art. 23: the C$ 350.000 limit of the 20 % band).

### NI-F1 The 2012 tariff's one-point-a-year reduction from 2016 was repealed before it began
- kind: statute-fault
- provisions: Ley 822 art. 23 last paragraph; Ley 891 art. 5 a)
- Lean: NiTax.art23
- note: Statute history: the reduction clause never took effect; the 0/15/20/25/30 % tariff stands (as far as the 2014 text reaches).
- status: proved in Lean / recorded (build phase)

### NI-F2 The printed 'impuesto base' column equals the band sums: no jump
- kind: loophole-known
- provisions: Ley 822 art. 23
- Lean: NiTax.art23_no_jump
- note: Clean tariff; deductions of art. 21 (25 % of expenses up to C$ 20.000).
- status: proved in Lean / recorded (build phase)

## Step 4: known ways of paying less, catalogued from the statute

- C$ 100.000 exempt band (recreated)
- art. 21 expense deduction (recreated with input)
- Ley 987/2019 changes (not reached)

## Step 5: what was searched

Literature not checked (web-search budget 0 this session): IMF Article IV and FAD reports, IDB/CIAT tax expenditure and evasion studies, ECLAC Panorama Fiscal, national tax-administration reports, academic papers on the country's income tax. Searched instead: the statute and its amendment notes (provisions listed in the Lean docstrings), the generic scanners (results/search/SUMMARY.md, scale = scale.json), and decide-proofs of every statute-visible threshold.

Generic scanners (quick grid, 0-4 scale): single: peak METR none at 30.0 % scale, bands >100 % 1.43, largest notch 0; single_parent_2: peak METR none at 30.0 % scale, bands >100 % 1.43, largest notch 0; couple_1earner_2: peak METR none at 30.0 % scale, bands >100 % 1.43, largest notch 0.

## Model limitations (also in each output's `unsupported`)
See the `unsupported` list in the exe output and results/summary.json.

### W5R-1 INSS input allotted by wages, not halved (W5 review pass 2, 2026-11-20)
- kind: model-fix
- Pointer: `ni_open_hrms_nicaragua_grid` (first W5 reviewer's open row 41): model above the tool on 138 of 582 dev
  cases, all couples with one earner. The household total `niInss` was halved between the adults, so the earner deducted
  half of his own contributions.
- Statute: Ley 822 art. 21 "Del total de rentas del trabajo no exentas, se autoriza realizar las siguientes deducciones:
  ... 2. Las cotizaciones o aportes de las personas naturales asalariadas en cualquiera de los regímenes de la Seguridad
  Social" (each employee's own contributions, from that employee's rentas del trabajo).
- Change: `niInss` allotted in proportion to wages (halves only when nobody has wages). Only two-adult households with
  the input change (333 of 1,164 checked). Dev: hrms_nicaragua 444 -> 581 / 582 exact; calcular unchanged (101 / 282,
  single adults).
- status: model changed

### W5R-2 décimo tercer mes exemption as an input (art. 19 num. 2)
- kind: model-fix (input; default unchanged)
- Ley 822 art. 19 "Exenciones objetivas ... 2. El décimo tercer mes, o aguinaldo, hasta por la suma que no exceda lo
  dispuesto por el Código del Trabajo" (src/ley822_g241.txt, sha256 017bb80b…). The annual wage does not say whether it
  holds an aguinaldo: input `niThirteenthMonth` (default false; true = 13 equal salaries, the thirteenth, wages / 13,
  exempt; the Código del Trabajo text itself not read). #guard. With the default all 1,164 checked outputs are unchanged.
- Finding (calcular, `ni_open_calcular_grid`): the app spreads the year over 13 pays and taxes the thirteenth like a
  month (its monthly withholding x 13; the misses are constant per band, 5,625 = (30 % x 500,000 - 82,500) / 12), i.e.
  it does not apply art. 19 num. 2; with `niThirteenthMonth` the model is below it. Software error (art. 19 num. 2) plus
  the app's monthly-projection method.
- status: model changed (input); finding recorded

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| NI-F1 | statute-fault | proved | Statute history (builder). Evidence: model Lean: NiTax.art23. |
| NI-F2 | fact | proved | Model theorem. Evidence: model Lean: NiTax.art23_no_jump. |
| W5R-1 | record | explained | Record (model-fix): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5R-2 | record | explained | Record (model-fix (input; default unchanged)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/NI.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
