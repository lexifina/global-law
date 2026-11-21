# CO findings (Colombia (impuesto sobre la renta de personas naturales residentes; aportes a pensión y salud), 2025 (año gravable 2025))

Batch B01-oecd5, built 2026-11-20 01:48 UTC. Status: built (model frozen for the software phase; no referee values used). Scanner output: `results/search/SUMMARY.md` (run with a statutory reference wage instead of the OECD AW, `tools/scan_b01.py`).

### F1 ET art. 241's printed fixed amounts are rounded, so the literal tax jumps at three thresholds and falls at two
- kind: statute-fault
- status: proved

The table prints 116, 788, 2.296, 5.901, 10.352 UVT; the band sums are 115,9; 787,9; 2.296,0; 5.901,0; 10.352,1. Read literally, the tax jumps +0,1 UVT (4.980 COP) at 1.700 UVT and falls by 0,1 UVT at 8.670 and 31.000 UVT. Lean `CoTax.art241_jumps` (kernel cumJumps), `art241_falls_at_8670` (the tax at 8.670 UVT is below the tax at 8.669 UVT plus one UVT at 33 %), `art241_close` (within 0,1 UVT elsewhere). Tiny in money (≈ 5.000 COP) but a real non-monotone point in the statute (cf. the 20-country NL finding on rounded columns).

### F2 Global law record issues (Colombia)
- kind: gov-error? no: tool record
- status: reported here (for the Global law maintainers)

(a) read_law's official link for Ley 100 art. 20 is .../basedoc/codigo_comercio.html (wrong act). (b) The record shows Ley 2381 de 2024 art. 94 'entrará en vigor el 1 de julio de 2025' with no note that its entry into force was suspended (Senate note: 'Entrada en vigencia suspendida, salvo los artículos 12, parágrafo transitorio, y 76'; 'Los artículos declarados exequibles entran en vigencia a partir del 1 de abril de 2027. Sentencia C-264-26'); the record warns it does not hold commencement conditions. For 2025 the model applies Ley 100.

### F3 Reading: both dependant reliefs are given for the same child
- kind: reading / possible loophole
- status: reading; to check against the DUR / DIAN doctrine

ET art. 387 inc. 2 (10 % of labour income, max 32 UVT a month) and art. 336 num. 3 inc. 2 ('Sin perjuicio de lo establecido en el inciso 2 del artículo 387 ... 72 UVT por dependiente hasta ... cuatro') are both applied for the same children. Household c (wage 120 M, two children): 12,0 M COP deduction + 7,17 M COP outside the 40 % limit. The regulation (DUR) was not read; if it bars double use, the model over-deducts.

### F4 Contributions are incomplete (parameters not reached)
- kind: model limitation
- status: open

Pension 3,875 % (25 % of the 15,5 % Ley 100 art. 20 states; the 2008 decree that may add one point was not reached) and health 4 %; the solidarity fund (1 % from 4 SMMLV) and the 25-SMMLV ceiling need the 2025 minimum wage, not reached. Access tier B.

### F5 Labour-income reliefs shape the METR
- kind: observation
- status: lead checked

Scanner METR peak 38,3 % (single) against a top statutory 39 % rate: the 25 % exemption (capped at 790 UVT) and the 40 % / 1.340 UVT limit on exempt income and deductions phase out the relief as income rises; no band above the top rate.

## Round D2 (improvement agent, 2026-11-20): D1 dev failures settled from the statute

### D2-1 OECD classes employee contributions as non-tax payments; --oecd added; pension 4 % decree still unread
- kind: convention
- OECD, Taxing Wages 2025, Part II, Colombia chapter (tw2025.pdf pp. 255-260): health and pension contributions "are not
  classified as taxes but as a NTCP since more than 50% goes to private sector"; "the employee's contributions to pensions
  and health are included in the model as non-taxable income"; employee pension "4.0% of the employee's monthly
  earnings". `--oecd`: employeeSocial 0, contributions still excluded from income, employee pension 4 %. Probe S100:
  CGTC 21,764,182 (OECD 21,764,182.17).
