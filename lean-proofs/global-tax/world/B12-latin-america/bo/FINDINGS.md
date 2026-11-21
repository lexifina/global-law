# Bolivia (BO) 2025: findings (B12-latin-america, build phase 2026-11-20 07:15 UTC)

Model only from the statute; no referee values seen. Scanner scale: 132,000 BOB (Ley 843 art. 26 and D.S. 21531 art. 8: four Salarios Minimos Nacionales a month (4 x Bs 2.750, D.S. 5383 art. 7) x 12, the effective RC-IVA exemption level).

### BO-F1 The 2 SMN minimum and the 13 % credit on 2 SMN together exempt wages up to 4 SMN (Bs 11.000 a month)
- kind: loophole-known
- provisions: Ley 843 art. 26; D.S. 21531 art. 8 c) 2
- Lean: BoTax.exempt_up_to_four_smn, BoTax.flat_above
- note: Above that the RC-IVA is a flat 13 % of the excess, reducible by 13 % of invoices presented.
- status: proved in Lean / recorded (build phase)

### BO-F2 SIN's link 'Ley N 843 - Texto Ordenado ... 30-09-2014' serves Ley 843 of 24-10-2016 (a CAF loan law)
- kind: gov-error
- provisions: impuestos.gob.bo/index.php/leyes/ -> wp-content/uploads/2025/11/LEY843.pdf
- Lean: -
- note: Both the 2014 and the 2018 'Leyes 843 y 2492' entries point to the wrong file. Draft note: 'The link for Ley 843 (Texto Ordenado) on the Leyes page opens Ley 843/2016 (loan contract with CAF); please link the Texto Ordenado.'
- status: proved in Lean / recorded (build phase)

### BO-F3 Dividends are outside the RC-IVA while wages pay 13 %
- kind: loophole-known
- provisions: Ley 843 art. 19 c)
- Lean: BoTax.out detail
- note: Owner-managers can take profits as dividends (IUE company side not modelled).
- status: proved in Lean / recorded (build phase)

### BO-F4 SIN's decree list dates D.S. 5503 '17-12-2026' under year 2025
- kind: gov-error
- provisions: impuestos.gob.bo/index.php/decretos/
- Lean: -
- note: A date typo on the list; the decree's 20 % extra invoice credit runs from its publication to 2027.
- status: proved in Lean / recorded (build phase)

## Step 4: known ways of paying less, catalogued from the statute

- effective 4 SMN exemption (recreated, proved)
- invoice credit (recreated with input)
- dividends outside RC-IVA (recreated)
- term-deposit interest exclusions (not modelled)

## Step 5: what was searched

Literature not checked (web-search budget 0 this session): IMF Article IV and FAD reports, IDB/CIAT tax expenditure and evasion studies, ECLAC Panorama Fiscal, national tax-administration reports, academic papers on the country's income tax. Searched instead: the statute and its amendment notes (provisions listed in the Lean docstrings), the generic scanners (results/search/SUMMARY.md, scale = scale.json), and decide-proofs of every statute-visible threshold.

Generic scanners (quick grid, 0-4 scale): single: peak METR none at 13.0 % scale, bands >100 % 1.0, largest notch 0; single_parent_2: peak METR none at 13.0 % scale, bands >100 % 1.0, largest notch 0; couple_1earner_2: peak METR none at 13.0 % scale, bands >100 % 1.0, largest notch 0.

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
- provisions: Ley 065 de Pensiones arts. 83 b), 87 b) and f), 88, 151 a), glossary "Total Ganado" (60 SMN); D.S. 778 annex table (Riesgo Común 1,71 %, Comisión 0,50 %) (aps.gob.bo)
- SIP employee contributions 12.71 % (11 % from 65) of the monthly wage up to 60 SMN (Bs 165.000) plus the Aporte Nacional Solidario 1 / 5 / 10 % over Bs 13.000 / 25.000 / 35.000, when boEmployeeContrib is not given; deducted under Ley 843 art. 25. Before W5 the model booked no such contribution (or only an optional input); the W5a grids and the pattern A sweep flagged it (IMPROVE_W5 pattern A, `w5/pa/SWEEP.md`). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS. Open: SIP: ANS thresholds as printed in 2019 (updates not checked).
- status: fixed

### W5S4-1 arte-contable-app RC-IVA (SergioYucra): 13 % of one SMN as the credit, not two (reading) (W5 review pass 4, 2026-11-20)
- kind: software-error
- `bo_open_arte_contable_sergioyucra_grid`: the tool's computed credit is 13 % of one SMN (it cites D.S. 5383, the 2025 minimum-wage decree); Ley 843 art. 26 and D.S. 21531 art. 8 as read for the model give the employee 13 % of two SMN. Dev: tool above by 13 % x 2,750 x 12 = 4,290 a year wherever tax is due (-4,267..-4,291).
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| BO-F1 | fact | confirmed | exe and #guard L1BO.F1 (0 at 132,000 with and without W5 contributions); Ley 843 art. 26 re-read ('dos salarios mínimos'). Design, not a loophole. Evidence: exe + Lean `L1BO.F1` (`world/loopholes/rest/lean/L1BO.lean`, 3 #guard): it(a) = 0; it(b) = 2; it(c) = 0; statute re-read: `src/l843_raw.txt`; model Lean: BoTax.exempt_up_to_four_smn, flat_above. |
| BO-F2 | gov-error | explained | Wrong link (builder). |
| BO-F3 | loophole | model-proved | 0 RC-IVA on dividends vs 13 % on wages. exe and #guard L1BO.F3. Evidence: exe + Lean `L1BO.F3` (`world/loopholes/rest/lean/L1BO.lean`, 1 #guard): it(a) = 0. Known/new: **known**: pattern: income shifting between wages and dividends by owner-managers (Harju & Matikka 2016, International Tax and Public Finance, 10.1007/s10797-016-9393-4); the country's dividend rate is published. |
| BO-F4 | gov-error | explained | Date typo (builder). |
| W5R | record | explained | Record (model-fix (cross-country sweep from NI W5R-1)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/BO.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= BO-F3).
