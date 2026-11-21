# Mexico: findings (ejercicio fiscal 2025)

Model: `lean/MxTax` (exe `mxtax`). Runs: `runs/scan_wage.py`, `runs/scan_regime.py`, `runs/quantify.py` (outputs
`runs/*.json`). Lean names refer to `lean/MxTax/Theorems.lean` and `Tests.lean` (no `sorry`, no `native_decide`).
Amounts in MXN a year unless stated. "Net" = gross - ISR - IMSS employee quotas.

### F1 OECD books cesantía y vejez as a non-tax payment
- kind: model-fix (convention). Households: all 8 OECD types. Our `employeeSocial` holds every IMSS employee quota
  (LSS arts. 25, 106 fr. II, 107, 147, 168 fr. II b); the OECD EECSSC leaves out the 1.125 % cesantía y vejez quota
  (paid into the worker’s AFORE account), so OECD take-home pay is higher by exactly that quota (S67 1,655; S100
  2,471; S167 4,126). Mapping: `oecd_map.py` (EECSSC = `detail.imssOecdSsc`). Who is right: both; CFF art. 2 fr. II
  makes "aportaciones de seguridad social" contributions, the OECD classifies payments to funded individual accounts
  as non-tax compulsory payments. Lean: `Imss.oecdSsc`. Status: explained.

### F2 OECD uses the annual 2025 UMA for the whole year in the IMSS 3-UMA threshold
- kind: model-fix (OECD simplification). OECD EECSSC = 1.25 % x W + 0.40 % x (W - 3 x 41,273.52) reproduces all 8
  OECD values to the centavo (`mxImss:"oecd"`): a 364.8-day UMA year (41,273.52 = 113.14 x 30.4 x 12) and the 2025 UMA
  in January. IMSS quotas are daily (LSS art. 106 fr. II "tres veces el salario mínimo general diario") and the 2025
  UMA is in force only from 1-02-2025 (Ley para Determinar el Valor de la UMA art. 5; INEGI DOF 10-01-2025): 31 days
  at 3 x 108.57 and 334 at 3 x 113.14 give a threshold of 123,463.29, not 123,820.56. Effect +1 to +3 MXN (S100 3,130
  vs 3,128). Who is right: the statute (calendar). Lean: `imssOf`. Status: explained.

### F3 The OECD exempt-income (BTA) assumption, identified
- kind: model-fix. OECD BTA (5,091.30 at S100/S167, 4,603.55 at S67) = exempt aguinaldo min(15 days, 30 UMA) + exempt
  prima vacacional min(25 % x 12 days, 15 UMA), a day = W/365, both inside the AW (LISR art. 93 fr. XIV; LFT arts. 76,
  80, 87). Reproduced to the centavo (`Tests.oecd_S100_bta`, `oecd_S67_bta`). Reading note: if the AW includes them,
  a day’s salary is W/383, not W/365 (S67 ISR +10 MXN; immaterial). Status: explained; the model’s default.

### F4 The published tarifas are not continuous or monotone (by up to 1.52 centavos)
- kind: statute-fault (trivial in money). Each cuota fija was inflation-updated and rounded on its own (LISR art. 152
  último párrafo), so it is not the tax of the row below at its upper limit. Annual 2025 tarifa (RMF 2025 Anexo 8
  C.II = RMF 2026 Anexo 8 C.I) jumps -0.76, +0.88, +0.57, -0.52, -0.86, +0.99, -0.51, -0.20, -1.52, +1.40 centavos at
  its 10 edges; at 6 edges a centavo more income lowers the tax. Proved for all incomes: the tarifa equals the
  kernel’s progressive band schedule within -3.87/+0.34 centavos (annual, `tarifa152_vs_bands`) and -0.89/+0.09
  (monthly, `tarifa96_vs_bands`); `tarifa152_drop` (1,503,902.46 -> .47: -1.52 centavos); `tarifa152_almost_mono`. With the kernel 1.1 `Table`: the rows
  tile the line and the cuotas rise (`cuotas152_contiguous`), every cuota is within 4 centavos of the band schedule at
  its límite inferior (`cuotas152_vs_bands`), and 7 of the 11 differ from it (`cuotas152_disagree`).
  Status: proved. Fix (if wanted): derive each cuota fija from the row below after updating the limits.

