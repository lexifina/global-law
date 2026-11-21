# Luxembourg (année d'imposition 2025): findings

Model: `lean/` (lib `LuTax`, exe `lutax`, on `TaxKernel`). Amounts in euros. Statute: L.I.R. "texte coordonné en vigueur
au 1er janvier 2025" (ACD, actualised 02/02/2026), with the 2024 and 2026 coordinated texts for versioned checks
(`law/LIR_*.txt`); loi du 30 juin 1976 art. 6 (legilux consolidation of 1.1.2024); CSS 2025; Code du travail 2025; RELIBI
law 2005 and its 2016 amendment; amending laws of 20.12.2024 (Mémorial A 558, 563, 589). Lean names refer to
`lean/LuTax/Theorems.lean` unless stated. Kinds as in CONTRACT20.

### F1 OECD Taxing Wages 2025 reproduced on every tax and contribution line
- kind: model-fix (conventions), validation
- households: the eight TW types at the OECD AW 77 844 (family check.py, `--args="--oecd"`)
- amounts: CGTC, CGITLETC, CGITFP, SLT, EECSSC exact on 40/40 lines; THP and CTGG differ only by F2. Under `--oecd` the
  cote (art. 124 (1)) and the majoration are not rounded down to the euro, as in the OECD lines (CGITLETC 15 367,875 for
  S100 = 14 362,5 x 1,07). Without `--oecd` the statute's rounding moves CGITLETC by up to -1,12 (M100_0: 6 011 vs
  6 012,12): that is the statute (art. 124 (1) "arrondies au multiple inférieur d'un euro"; ACD barème notes), so a
  convention, not an OECD error.
- provisions: L.I.R. 118-121, 124, 126; loi 1976 art. 6; CSS 29, 238-241, 376-377. Lean: `LuTax.taxWithFE_oecdC`
- status: 48/56 exact, 56/56 within 1 % (`results/oecd_check.md`).

### F2 The OECD's allocations familiales for two children aged 6 and 11 are 4,48 euros too high
- kind: gov-error (unexplained, immaterial)
- households: SP67, M100_0, M100_100, M100_67 (CTGG)
- amounts: OECD 7 874,00; statute 7 869,52 = 2 x [4 x (299,86 + 22,67) + 8 x (307,35 + 23,23)]: CSS art. 272 (31,75 euros
  + 2,40 from age 6, at index 100), index 944,43 (Jan-Apr 2025) and 968,04 (from 1 May 2025, CCSS parameter table). The same
  formula reproduces the CAE's published 2026 amounts (315,04 + 23,81 at index 992,24), so the parameters are right; no
  split of the year at a whole month gives 3 937 per child. The allocation de rentrée scolaire (art. 275: 115 euros per
  child over six) is not in the OECD's CTGG (with it 8 099,52); `--oecd` leaves it out too.
- status: open, 0,06 %. Draft note to the OECD: "Taxing Wages 2025, Luxembourg, CTGG for two children aged 6 and 11: CSS
  art. 272 at index 944,43 (Jan-Apr) and 968,04 (May-Dec) gives 7 869,52, not 7 874,00; please state the months and index
  used."

### F3 The ACD's official formulas, calculator and examples agree with the model everywhere tested
- kind: validation
- amounts: (a) "Formules du calcul automatisé de l'impôt" 2025 (income formulas, classes 1, 1a, 2;
  `refs/bareme-2025-format-excel.xlsx`): 24 003 of 24 003 multiples of 50 from 0 to 400 000 identical in cote and in
  cote + majoration (RIAs where the formula gives a cote under 12 and the statute 0, art. 124 (2), not stated on the
  formula sheet, counted as agreement). (b) ACD online calculator (https://saturn.etat.lu/cobar/bareme/CalculPP, 2025,
  "revenu annuel", queried sequentially 1,5 s apart by `harness/calc.py`): 387 of 387 (class x amount) cases identical in
  "Impôt suivant barème" and "Total dû", including 150 000 / 150 050 / 300 000 / 300 050, the 1a cap 51 800 / 51 850 and
  1 000 000. (c) Circulars L.I.R. n° 154ter/1 du 26.2.2025 and n° 154quater/1 du 12.3.2025 (scanned; OCR in `refs/circ/`):
  11 of 11 worked figures (class 1a cotes 746 and 11 548; CIM 3 198, 3 504, 3 318,94; CIS 516 / 591 / 600; CI-CO2
  165,12 / 189,12 / 192). The derived class-1a schedule (`LuTax.c1aBands`) equals the statute's "réduit d'un quart de son
  complément à 79 380 euros" with the 39-42 % caps (Lean `c1a_eq_formula_points`; numerically at all 8 001 points).
