# El Salvador (SV) 2025 (D.L. 293/2025 reform applied to the whole year): findings (B12-latin-america, build phase 2026-11-20 07:15 UTC)

Model only from the statute; no referee values seen. Scanner scale: 10,742 USD (LISR art. 37 as reformed by D.L. 293/2025 (Decreto Ejecutivo No. 10/2025 annual table, official secondary): the US$ 10.742,86 limit of tramo II).

### SV-F1 Entering tramo II costs US$ 212,12 at once (fixed amount at the first cent above US$ 6.600)
- kind: statute-fault
- provisions: LISR art. 37 (D.E. 10/2025 table)
- Lean: SvTax.entry_notch, SvTax.art37_jumps
- note: Scanner: notch of US$ 211 at a wage of US$ 8.200 (6.600 + the 1.600 deduction), METR 396 %.
- status: proved in Lean / recorded (build phase)

### SV-F2 The US$ 1.600 deduction is lost in full one dollar above US$ 9.100 of salary: US$ 160 more tax
- kind: loophole-known
- provisions: LISR art. 29 num. 7 (as quoted in D.E. 10 art. 1 e)
- Lean: SvTax.deduction_notch
- note: All-or-nothing deduction.
- status: proved in Lean / recorded (build phase)

### SV-F3 At US$ 10.742,86 the printed fixed amount (720,00) is US$ 93,59 above the tramo II sum
- kind: statute-fault
- provisions: LISR art. 37 (D.E. 10/2025 table)
- Lean: SvTax.tramo3_notch
- note: A third notch; whether art. 37 itself prints these figures needs D.L. 293/2025 (not reached).
- status: proved in Lean / recorded (build phase)

### SV-F4 The Ministry's consolidated LISR file (DC5101) still showed reforms to 2007 in colones in 2024
- kind: gov-error
- provisions: mh.gob.sv DC5101_19_Ley_de_Impuesto_sobre_la_Renta.pdf
- Lean: -
- note: An outdated official consolidation; citizens cannot read the 2011 or 2025 tariff there.
- status: proved in Lean / recorded (build phase)

## Step 4: known ways of paying less, catalogued from the statute

- US$ 212 entry notch (recreated, proved)
- US$ 1.600 deduction cliff (recreated, proved)
- tramo III step (recreated)
- 25 % cap of the 1991 text (status unverified: not modelled)

## Step 5: what was searched

Literature not checked (web-search budget 0 this session): IMF Article IV and FAD reports, IDB/CIAT tax expenditure and evasion studies, ECLAC Panorama Fiscal, national tax-administration reports, academic papers on the country's income tax. Searched instead: the statute and its amendment notes (provisions listed in the Lean docstrings), the generic scanners (results/search/SUMMARY.md, scale = scale.json), and decide-proofs of every statute-visible threshold.

Generic scanners (quick grid, 0-4 scale): single: peak METR none at 396.3 % scale, bands >100 % 0.76, largest notch 3; single_parent_2: peak METR none at 396.3 % scale, bands >100 % 0.76, largest notch 3; couple_1earner_2: peak METR none at 396.3 % scale, bands >100 % 0.76, largest notch 3.

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

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| SV-F1 | statute-fault | model-proved | 212 USD for one dollar at 8,200 of pay. exe and #guard L1SV.F1; model theorems. Evidence: exe + Lean `L1SV.F1` (`world/loopholes/rest/lean/L1SV.lean`, 1 #guard): tot(b)-tot(a) = 212; model Lean: SvTax.entry_notch, art37_jumps. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| SV-F2 | loophole | confirmed | 160 USD for one dollar at 9,100 of salary. exe and #guard L1SV.F2. Evidence: exe + Lean `L1SV.F2` (`world/loopholes/rest/lean/L1SV.lean`, 1 #guard): tot(b)-tot(a) = 160; statute re-read: `src/ocr/de10-3.txt`; model Lean: SvTax.deduction_notch. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| SV-F3 | statute-fault | model-proved | 94 USD at 10,742-10,743. exe and #guard L1SV.F3. Evidence: exe + Lean `L1SV.F3` (`world/loopholes/rest/lean/L1SV.lean`, 1 #guard): tot(b)-tot(a) = 94; model Lean: SvTax.tramo3_notch. |
| SV-F4 | gov-error | explained | Outdated consolidation (builder). |
| W5R | record | explained | Record (model-fix (cross-country sweep from NI W5R-1)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/SV.json`): METR 183-413 % and notches 211 / 159 / 93 = SV-F1, SV-F2, SV-F3 (couple multiples).