### F5 The statute still counts in "salario mínimo" where the UMA applies; the 2021 reform converted only one
- kind: statute-fault. DOF 12-11-2021 (in force 2022) replaced art. 151 último párrafo "cinco salarios mínimos
  generales elevados al año" by "cinco veces el valor anual de la Unidad de Medida y Actualización" (Global law
  `phrase_history`: added 2022-01-01; the text on 2021-06-30 had the salario mínimo), but left the same article’s
  fr. V cap ("cinco salarios mínimos generales del área geográfica del contribuyente elevados al año"), fr. I and II,
  and art. 93 fr. I, IV, XIII, XIV, XIX b), XX ("del Distrito Federal"), XXIII c), XXIX and penúltimo párrafo, and
  art. 96 ("un salario mínimo general correspondiente al área geográfica") in minimum wages and abolished geographic
  areas. They are read as UMA through the desindexación decree (DOF 27-01-2016, transitorios), as SAT and the OECD do
  (the OECD BTA uses 113.14 = UMA; at the 278.80 minimum wage the exemption would be 12,546 instead of 5,091; at
  fr. V, 5 x 278.80 x 365 = 508,810 instead of 206,367.60). Same in LSS arts. 28 and 106 ("Distrito Federal"), and
  LSS art. 106 fr. II still prints the 2 % worker quota that transitorio décimo noveno cut to 0.40 % by 2007.
  Classification: statute-fault (drafting; the reading is settled). Status: open.
  Draft note (not filed): «Art. 151 fr. V LISR y arts. 93 y 151 fr. I-II: sustituir “salario(s) mínimo(s)
  general(es) del área geográfica ... elevado(s) al año” por “valor anual de la Unidad de Medida y Actualización”,
  como se hizo en el último párrafo del art. 151 (DOF 12-11-2021).»

### F6 The subsidio para el empleo cut-off is a cliff: one centavo costs 474.65 a month
- kind: loophole-new (a notch; the all-or-nothing rule is in the decree, its size and dead zone not found quantified
  in the sources searched: the decrees DOF 01-05-2024 and 31-12-2024, SHCP Renuncias Recaudatorias 2025, 2 web
  searches, about 38 results). SE-2025 art. Segundo: a month’s taxable income <= 10,171.00 gets 474.65 off its ISR;
  10,171.01 gets nothing. Monthly ISR 314.86 -> 789.51 (`subsidy_cliff`, `subsidy_cliff_levels`). Pay after ISR at
  10,171.00 (9,856.14) is reached again only at 10,703.59: every wage from 10,171.01 to 10,703.58 a month (a 5.2 %
  band) leaves less than 10,171.00 (`subsidy_dead_zone_month`). The cap is exactly 1.2 monthly minimum wages
  (1.2 x 278.80 x 30.4 = 10,170.62, `Tests.cap_is_1p2_sm`); SHCP counts about 6.1 million beneficiaries (DRR 2025,
  cuadro VIII): a raise of up to 5 % above 1.2 minimum wages is worth nothing or less. Fix: withdraw the 474.65
  gradually above 10,171 instead of at once. Status: proved.

### F7 Annual view of the cliff: 10 pesos more pay, 5,213 less net
- kind: loophole-new (same rule over the year, with the aguinaldo and prima as the OECD assumes them). A worker paid
  in 12 equal months: 128,380 a year keeps the subsidy in 11 months (5,221.45), 128,390 in none
  (`subsidy_cliff_annual`); net falls by 5,213 (`runs/scan_wage.py`) and is recovered only at 134,420 (dead zone
  6,040 = 4.7 % of pay). The employer’s annual calculation (art. 97 with SE-2024 art. Tercero) does not smooth it:
  the annual credit is the sum of the monthly subsidies. Status: proved.