- status: confirmed. The CIM example (3 318,94) settles the CIM's rounding, which art. 154ter does not state: up to the
  cent, as for the other credits.

### F4 The annual salary table of the décompte annuel differs from the assessment by -10 to +15 euros
- kind: gov-error, classified convention
- households: wage-only employees whose tax is settled by the décompte annuel (RGD 20.12.2024 art. 1 (1) 1° a))
- amounts: the ACD's "Formules de l'impôt annuel sur les salaires" apply the tarif to the salary echelon (multiple of 50)
  less 1 020 (forfaits 540 + 480), while the assessment rounds the RIA (salary - 1 020) down to 50 (art. 126 (2)). Over
  40 858 salaries 14 000-300 000 (step 7): table - statute in [-9, +15] (class 1), [-10, +15] (1a), [-9, +13] (2); mean
  about 0 (+0,12 / -0,12 / -0,06) (`results/validate.json`, salary_table_vs_statute).
- provisions: L.I.R. 126 (2), 145; RGD 20.12.2024 (Mémorial A 590) art. 1, 3
- status: convention (a 30-euro offset between the table's echelon and the statute's rounding step). Immaterial.

### F5 Loi du 30 juin 1976, art. 6: "300.00 €" for the class-2 threshold of the 9 % majoration
- kind: statute-fault (typographical)
- amounts: art. 6, 1. "porté à 109% pour la tranche du revenu imposable ajusté dépassant respectivement 150.000 € en
  classes 1 et 1a ou 300.00 € en classe 2" (legilux consolidation 1.1.2024, `law/loi_1976-06-30_fonds_emploi_cons20240101.txt`).
  Read literally every class-2 household above 300 euros of RIA would pay 9 %. The ACD applies 300 000 (A-Z "Fonds pour
  l'emploi"; barème notes "Si le revenu est supérieur à 300.000 €"; the calculator), as does the model
  (`Params.feThreshold2`).
- status: reading (obvious typo); whether the slip is in the Mémorial or only in the consolidation was not checked.

### F6 Loi du 30 juin 1976, art. 7 still says the IRC is "porté à 104 pour cent"; the ACD charges 7 %
- kind: statute-fault (consolidation not updated) / reading
- amounts: art. 7, 1. "l'impôt sur le revenu des collectivités est porté à 104 pour cent" (consolidation 1.1.2024); ACD A-Z:
  "L'impôt sur le revenu des collectivités est majoré depuis l'année d'imposition 2013 de 7%"; the OECD's combined CIT rate
  23,87 % = 16 % x 1,07 + 6,75 % also uses 7 %. Either the 7 % rests on a provision the consolidation does not show or art. 7
  was not updated. The owner-manager scans use 7 %.
- status: open (needs the 2012/2013 amending law).

### F7 Dangling, undefined and stale references in the L.I.R.
- kind: statute-fault (minor)
- (a) art. 152ter (1), 154quinquies (1), (2) refer four times to "l'article 154quarter" (2024, 2025 and 2026 coordinated
  texts); no such article exists, 154quater is meant. (b) art. 123bis (3) b): "un dixième de la différence entre 76.600
  euros et le revenu préqualifié": "revenu préqualifié" is defined nowhere in the L.I.R. (context: the RIA). (c) art. 123bis
  (3) a) fixes the bonification at "le même montant que la modération d'impôt pour enfant, telle que visée à l'article
  122, alinéa 1er": alinéa 1 has no amount (922,5 euros is in alinéa 3). (d) versioned: the 67 400 / 76 600 phase-out of
  art. 123bis (3) b) is identical in 2024, 2025 and 2026 while the tarif was indexed (zero band 12 438 in 2024, 13 230 in
  2025) by L. 22.12.2023 and L. 20.12.2024 (an amount not updated when a related amount changed, unless a policy choice).
  (e) the ACD's text "en vigueur au 1er janvier 2025" already contains art. 123bis (1a) inserted by L. 19.12.2025 (Mémorial
  A 2025 n° 614): the label of the consolidation is not its content.
