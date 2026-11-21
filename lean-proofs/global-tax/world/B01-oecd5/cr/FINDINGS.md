# CR findings (Costa Rica (impuesto al salario, impuesto sobre las utilidades de personas físicas, rentas de capital; CCSS), 2025 (calendar year; período fiscal enero-diciembre))

Batch B01-oecd5, built 2026-11-20 01:48 UTC. Status: built (model frozen for the software phase; no referee values used). Scanner output: `results/search/SUMMARY.md` (run with a statutory reference wage instead of the OECD AW, `tools/scan_b01.py`).

### F1 Ley 7092 art. 35's last paragraph names as the only non-subject incomes two subsections that were repealed
- kind: statute-fault (known: noted by the PGR)
- status: recorded (known)

Art. 35: 'Los únicos ingresos no sujetos ... son los mencionados en los incisos a y d)', while a) and d) were 'Derogado por el artículo 20 de la ley No. 7293'. SINALEVI's own note: 'Existe evidente error en esta ley N° 7293 ... primero suprime los incisos a) y d) ... y de inmediato reforma su párrafo último, citando como vigentes los referidos incisos'.

### F2 Salaried and self-employed people with the same income pay very different tax
- kind: observation (horizontal equity; known)
- status: proved (arithmetic) / scanner lead

The salary scale exempts 922.000 a month (11.064.000 a year) while the profits scale of personas físicas exempts 4.094.000 a year (Decreto 44772-H art. 1, 4). Lean `exempt_gap`: 6.970.000 CRC a year of income is taxed for the self-employed and not for employees. Scanner income-type: self-employment costs up to 9,85 % of income more than wages at 0,25 of the scale.

### F3 The spouse credit is a marriage bonus
- kind: observation (statute)
- status: statutory

Art. 34 ii: a credit 'Por el cónyuge' of 2.600 a month (31.200 a year), claimable by one spouse even when both work; cohabiting partners do not get it. Scanner filing-unit: bonus at 75 % of couple points, max 31.200 CRC.

### F4 Convention: the annual wage includes the aguinaldo
- kind: convention (stated)
- status: stated in conventions.json

Ley 2412 makes the aguinaldo (one month's average salary, paid in December) compulsory and art. 35 b) exempts it from the salary tax; the model reads `wages` as 13 monthly salaries (option --no-aguinaldo: 12). The aguinaldo is outside the CCSS base ('un aguinaldo y no ... un salario', Ley 2412 considerando 7°).

### F5 Source access lesson
- kind: lesson
- status: noted

Costa Rica's laws are reachable on SINALEVI through POST /ResultadosNormativa/_CargarTextoCompleto (idFichaNorma, version); tables are often embedded images (the IVM contribution schedule is an image of Transitorio XI). The text of Ley 7092 carries the 2026 amounts; the year's amounts must come from that year's decree.

## Round D2 (improvement agent, 2026-11-20): D1 dev failures settled from the statute

### D2-1 Residuals are rounding (no change)
- kind: test-note
- All 72 TW 2025 dev cases within 1 %; the 10 not exact differ by 2-16 colones on CGTC (rounding of the OECD's annual
  figures against the model's; cause not traced further) and 5 on one tax. Tax DB SSC EECSSC/gross 9.85 vs 10.67 % is the OECD's
  average rate line; not a statute question. No change.
- status: closed

### W5S4-1 crimson-web payroll (JCAnalyticsCR): 2026 IVM rate and 2024 credits in its '2025' defaults; spouse credit only for a non-earning spouse (W5 review pass 4, 2026-11-20)
- kind: software-error
- `cr_open_crimson_web_jcanalytics_grid`: CCSS worker 10.83 % (IVM 4.33 %) where the Reglamento IVM Transitorio XI table gives 4.17 % for 2023-2025 (ratio 0.9852 on every case); credits 1,710 / 2,590 a month where Decreto 44772-H art. 5 gives 1,720 / 2,600 (-118 / -120); the spouse credit only when the spouse has no income, where Ley 7092 art. 34 lets one of two earning spouses claim it (-31,200 = 12 x 2,600).
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | explained | Recorded as known (PGR/SINALEVI note); not re-read. |
| F2 | loophole | confirmed | 987,650 CRC a year: the same 11,064,000 is untaxed as salary and taxed as self-employment profit. exe (--no-aguinaldo) and #guard L1CR.F2; model theorem exempt_gap. Evidence: exe + Lean `L1CR.F2` (`world/loopholes/rest/lean/L1CR.lean`, 2 #guard): it(a) = 0; it(b) = 987650; statute re-read: `src/sinalevi/dec44772.txt`; model Lean: CrTax.exempt_gap. Known/new: **known**: El Financiero and La Nación (2025-2026) report the gap between the salaried and the self-employed exempt amounts and a deputy calling it 'muy desproporcionada'; for 2026 the self-employed amount rose to 6,244,000 (Observador.cr); web search 8. |
| F3 | loophole | confirmed | 31,200 CRC a year (2025; Ley 7092 now prints 31,080 for 2026). exe and #guard L1CR.F3 (married minus cohabiting, both earning). Evidence: exe + Lean `L1CR.F3` (`world/loopholes/rest/lean/L1CR.lean`, 1 #guard): tot(b)-tot(a) = 31200; statute re-read: `src/sinalevi/ley7092_v83.txt`. Known/new: **known**: The spouse credit and its amount are in Hacienda's yearly decree and PwC Costa Rica's 'Actualización de los tramos ... y sus créditos fiscales' (found by web search 8); that it needs marriage is the rule's own wording: a design, recorded as known. |
| F4 | record | explained | Record (convention (stated)): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| F5 | record | explained | Record (lesson): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| D2-1 | record | explained | Record (test-note): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/CR.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **Owner-manager (company_world.py)**: corporate rate 30.0 % (Ley 7092 art. 15 a): 'Personas jurídicas: Treinta por ciento (30%)' (src/sinalevi/ley7092_v83.txt:1327); the art. 15 b) reduced rates for small companies by gro); at a profit of 3 AW the best split costs 27.5 % of the profit, all salary 27.5 %, all dividends 40.5 % (employer contributions: statute rate 9.25 %); dividends beat salary once employer contributions exceed 37 %. Known pattern (CROSS38 section 4). `results/search/owner.md`.
<!-- R2-SCANNERS:END -->