### F8 The aguinaldo costs December’s subsidy; a more generous aguinaldo can cost the worker
- kind: loophole-new (timing). The taxable part of the aguinaldo is income of December (art. 96: "la totalidad de
  los ingresos obtenidos en un mes"), so from 112,750 a year December’s base exceeds 10,171 and December’s subsidy is
  lost (`december_subsidy_lost`; net -465 for +10 pesos, dead zone 550). With the same annual pay but a 30-day
  aguinaldo this starts at 100,000: the worker loses 475 (`runs/quantify.py` K2). Avoidance: pay part of the
  aguinaldo in November, or the employer’s optional RLISR art. 174 calculation (not modelled; whether its base counts
  for the decree’s "ingresos mensuales que sirvan de base" is a reading question). Status: proved.

### F9 IMSS: the worker’s quotas switch on at one peso above the minimum wage
- kind: loophole-new (notch; LSS art. 36 is well known, its notch for the worker not found quantified in the sources
  searched). LSS art. 36: "Corresponde al patrón pagar íntegramente la cuota señalada para los trabajadores, en los
  casos en que éstos perciban como cuota diaria el salario mínimo". At 101,762 a year (278.80 a day) the worker pays
  0; at 101,763 every quota on the whole wage, 2,416.87 (`imss_minimum_wage_notch`); net -2,408 for +10 pesos, dead
  zone to 104,550. Reading: "el salario mínimo" as a daily wage not above it. Status: proved.

### F10 RESICO’s table taxes the whole revenue at one rate: notches at 300,000, 600,000, 1,000,000, 2,500,000
- kind: loophole-known (the single-rate structure is plain in art. 113-F "Tasa aplicable"; CATALOGUE K3).
  300,000.01 pays 300.00 more than 300,000.00; 600,000.01 +2,400.00; 1,000,000.01 +5,000.00; 2,500,000.01
  +12,500.00 (`resico_notch_300k`, `resico_notches`). Status: proved.

### F11 Leaving RESICO during the year: month-count notches, and a year with no rate
- kind: loophole-new + statute-fault. Art. 113-E tercer párrafo: above 3,500,000 the section stops applying "a partir
  del mes siguiente"; RMF 2025 regla 3.13.5 fr. I keeps the earlier months’ RESICO payments definitive and puts only
  the remaining months under the general regime. With revenue earned evenly, crossing 3.5 M in December costs
  nothing that year; but one peso above 3,818,181.81 moves December’s profit to art. 152 (`resico_month_notch`): net
  -39,992 for +1 peso (margin 100 %); at 4,200,000.01 -80,109; each month lost is another notch. Statute gap: a
  taxpayer who passes 3.5 M only in December stays in RESICO all year, yet the annual table of art. 113-F stops at
  "Hasta 3,500,000.00" and has no rate for that year’s revenue (the model reads 2.50 %, the monthly table’s last
  rate). Not found in the sources searched (RMF 2025 reglas 3.13.4-3.13.5; 1 web search, 20 results). Status: notch
  proved; gap open (reading).

### F12 Which subsidy does the annual calculation credit? (immaterial)
- kind: reading. SE-2024 art. Tercero: the annual tax "se disminuirá con la suma de las cantidades que por concepto
  de subsidio para el empleo mensual le correspondió"; art. Segundo: a monthly subsidy larger than the month’s ISR is
  lost. Entitlement (R1, the model) vs applied (R2) differ by at most 37 MXN a year on a 30,000-130,000 grid (at
  91,450). Status: closed (immaterial).

### F13 The minimum-wage worker: no withholding (art. 96) but an annual tax (arts. 97, 152)
- kind: statute-fault (reading). Art. 96: "No se efectuará retención a las personas que en el mes únicamente
  perciban un salario mínimo general"; yet the annual tax of a worker paid the 2025 minimum wage with the legal
  aguinaldo and prima (101,762) is 1,110 after the subsidy (model), which the employer’s annual calculation (art. 97)
  or the worker would owe. Either the liability is real and art. 96 only defers it, or the minimum wage is meant to
  be untaxed and the annual rules do not say so. Status: open (the model computes the annual liability).

### F14 Fixed nominal thresholds next to indexed tarifas
- kind: statute-fault (amounts not updated when a related amount changed). The tarifas were updated by inflation in
  2023 and again for 2026 (+13.21 %: 8,952.49 -> 10,135.11, RMF 2026 Anexo 8 C.II) under art. 152 último párrafo,
  but the 400,000 threshold of arts. 97 b) and 98 fr. III e) is the 2014 figure, and RESICO’s 3,500,000 (2022) and
  the subsidy’s 10,171 (decree) are nominal too. Effect: fewer employees left to the employer’s annual calculation
  each year; RESICO’s real ceiling shrinks. Status: open (design).

### F15 Shifting income to a spouse pays (individual taxation)
- kind: loophole-known (CATALOGUE K9). A couple with 1,000,000 of wages (adult 1) and 600,000 of interest saves
  77,555 if the interest belongs to the non-earning spouse (LISR art. 140 "el propietario del título valor"; sociedad
  conyugal); rental 600,000 split equally saves 40,764. Lean: kernel `splitting_le_separate` on the band schedule
  (`split_ok`). Status: recreated.

### F16 Timing across the subsidy cliff: bunching two years’ pay gains 7,112
- kind: loophole-new (timing; found blind by the harness timing scanner, `results/search/timing.md`). A worker who
  would earn 128,690 in each of two years keeps 7,112 more (3.24 % of the AW) by taking 155,922 in one year and
  101,459 in the other: the low year keeps all 12 monthly subsidies, the high year had none to lose. Provisions: SE-2025
  art. Segundo (monthly cut-off), SE-2024 art. Tercero (annual credit = sum of monthly subsidies). Lean: the cliff
  itself (`subsidy_cliff_annual`); the two-year gain is a scan result. Status: lead confirmed by the model’s detail
  lines (subsidioEmpleo.entitlement).

### F17 Generic scanners recreate the cliffs blind
- kind: model-fix (validation of the search). `~/cmp20/harness/search/run_all.py MX` (results/search/SUMMARY.md)
  found without being told: the subsidy cliff (largest notch 5,221 at 128,383), the LSS art. 36 notch (2,416 at
  101,762), the December band (METR 121 % at 112,439-112,879), no marriage effect anywhere (individual taxation),
  a split gain of up to 48,113 for a one-earner couple at 4 AW (needs income that can legally be moved, F15), and
  pensions taxed up to 22.6 % less than wages (art. 93 fr. IV, 15 UMA a day; DRR ISRP.E.1, 100,441 mdp). Rerun
  2026-11-19 after the resume: identical results. The harness owner-manager scan is skipped for MX (no `company.json`
  entry); the own-company comparison is in CATALOGUE K6.