- status: (a)-(c) reading, (d) statute-fault or policy, (e) publication convention.

### F8 The CIS / CIP / CII bands are defined on whole euros only and do not join
- kind: statute-fault (minor)
- amounts: art. 154quater (2) "de 936 euros à 11.265 euros ... de 11.266 euros à 40.000 euros ... de 40.001 euros à 79.999
  euros": 11 265,50 or 40 000,50 is in no band; at 11 265 the first piece gives 599,55 (rounded up), at 11 266 the second
  600 (Lean `cis_kink`); the credit ends with 0,02 at 79 999 and 0 at 80 000 (`cis_end`).
- status: reading (salaries are whole euros in practice).

### F9 A cote under 12 euros is nil (art. 124 (2)): one 50-euro step of RIA costs 13 euros
- kind: loophole-new (immaterial notch)
- households: class 1, RIA 13 350 -> 13 400: cote 0 -> 13 (the tarif's own increment is 4). Lean: `nil_cote_notch`.
- status: confirmed; the notch is at most 12 euros.

### F10 Class 1a above the cap is class 1 minus 2 321,46 euros: the advantage never fades
- kind: statute property (proved)
- amounts: tarif.ticks x - tarif1a.ticks x = 2 321,46 euros (2 484 with the majoration) from 54 090 up (Lean
  `c1a_advantage_const`, band edges to 1 000 000; ACD formula constants 12 235,5 / 14 556,96). Single parents, widows and
  everyone aged 64 at 1 January keep it at any income; the age switch is worth 2 484 (pension 60 000) / 2 502 (wage
  60 000) a year (`results/scan_lu.json`, age64).

### F11 Marriage penalty for parents: unmarried partners pay less (known)
- kind: loophole-known (CATALOGUE K3, K4)
- households: two earners with two children: married (class 2 + abattement 129b 4 500) vs unmarried cohabiting (partner 1
  class 1a, partner 2 class 1; no CIM, both parents share the home, art. 154ter (1)).
- amounts: married pays up to 1 155 more (85 000 split 55/45); equal splits -97 (40 000) to 1 097 (100 000), about 600
  above 130 000; penalty at 57 % of parent grid points (`results/scan_lu.json` unit; kernel unit scanner -1 162 at
  1,05 AW). PACS partners may simply not request collective taxation (art. 3bis (1) "sur demande conjointe"), so for
  parents a PACS weakly dominates marriage.
- provisions: L.I.R. 3, 3bis, 119 2. b), 120bis, 121, 129b, 154ter (1). Lean: `married_vs_unmarried_parents`,
  `married_penalty_const`. Known: lesfrontaliers.lu (classes d'impôt).

### F12 Spouse mini-job: 936 euros of wage bring 492 euros of refundable credits (NOVEL N3)
- kind: loophole-new (lead)
- households: married, earner 80 000 + spouse wage 935 -> 936: household net +493 for one euro (CIS 300 + CI-CO2 192,
  art. 154quater (2), refundable); spouse wage 5 000: household net +5 057 (101 % of the pay: the abattement 129b absorbs
  the spouse's net income, the second forfaits 540 + 480 apply, CIS + CI-CO2 609,86).
- Lean: `minijob_credits`. status: confirmed in the model; condition: personal compulsory affiliation (art. 154quater (1)).

### F13 CISSM: non-periodic pay up to 3 000 euros is outside the monthly wage (NOVEL N2)
- kind: loophole-new (lead)
- households: full-time employee, 39 000 a year: 3 250 a month gives CISSM 47,25 a month; 3 000 a month + a 3 000 bonus
  gives 81: +405 a year, the maximum (3 000 x 81/600).
- provisions: art. 139quater (2) "Les revenus non périodiques ne sont cependant pas à inclure tant que leur somme ... ne
  dépasse pas le montant de 3 000 euros, à moins qu'ils ne constituent la contrepartie d'une réduction de la rémunération
  ordinaire". Lean: `cissm_bonus_shift`, `cissm_bonus_shift_top`. status: lead (the anti-abuse clause applies to a
  converted wage, not obviously to a contract written that way).

### F14 The CISSM taper stacks: 64-70 % marginal rate between 36 000 and 43 400 (NOVEL N1)
- kind: loophole-new (METR band)
- households: single with 40 000 of dividends: METR 63,7 % average, 70 % peak, wages 38 800-43 400; second earner 65,8 %
  at 36 120-43 126; single parent with dividends 74,4 % peak (kernel METR scanner; scan_lu.py). The CISSM is withdrawn at
  13,5 % of the monthly wage from 3 000 to 3 600 (36 000-43 200 a year) on top of 12,45 % contributions, the tarif and,
  from 40 000, the CIS and CI-CO2 tapers (1,98 %). No band above 100 %. Lean: `cissm_band`. status: confirmed.

### F15 Bunching across the social ceiling and the end of the CIM taper (NOVEL N4)
- kind: loophole-new (timing)
- households: single 162 000 in each of two years vs 266 000 + 58 000: +4 474; single parent: +7 276 (the low year keeps
  the full CIM 3 504 instead of 750, art. 154ter (2); contributions stop at 160 905,28 a year, CSS 241 (3)); kernel timing
  scanner 5 624 for a single parent. status: confirmed.

### F16 Owner-manager: a salary of about 2 000, the rest as dividends (known)
- kind: loophole-known (CATALOGUE K5)
- amounts: profit 77 844: 11 139 more net than all salary; 155 688: 28 053; 1 000 000: 132 647. A small salary beats zero
  because the first wages bring the CIS and CI-CO2 untaxed (scan_lu.py owner; kernel owner.py 0-2 % salary).
- provisions: L.I.R. 115 n° 15a, 174; loi 1976 art. 6/7 (F6). status: confirmed.

### F17 Generic kernel theorems hold for Luxembourg
- kind: validation (proofs)
- tarif and class-1a schedule progressive, monotone, convex; splitting <= separate; separate <= joint; majoration
  monotone (`fe_mono`) and continuous at 150 000 (`fe_continuous`, `fe_thresholds`: the ACD's constants 931,8 / 885,36 /
  1 863,6 are 2 % of the cotes at the thresholds); CIM continuous at 60 000 / 105 000. No generic theorem fails. Kernel
  note: the 109 % "pour la tranche du revenu ... dépassant" is a surcharge on the tax that accrues above an income
  threshold, written as `Surcharge.above` on the cote at the threshold.

### W5S-1 StandaloneSalaryCalculatorApp: no CIM; credits on the main salary only (W5 review pass 2, 2026-11-20)
- kind: software-error
- `lu_open_standalone_salary_calculator_grid`: params/2025-05.json has CIS, CI-CO2 and CISSM but no crédit d'impôt monoparental (LIR art. 152bis), so a class 1a parent misses 3,504 at low income; for a class 2 couple the credits are computed on the main salary only. The May 2025 index parameters used for the whole year are a declared deviation.
- status: recorded (world/IMPROVE_W5.md pass 2)
