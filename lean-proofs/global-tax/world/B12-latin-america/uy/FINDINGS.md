# Uruguay (UY) 2025: findings (B12-latin-america, build phase 2026-11-20 07:15 UTC)

Model only from the statute; no referee values seen. Scanner scale: 1,183,680 UYU (IRPF Titulo 7 arts. 37 A and 38: the 180 BPC threshold at BPC $ 6.576 (Decreto 05/025, DGI table)).

### UY-F1 The deduction credit falls from 14 % to 8 % of all deductions one peso above 180 BPC
- kind: loophole-new
- provisions: TO 1996 T7 art. 38 penultimate paragraph (Ley 20.124 art. 1)
- Lean: UyTax.art38_notch
- note: At $ 1.183.680 of nominal income a single worker loses $ 13.849 of credit for one more peso (scanner: METR 276 %); single parent with two children $ 30.696 (562 %). Not found in 0 sources searched (no literature search); the rule is visible in the statute.
- status: proved in Lean / recorded (build phase)

### UY-F2 FONASA moves from 3 % to 4,5 % (6 % with children) of the whole wage above 2,5 BPC a month
- kind: loophole-known
- provisions: Ley 18.211 art. 61
- Lean: UyTax.fonasa_notch
- note: Jump of 1,5-3 % of 16.440 pesos a month at the threshold (partly returned through the art. 38 credit).
- status: proved in Lean / recorded (build phase)

### UY-F3 Labour is taxed up to 36 %, dividends at 7 %, interest at 0,5-12 %
- kind: loophole-known
- provisions: TO 1996 T7 arts. 26, 37
- Lean: UyTax.out (Cat. I surtaxes)
- note: Dual system: owner-managers gain by paying themselves dividends (company IRAE side not modelled).
- status: proved in Lean / recorded (build phase)

## Step 4: known ways of paying less, catalogued from the statute

- art. 38 rate notch at 180 BPC (recreated, proved)
- FONASA 2,5 BPC notch (recreated, proved)
- labour vs capital rate gap (recreated)
- nucleo familiar election B/C (not modelled)
- rent exemption under 40 BPC with bank-secrecy waiver, art. 27 J (not modelled)

## Step 5: what was searched

Literature not checked (web-search budget 0 this session): IMF Article IV and FAD reports, IDB/CIAT tax expenditure and evasion studies, ECLAC Panorama Fiscal, national tax-administration reports, academic papers on the country's income tax. Searched instead: the statute and its amendment notes (provisions listed in the Lean docstrings), the generic scanners (results/search/SUMMARY.md, scale = scale.json), and decide-proofs of every statute-visible threshold.

Generic scanners (quick grid, 0-4 scale): single: peak METR none at 275.9 % scale, bands >100 % 1.0, largest notch 1; single_parent_2: peak METR none at 562.0 % scale, bands >100 % 1.0, largest notch 2; couple_1earner_2: peak METR none at 428.7 % scale, bands >100 % 1.0, largest notch 2.

## Model limitations (also in each output's `unsupported`)
See the `unsupported` list in the exe output and results/summary.json.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| UY-F1 | loophole | confirmed | 13,850 UYU for one peso at 1,183,680 (single); 30,697 with two children. exe and #guard L1UY.F1; scale table re-read. Evidence: exe + Lean `L1UY.F1` (`world/loopholes/rest/lean/L1UY.lean`, 2 #guard): tot(b)-tot(a) = 13850; tot(d)-tot(c) = 30697; statute re-read: `src/to1996.txt`; model Lean: UyTax.art38_notch. Known/new: **new**: The 14 % / 8 % rule is published (DGI 'IRPF para trabajadores dependientes'; IMPO Decreto 148/007 art. 58); no hit describes the jump in tax at 180 BPC; web search 5 + Crossref. |
| UY-F2 | loophole | model-proved | 2,959 UYU a year for one peso at 197,292 (2.5 BPC a month). exe and #guard L1UY.F2. Evidence: exe + Lean `L1UY.F2` (`world/loopholes/rest/lean/L1UY.lean`, 1 #guard): tot(b)-tot(a) = 2959; model Lean: UyTax.fonasa_notch. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| UY-F3 | loophole | model-proved | 7 % on dividends vs up to 36 % on labour. exe and #guard L1UY.F3. Evidence: exe + Lean `L1UY.F3` (`world/loopholes/rest/lean/L1UY.lean`, 1 #guard): tot(a) = 70000. Known/new: **known**: pattern: flat or final tax on capital income beside a progressive labour tax (Dual Income Taxes: A Nordic Tax System, 10.4337/9781849804998.00012); the rates are published. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/UY.json`): METR 276-429 % and notches 13,849 / 22,805 = UY-F1; notch 2,958 at 197,291 = UY-F2; METR 118-121 % = FONASA and the deduction credit.


### D9R-1 FRL 0,10 % added (D9 review, 2026-11-20); montepío ceiling still open
- Model fix from the statute: Ley 19.689 (D.O. 08/11/2018) art. 17 sets the Fondo de Reconversión Laboral rate "para
  empleadores, trabajadores y Estado en un 0,10% ... calculado sobre las asignaciones computables gravadas por
  contribuciones especiales de seguridad social" from 1 January 2019 (IMPO copy `law/d9/impo_ley19689_art17.html`,
  SHA256SUMS); deductible for the IRPF under Título 7 art. 38 B) ("Los aportes ... al Fondo de Reconversión Laboral").
  Now `frl` = 0,10 % of the wage, in employeeSocial and in the art. 38 deductions; #guards; input `"uyFrl": false`
  restores the old model (`check4.py UY` with it: 0 / 300 differ from the pre-change exe; 279 / 300 change without).
  Rescanned (`logs/d9_review_scan_UY.log`).
- Found on `uy_official_dgi_simulador_irpf_2025_grid` (DGI simulators 2025): employeeSocial model / ref = 0.9949 =
  19.5 / 19.6 below the AFAP ceiling, incomeTax +0,10 % x wage x the art. 38 rate (14 % / 8 %). Dev exact 130 -> 475 / 550.
- Still open (M): the montepío ceiling of Ley 20.130 art. 22 (indexed; 2025 value not reached): above about
  $ 3,35 M a year the DGI simulator caps the jubilatorio contribution and the model does not (34 dev cases; model
  employeeSocial above, incomeTax below). Needs the 2025 indexed ceiling from a BPS / executive instrument, not the
  simulator.
- provisions: Ley 19.689 art. 17; TO 1996 Título 7 art. 38 B); Ley 20.130 art. 22 (open)

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 25.0 % (Texto Ordenado 1996, Título 4 (IRAE) art. 15: 'La tasa del impuesto será del 25%' (src/to1996.txt:8470)); at a profit of 3 AW the best split costs 29.1 % of the profit, all salary 40.6 %, all dividends 30.2 % (employer contributions: statute rate 7.50 %); dividends beat salary once employer contributions exceed 0 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
