# Paraguay (PY) 2025: findings (B12-latin-america, build phase 2026-11-20 07:15 UTC)

Model only from the statute; no referee values seen. Scanner scale: 80,000,000 PYG (Ley 6380/2019 arts. 62 and 69: G. 80.000.000, the gross income above which the IRP is due).

### PY-F1 The IRP is due on the whole renta neta once gross income passes G 80.000.000: G 6.052.000 for one guarani
- kind: loophole-known
- provisions: Ley 6380 arts. 62, 69 last paragraph
- Lean: PyTax.threshold_notch
- note: Scanner: METR 1 530 % at 1 scale (G 80 m). The notch shrinks with documented expenses (art. 64).
- status: proved in Lean / recorded (build phase)

### PY-F2 Personal and family consumption is deductible without cap: the IRP is close to a tax on saving
- kind: loophole-known
- provisions: Ley 6380 art. 64 num. 1-4
- Lean: PyTax.expenses_cancel
- note: A worker who documents spending equal to income pays nothing (proved for G 500 m).
- status: proved in Lean / recorded (build phase)

### PY-F3 Capital income and dividends at a flat 8 % against up to 10 % on services
- kind: loophole-known
- provisions: Ley 6380 arts. 43, 60, 69
- Lean: PyTax.out
- note: Small rate gap; dividends also bear IRE 10 % at company level (not modelled).
- status: proved in Lean / recorded (build phase)

## Step 4: known ways of paying less, catalogued from the statute

- 80 m all-or-nothing threshold (recreated, proved)
- unlimited personal-expense deduction (recreated, proved)
- flat 8 % on capital (recreated)
- first-year rule of art. 62 (not modelled)

## Step 5: what was searched

Literature not checked (web-search budget 0 this session): IMF Article IV and FAD reports, IDB/CIAT tax expenditure and evasion studies, ECLAC Panorama Fiscal, national tax-administration reports, academic papers on the country's income tax. Searched instead: the statute and its amendment notes (provisions listed in the Lean docstrings), the generic scanners (results/search/SUMMARY.md, scale = scale.json), and decide-proofs of every statute-visible threshold.

Generic scanners (quick grid, 0-4 scale): single: peak METR none at 1530.2 % scale, bands >100 % 1.0, largest notch 1; single_parent_2: peak METR none at 1530.2 % scale, bands >100 % 1.0, largest notch 1; couple_1earner_2: peak METR none at 1530.2 % scale, bands >100 % 1.0, largest notch 1.

## Model limitations (also in each output's `unsupported`)
See the `unsupported` list in the exe output and results/summary.json.

## Round W2 (improvement agent, 2026-11-20): W1 software-grid dev failures settled from the statute

### W2-1 IPS employee rate: 9 % stands; OpenFisca-Paraguay's 9.5 % has no cited text (software error)
- kind: software-error
- The package's `tasa_empleado_general` rises to 0.095 on 2025-01-01, referenced to "Actualización Régimen General 2025
  (Contribución Solidaria)" without a law or resolution number. The IPS's own rate table (src/ips_tabla_1786135176.jpg,
  headed Resolución MTESS 670/2026) reads "TRABAJADOR 9%". Ley 98/1992 (art. 17 of the IPS charter as amended) was not
  reachable as text this round (BACN search is script-rendered; not in Global law's Paraguay corpus). No change.
- provisions: Ley 98/1992 (not read); IPS rate table
- Lean: PyTax.ipsRate
- status: recorded in software/ISSUES.md (W2); read Ley 98/1992 when reachable

### W5S-1 calcular (Paraguay): IRP on gross pay without the art. 63 exclusion (W5 review pass 2, 2026-11-20)
- kind: software-error
- `py_open_calcular_grid`: the app's IRP note says it taxes 'todo lo cobrado en el año y sin gastos deducibles'; Ley 6380/2019 art. 63 para. 2: 'Para la determinación de la renta bruta se excluirán ... los aportes del trabajador al régimen de jubilaciones y pensiones, o al sistema de seguridad social creado o admitido por ley' (src/l6380page.txt). Its tax is above the model's by 9 % of the IPS (e.g. 658,530 at 81.3 M).
- status: recorded (world/IMPROVE_W5.md pass 2)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| PY-F1 | loophole | model-proved | 6,052,000 PYG for one guaraní of income above 80,000,000. exe and #guard L1PY.F1; model theorem threshold_notch. Evidence: exe + Lean `L1PY.F1` (`world/loopholes/rest/lean/L1PY.lean`, 1 #guard): tot(b)-tot(a) = 6052000; model Lean: PyTax.threshold_notch. Known/new: **new**: Rule published (PwC Paraguay 'Taxes on personal income'; DNIT 'El IRP se debe liquidar en marzo'; Última Hora); none of the hits describes that one guaraní over 80 M taxes the whole renta neta; web search 2 + Crossref. |
| PY-F2 | loophole | model-proved | 0 IRP on 500 M of income with 500 M of documented personal spending. exe and #guard L1PY.F2. Evidence: exe + Lean `L1PY.F2` (`world/loopholes/rest/lean/L1PY.lean`, 1 #guard): it(a) = 0; model Lean: PyTax.expenses_cancel. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| PY-F3 | fact | explained | Small rate gap (8 % vs 10 %). |
| W2-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/PY.json`): METR 1,530 %, notches 6,051,999 and timing 6,052,000-9,909,080 = PY-F1.
