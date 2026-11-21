# CL findings (Chile (impuesto único de segunda categoría + global complementario; AFP, salud, seguro de cesantía), 2025 (año comercial 2025, año tributario 2026))

Batch B01-oecd5, built 2026-11-20 01:48 UTC. Status: built (model frozen for the software phase; no referee values used). Scanner output: `results/search/SUMMARY.md` (run with a statutory reference wage instead of the OECD AW, `tools/scan_b01.py`).

### F1 The seguro de cesantía ceiling changed on 1 February 2025 (provisional index replaced)
- kind: gov-practice (statute implementation)
- status: proved (parameter derivation)

Res. ex. 47/2025 set 131,8 UF from 1 January on INE's provisional 4,1 %; Res. ex. 253/2025 set 131,9 UF from 1 February on the definitive 4,2 % and voided Res. 47 from that date. The AFP/health tope stays 87,8 UF (84,3 × 1,042 = 87,84). Lean `ClTax.tope_check`, `tope_check_feb` reproduce all four from the 2024 values. A model that takes the January resolution for the year is 0,1 UF a month off for incomes above the ceiling (Feb-Dec). Same pattern in 2024 (Res. 224/225 'desde el 1 de febrero de 2024').

### F2 The art. 57 interest exemption is all-or-nothing: one peso more costs the whole exemption
- kind: statute-fault (notch; likely known)
- status: found by the model; not yet checked against the literature (not found in 0 sources searched: web search budget 0)

LIR art. 57: interest (art. 20 N° 2) is exempt from global complementario 'cuando el monto total de ellas no exceda' 20 UTM of December (1.390.840 CLP) for taxpayers whose other income is only wages. Model (cltax): wage 24.000.000 + interest 1.390.840 → global complementario 0; + 1 peso → 55.822 CLP (at 60.000.000 of wages: 189.342). No glide zone. Households: n0/n1, m0/m1 in FINDINGS evidence.

### F3 Contribution ceiling makes bunching across years pay
- kind: observation (structure)
- status: lead checked

Timing scanner: bunching two years' wages gains up to 2,36 M CLP (9,4 % of the 30-UTA scale) around the 87,8 UF ceiling (contributions stop, METR falls by 17,6 points). Known feature of capped contributions.

### F4 Readings: rounding and the art. 47 reliquidation
- kind: reading
- status: reading

The LIR text read gives no rounding for the tax in pesos or the scale thresholds in UTM tenths: half-up to the peso used (R1). Art. 54 N° 3 / art. 75 adjust income and withheld tax by the same IPC factors (end of the month before receipt to end of November; SII rounds the percentage to one decimal and ignores negative ones), so with even monthly pay the optional art. 47 reliquidation (`--reliquidar`) returned no refund in the households tried. The edges scanner shows 1-2 peso falls at unit scale (1.257 unit steps): artefacts of rounding each month's tax and contributions half-up, not of the statute.

### F5 Model gaps
- kind: model limitation
- status: open

Dividends (first-category credit depends on the company's register), listed-share gains (art. 107), independent workers' contributions, the AFP commission (set by each AFP, not by statute) and family allowances are unsupported. Scanner income-type 'gains' for dividends and gains are artefacts of these gaps.

## Round D2 (improvement agent, 2026-11-20): D1 dev failures settled from the statute

### D2-1 The OECD gap is classification and convention, not the statute; --oecd added with the OECD's own methodology
- kind: convention
- Source of the conventions (rule 8): OECD, Taxing Wages 2025, Part II, Chile chapter (improve-anglo/refs/tw2025/tw2025.pdf,
  pp. 241-251): "Employee social security contributions in respect of pensions and unemployment are not classified as
  taxes in this report; though they are included in modelling as deductions for income tax"; AFP commission note 5
  "Average cost in 2024 was 1.15% of gross income" (NTC_pens 11.15 %); "In order to estimate taxes, tax rates are
  applied on an annual basis, on the annual average income"; UTM note 1 "Value up to 18 June". `--oecd` (conventions.json)
  = employeeSocial health 7 % only; AFP commission 1.15 % deducted; art. 43 scale applied to the year's base at 12 x the
  June UTM (68.785). Probe S100: CGTC 11,539,004 (OECD 11,539,004.75), tax 15,833 (15,833.39), EECSSC 994,128.
- Statute mode unchanged except: the AFP commission (DL 3.500 art. 17 inc. 2, an AFP's own rate) is now deductible
  through the input `clAfpCommission` (basis points), default 0.
- Not modelled (both modes): asignación familiar, aporte familiar permanente, bolsillo familiar electrónico (the OECD's
  CTGG) and the education credit of LIR art. 55 ter (the OECD's child credit 4.4 UF per child): statutory, but their 2025
  amounts were not read this round; next for B01.
- Dev (local rerun): TW 2025 statute 16 / 16 (unchanged), convention 36 / 55; Tax DB rates statute 12 / 12, convention
  42 / 42; Tax DB PIT convention 3 / 4; SSC convention 1 / 1 (of covered 72, 47, 4, 3).
- Lean: ClTax.wageContrib, wageHealthYear, oecdCommission, julyUTA (June UTM), out --oecd
- status: convention flag added; benefits open

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | fact | proved | ClTax.tope_check, tope_check_feb (model theorems, rebuilt); the Diario Oficial resolution 2596352 re-read (87,8 UF). |
| F2 | loophole | confirmed | 55,822 CLP of global complementario for one peso of interest at 24 M of wages; 189,342 at 60 M. exe and #guard L1CL.F2 reproduce both amounts on the current model. Evidence: exe + Lean `L1CL.F2` (`world/loopholes/rest/lean/L1CL.lean`, 2 #guard): it(b)-it(a) = 55822; it(d)-it(c) = 189342; statute re-read: `src/art-057@2025-07-01.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F3 | fact | explained | Timing lead (2,361,116 CLP, 9.4 % of the scale) re-found by the fresh scan: contributions stop at the 87,8 UF tope (Res. ex. 2596352 re-read), so the schedule is concave there. A contribution-ceiling effect, not a loophole of the tax. Evidence: exe + Lean `L1CL.F3` (`world/loopholes/rest/lean/L1CL.lean`, 1 #guard): soc(a) = 7362741; statute re-read: `src/diariooficial/2596352.txt`. |
| F4 | reading | explained | Reading of rounding and the art. 47 reliquidation; the 1-2 peso unit falls are monthly rounding (edges scan). |
| F5 | record | explained | Record (model limitation): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| D2-1 | record | explained | Record (convention): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/CL.json`): timing 2,361,116 (9.4 % of the scale) = F3 (contribution ceiling); income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings (F5 model gaps).