- Statute mode unchanged: Ley 100 art. 20 (Global law, as in force 2025-07-01) gives 15,5 % and lets the Government add
  one point from 2008 by decree; Decreto 4982 de 2007 was not reachable (Función Pública and SUIN script-rendered or
  refused; Ley 2381 de 2024's 16 % is suspended), so the model keeps 3,875 % (flagged).
- Not modelled: subsidio familiar (cajas de compensación: regional cuota monetaria; the OECD uses a national average,
  2023 COP 661,822 per beneficiary): CTGG gap.
- Dev: TW 2025 statute 28 / 36, convention 59 / 60; Tax DB rates statute 24 / 24, convention 45 / 45.
- Lean: CoTax.pensionContribAt, oecdPensionTenthBp, out --oecd
- status: convention flag added; decree open

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: Ley 797 de 2003 arts. 5 (Ley 100 art. 18), 7 (art. 20), 8 (art. 27) (Global law repo); Decreto 4982 de 2007 art. 1 (16 %); Decreto 1572 de 2024 art. 1 (SMMLV) (Colpensiones normogram)
- pension rate 16 % (employee 4 %), base capped at 25 SMMLV for pension and health, Fondo de Solidaridad Pensional 1 % from 4 SMMLV plus 0.2-1 % from 16 SMMLV (INCR); SMMLV 2025 = 1.423.500. Before W5 the model booked no such contribution (or only an optional input); the W5a grids and the pattern A sweep flagged it (IMPROVE_W5 pattern A, `w5/pa/SWEEP.md`). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS. Open: contributions: 1-SMMLV minimum base and PILA rounding not applied; Ley 2381 de 2024 FSP rules not applied.
- status: fixed

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | proved | Model theorems rebuilt; ET art. 241 re-read in the DIAN text. Tiny in money (about 5,000 COP). Evidence: exe + Lean `L1CO.F1` (`world/loopholes/rest/lean/L1CO.lean`, 1 #guard): it(a) = 0; statute re-read: `src/dian/et.htm`; model Lean: CoTax.art241_jumps, art241_falls_at_8670, art241_close. |
| F2 | record | explained | Global law record note for the maintainers; not a loophole. |
| F3 | reading | lead | 3,072,501 COP less tax for 120 M of wages with two children (exe). Both ET art. 387 inc. 2 (10 %, 32 UVT) and art. 336 num. 3 inc. 2 (72 UVT per dependant, 'en adición al límite') re-read; the DUR regulation that may bar double use was not read. Stays a lead. Evidence: exe + Lean `L1CO.F3` (`world/loopholes/rest/lean/L1CO.lean`, 1 #guard): it(a)-it(b) = 3072501; statute re-read: `src/art-0387@2025-07-01.txt`. |
| F4 | record | withdrawn | Superseded by W5A-1: pension 4 %, health 4 %, FSP and the 25-SMMLV cap are now modelled (Ley 797 arts. 5, 7, 8). |
| F5 | fact | explained | No band above the top rate in the fresh scan except the FSP notches (L1). |
| D2-1 | record | explained | Record (convention): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5A-1 | record | explained | Record (model gap fixed from the statute): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| L1 | loophole | confirmed | 683,280 COP a year at 68,328,000 (4 SMMLV x 12); 366,238 at 16 SMMLV (273,312,000). Found blind by the fresh METR scan (170 % at 0.805 scale; notches at 4, 16, 17, 18 SMMLV x 12); exe and #guard L1CO.L1. Partly returned through the INCR deduction (the tax line falls by about 512,000 at the 4 SMMLV point at 33 %). Applies per month: a monthly base crossing 4 SMMLV costs 56,940 that month. Evidence: exe + Lean `L1CO.L1` (`world/loopholes/rest/lean/L1CO.lean`, 2 #guard): tot(b)-tot(a) = 683280; tot(d)-tot(c) = 366238; statute re-read: `law/w5/gl_ley797_art-0008.md`. Known/new: **new**: The 1 % from 4 SMMLV is widely published (Portafolio 'Un descuento en el salario: el fondo de solidaridad pensional'; Función Pública norma 194870), but no hit describes the fall in net pay at the threshold or the 16-20 SMMLV steps; web search 3 + Crossref. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/CO.json`): METR 125-177 % and notches 683,279 (4 SMMLV) and 412,017-434,907 (16-19 SMMLV steps) = L1 (new).

### L1 The pension solidarity contribution (FSP) is 1 % of the whole base from 4 SMMLV: one peso of monthly pay costs 683,280 COP a year, and each step from 16 SMMLV another 0.2 % of the whole base
- kind: loophole (found blind by the L1 re-scan)
- amounts: 683,280 COP a year at 68,328,000 (4 SMMLV x 12); 366,238 at 16 SMMLV (273,312,000)
- who: employees and independent workers whose pension base is at or just above 4 SMMLV (5,694,000 a month) or 16-20 SMMLV
- provisions: Ley 100 art. 27 as amended by Ley 797 art. 8 ('cotización adicional del 1% sobre la base de cotización ... cuya base de cotización sea igual o superior a cuatro (4) salarios'); art. 20 (0.2-1 % from 16 SMMLV)
- Lean: `L1CO.L1` in `world/loopholes/rest/lean/L1CO.lean` (#guard on the model's `country.compute`)
- status: confirmed (Found blind by the fresh METR scan (170 % at 0.805 scale; notches at 4, 16, 17, 18 SMMLV x 12); exe and #guard L1CO.L1. Partly returned through the INCR deduction (the tax line falls by about 512,000 at the 4 SMMLV point at 33 %). Applies per month: a monthly base crossing 4 SMMLV costs 56,940 that month.)
- novelty: new: The 1 % from 4 SMMLV is widely published (Portafolio 'Un descuento en el salario: el fondo de solidaridad pensional'; Función Pública norma 194870), but no hit describes the fall in net pay at the threshold or the 16-20 SMMLV steps; web search 3 + Crossref.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 35.0 % (Estatuto Tributario art. 240 (Ley 2277 de 2022 art. 10): 'La tarifa general del impuesto sobre la renta aplicable a las sociedades nacionales ... será del 35%' ); at a profit of 3 AW the best split costs 30.1 % of the profit, all salary 30.1 %, all dividends 37.9 % (employer contributions: statute rate 12.00 %); dividends beat salary once employer contributions exceed 30 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
- ceilings.py: ceiling at 5.0492 AW (contribution rate 10.0 -> 0.0 %, combined marginal 39 -> 33 %) (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
