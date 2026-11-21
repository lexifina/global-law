# Peru (PE) 2025 (ejercicio gravable 2025): findings (B12-latin-america, build phase 2026-11-20 07:15 UTC)

Model only from the statute; no referee values seen. Scanner scale: 107,000 PEN (LIR art. 53: the 20 UIT threshold of the progressive scale at the 2025 UIT of S/ 5 350 (D.S. 260-2024-EF art. 1)).

### PE-F1 Labour income up to 7 UIT (S/ 37 450) is untaxed; above it 8-30 % in UIT bands
- kind: loophole-known
- provisions: LIR arts. 46, 53
- Lean: PeTax.art53, PeTax.art53_thresholds
- note: Scanner: peak METR 43,2 % (30 % + 13 % SNP) from 45 UIT net; no notch, no band above the top rate.
- status: proved in Lean / recorded (build phase)

### PE-F2 Deposit interest exempt to 31-12-2026, capital income flat 6,25 %, dividends 5 % against 30 % on labour
- kind: loophole-known
- provisions: LIR arts. 19 i, 52-A, 53; D.Leg. 1549
- Lean: PeTax.person (capitalTax, dividendTax)
- note: Income-type gap of up to 25 points for an owner-manager (company tax side not modelled; harness company.json has no PE entry).
- status: proved in Lean / recorded (build phase)

### PE-F3 The additional deduction of up to 3 UIT needs electronic receipts and counts only 30 % of rent and fees
- kind: loophole-known
- provisions: LIR art. 46 second and fourth-last paragraphs
- Lean: optional input peDeductibleExpenses
- note: Choice of how to pay (receipted, bank means of payment) changes the tax: up to S/ 16 050 x marginal rate.
- status: proved in Lean / recorded (build phase)

## Step 4: known ways of paying less, catalogued from the statute

- 7 UIT allowance and tariff structure (recreated)
- deposit-interest exemption (recreated)
- capital vs labour rate gap (recreated for the individual side)
- gratificaciones outside SNP base, Ley 30334 (not modelled)

## Step 5: what was searched

Literature not checked (web-search budget 0 this session): IMF Article IV and FAD reports, IDB/CIAT tax expenditure and evasion studies, ECLAC Panorama Fiscal, national tax-administration reports, academic papers on the country's income tax. Searched instead: the statute and its amendment notes (provisions listed in the Lean docstrings), the generic scanners (results/search/SUMMARY.md, scale = scale.json), and decide-proofs of every statute-visible threshold.

Generic scanners (quick grid, 0-4 scale): single: peak METR none at 43.2 % scale, bands >100 % 2.645, largest notch 0; single_parent_2: peak METR none at 43.2 % scale, bands >100 % 2.645, largest notch 0; couple_1earner_2: peak METR none at 43.2 % scale, bands >100 % 2.645, largest notch 0.

## Model limitations (also in each output's `unsupported`)
See the `unsupported` list in the exe output and results/summary.json.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| PE-F1 | fact | model-proved | exe and #guard L1PE.F1 (0 tax at 7 UIT). Evidence: exe + Lean `L1PE.F1` (`world/loopholes/rest/lean/L1PE.lean`, 1 #guard): it(a) = 0; model Lean: PeTax.art53_thresholds. |
| PE-F2 | loophole | model-proved | 5 % on dividends, 0 on deposit interest, vs up to 30 % on labour. exe and #guard L1PE.F2. Evidence: exe + Lean `L1PE.F2` (`world/loopholes/rest/lean/L1PE.lean`, 2 #guard): tot(a) = 5000; tot(b) = 0. Known/new: **known**: pattern: flat or final tax on capital income beside a progressive labour tax (Dual Income Taxes: A Nordic Tax System, 10.4337/9781849804998.00012); the rates are published. |
| PE-F3 | fact | explained | Additional deduction depends on payment method (input). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/PE.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (= PE-F2).

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 29.5 % (TUO LIR art. 55: 'aplicando la tasa de veintinueve coma cincuenta por ciento (29,50%)' (src/capvii.txt:202)); at a profit of 3 AW the best split costs 27.4 % of the profit, all salary 28.7 %, all dividends 33.0 % (employer contributions: not included); dividends beat salary once employer contributions exceed 9 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
