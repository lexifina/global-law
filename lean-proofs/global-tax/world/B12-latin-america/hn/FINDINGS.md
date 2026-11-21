# Honduras (HN) 2025: findings (B12-latin-america, build phase 2026-11-20 07:15 UTC)

Model only from the statute; no referee values seen. Scanner scale: 331,638 HNL (LISR art. 22 b) / Acuerdo SAR-07-2025: the L 331,638.50 upper limit of the 15 % band).

### HN-F1 Wages up to L 257,493 are untaxed (L 217,493.16 exempt band + L 40,000 deduction without receipts)
- kind: loophole-known
- provisions: LISR arts. 13 a), 22 b)
- Lean: HnTax.person
- note: Scanner: 25 % top METR, no notch; individual taxation.
- status: proved in Lean / recorded (build phase)

### HN-F2 The scale is indexed every year to IPC by SAR accord (3.88 % for 2025)
- kind: statute-fault
- provisions: LISR art. 22 b) second paragraph
- Lean: HnTax.tabla2025
- note: Not a fault: recorded so the yearly accord is checked each year.
- status: proved in Lean / recorded (build phase)

## Step 4: known ways of paying less, catalogued from the statute

- L 40,000 deduction without proof (recreated)
- 1.5 % minimum tax on gross income above L 300 m (art. 22-A; not modelled)
- final withholding on interest/dividends (not modelled)

## Step 5: what was searched

Literature not checked (web-search budget 0 this session): IMF Article IV and FAD reports, IDB/CIAT tax expenditure and evasion studies, ECLAC Panorama Fiscal, national tax-administration reports, academic papers on the country's income tax. Searched instead: the statute and its amendment notes (provisions listed in the Lean docstrings), the generic scanners (results/search/SUMMARY.md, scale = scale.json), and decide-proofs of every statute-visible threshold.

Generic scanners (quick grid, 0-4 scale): single: peak METR none at 25.0 % scale, bands >100 % 2.455, largest notch 0; single_parent_2: peak METR none at 25.0 % scale, bands >100 % 2.455, largest notch 0; couple_1earner_2: peak METR none at 25.0 % scale, bands >100 % 2.455, largest notch 0.

## Model limitations (also in each output's `unsupported`)
See the `unsupported` list in the exe output and results/summary.json.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| HN-F1 | fact | model-proved | exe and #guard L1HN.F1 (0 tax at 257,493). Evidence: exe + Lean `L1HN.F1` (`world/loopholes/rest/lean/L1HN.lean`, 2 #guard): it(a) = 0; it(b) = 16. |
| HN-F2 | fact | explained | Not a fault (builder). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/HN.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.


### D9M-1 Earners aged 60-65: the SAR plantilla deducts L70,000 (40,000 + 30,000); the 30,000 has no text on file (D9 review, 2026-11-20) - OPEN
- Grid `hn_official_sar_plantilla_2025_grid` (SAR 'Plantilla para calcular Retención en la Fuente 2025'): dev 938 /
  1,059 exact; all 121 misses are households with an earner aged 60-65 (every case without one is exact), model above
  by 15 / 20 / 25 % x 30,000 per such earner. The plantilla's cell AB: 40,000 under 60, 70,000 at 60-64, 110,000 at 65+,
  and AH: 65+ less 350,000; its notes cite "Artículo 13 literal a, Ley de ISR / Decreto 199-2006, artículo 30 Ley del
  Adulto Mayor. Artículo 1 Decreto 59-2020" and "Artículo 14 Decreto 59-2020".
- Texts read: LISR art. 13 a) (SAR consolidation to Acuerdo SAR-07-2025) and Decreto 59-2020 art. 1 (La Gaceta 35,273,
  4 June 2020; `src/d9/`): L40,000, and L80,000 for "personas mayores de sesenta y cinco (65) años" (the model). Neither
  gives a 60-64 tier or a further 30,000. Decreto 199-2006 art. 30 was reached only as an excerpt headed "DESCUENTOS
  GENERALES" (PAHO compilation): its text was not read. Status: model gap OPEN (text to read: Decreto 199-2006 art. 30
  and any instrument granting adults 60+ L30,000).
- Also seen (no dev case exercises them): Decreto 59-2020 art. 2 rewrites art. 14 of the Ley de Equilibrio Financiero
  (Decreto 194-2002): persons over 65 "con una renta bruta hasta de ... (L. 350,000.00), quedan exentos del pago de este
  impuesto", from the fiscal period in which they turn 65; the model does not apply it (open), and the plantilla
  deducts 350,000 from every 65+ income instead of exempting incomes up to 350,000 (a reading difference to record if
  a case shows it). The model's 80,000 starts above 65 (`age > 65`), the plantilla's at 65.
- provisions: LISR art. 13 a) (Decreto 59-2020 art. 1); Ley de Equilibrio Financiero art. 14 (Decreto 59-2020 art. 2);
  Decreto 199-2006 art. 30 (not read)

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 25.0 % (LISR art. 22 a): 'Las personas jurídicas pagarán una tarifa de veinticinco por ciento (25%) sobre el total de la renta neta gravable' (src/lisr.txt:693-697); th); at a profit of 3 AW the best split costs 15.2 % of the profit, all salary 15.2 %, all dividends 32.5 % (employer contributions: not included); dividends beat salary once employer contributions exceed 30 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
