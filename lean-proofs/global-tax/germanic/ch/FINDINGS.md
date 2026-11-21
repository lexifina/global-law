# CH Switzerland 2025: findings

Model: `lean/ChTax` (DBG + StG ZH + City of Zürich; default options unless stated). Amounts in CHF. Households are
employees aged 40 with the statutory contributions unless stated. Lean names are in `lean/ChTax/Theorems.lean`.
Statute texts in `law/` (DBG Fedlex consolidation 1 Jan 2025; StG ZH zhlex Nachtrag 127, 1 Jan 2025).

### F1 The printed federal Grundtarif is 4-7 Rappen below its own band sum (the OECD computes the band sum)
- kind: statute-fault (minor, rounding); OECD: convention
- Provisions: DBG Art. 36 Abs. 1 (2025 text, V EFD 22 Aug 2024, AS 2024 479), Art. 39 (kalte Progression).
- The tariff prints a cumulative amount per row ("für 43 500 Franken Einkommen 229.20"). The band sum of its own
  per-100 increments is 229.24 at 43 500, 612.04 at 58 000 (printed 612.00), 1 149.61 at 76 100 (1 149.55),
  1 500.07 at 82 000 (1 500.00); the gap stays at 7 Rappen to the top (91 241.07 vs 91 241.00 at 793 400).
  Each row is the previous printed row plus its increments rounded down to 5 Rappen (229.24 to 229.20,
  1 149.57 to 1 149.55, 1 500.01 to 1 500.00); the same in 2023 (133.95, 221.95 ...) and 2024 (137.05, 225.90 ...).
  The married tariff (Abs. 2) is exact at every row. The printed table never falls (every row-boundary step is
  positive), so unlike NL/PT the rounding does not break monotonicity.
- Referees: the ESTV calculator uses the printed amounts (API_exportManyTaxScales 2025: Taxes 229.2, 612, 1149.55,
  1500; refs/estv_taxscales_2025.json); the OECD uses the band sum (S100 CGITFP 1 618.87 = band sum at 83 800;
  statute 1 618.80).
- Lean: `fedSingle_rows_off` (row gaps [0,0,4,4,6,7,7,7,7,7] Rp), `fed_printed_43500`, `fed_printed_76100`,
  `fed_printed_83800`, `fedMarried_rows_exact`, `fedSingle_rows_step_pos`. `--bandsum` reproduces the OECD.
- Status: confirmed; at most 7 Rappen.

### F2 The federal tariff is not progressive: the kernel's convexity theorem fails (kernel finding)
- kind: model-fix (kernel theorem not applicable; structural, not an error)
- Provisions: DBG Art. 36 Abs. 1-2; BV Art. 128 Abs. 1 lit. a (at most 11.5 % of income).
- Marginal rate 13.2 % (single, 184 900-793 300) / 13 % (married, 152 300-940 800), then 11.8 % / 12.5 % for one
  100-franc step and 11.5 % above, where the tax is exactly 11.5 % of income. `Schedule.progressive` is false;
  `Schedule.ticks_convex` (hence `splitting_le_separate`) does not hold; `ticks_mono` does.
- Lean: `fedSingle_not_progressive`, `fedMarried_not_progressive`, `fedSingle_not_convex`, `fedMarried_not_convex`,
  `fed_top_flat`, `fedSingle_mono`. METR scanner: rates above the 10-AW "top rate" (40.7 %) from about 2 AW (47.3 %
  max, single): the 13.2 % band exceeds the 11.5 % top. INBOX line sent.

### F3 OECD family benefit for Zürich: 268 per child and month where Zürich law pays 215 under age 12
- kind: gov-error (OECD model), classified as convention
- Provisions: FamZG Art. 3, 5; EG FamZG ZH § 4 Abs. 1 ("Fr. 215 bis zum Ende des Monates, in welchem das Kind das
  zwölfte Altersjahr vollendet, danach monatlich Fr. 268").
- OECD TW 2025 CTGG = 6 432 = 2 × 268 × 12 (2022-2024: 6 000 = 2 × 250 × 12). For the OECD's children aged 6 and 11
  in Zürich the law gives 2 × 215 × 12 = 5 160: benefits +1 272 and federal and cantonal taxable incomes +1 272
  (allowances are taxable, DBG Art. 17). The OECD chapter (TW 2025, p. 616) calls it "the average family benefit
  ... estimated", a national estimate, while taxes are for Zürich: an inconsistency of convention.
- Effect (M100_0): take-home pay 95 547 (OECD) vs 94 021 (statute default; also F5). `--oecd` reproduces it.

### F4 OECD Taxing Wages 2025 (year 2024) prints a federal tariff that mixes 2023 and 2024 values
- kind: gov-error (documentation)
- Source: Taxing Wages 2025, Switzerland chapter, "Rates for persons living alone" and the married table
  (refs/oecd_tw2025.txt l. 32470-32512, copy of the OECD PDF b3a95829-en). The "Taxable income" column has the
  2023 limits (14 800, 32 200, 42 200, 56 200, 73 900, 79 600, 105 500, 137 200, 179 400, 769 700: DBG 2023,
  law/dbg_2023-01-01.txt); the "excess over" column the 2024 limits (15 000, 32 800, 42 900, 57 200, 75 200, 81 000,
  107 400, 139 600, 182 600: law/dbg_2024-05-16.txt); the base amounts are 2024 band sums 1-8 Rappen above the 2024
  statute (137.06 vs 137.05, 225.94 vs 225.90, 603.46 vs 603.40, 1 138.06 vs 1 138.00, 1 482.58 vs 1 482.50).
  Married table: same mix (28 300 / 29 300 ...). Read literally, "14 800 to 32 200 ... 0.77 of the excess over
  15 000" is no year's tariff. The published 2024 results are right; only the documentation is wrong.
- Draft issue (not filed): "Taxing Wages 2025, Switzerland, federal schedules: the first column lists the 2023
  bracket limits while the base amounts and the 'excess over' column use 2024 values (DBG Art. 36 as amended by
  the EFD ordinance of 1 Sept 2023, AS 2023 493). Please print the 2024 limits (15 000, 32 800, 42 900, ...) and,
  if the statute's printed amounts are meant, 137.05 / 225.90 / 603.40 / 1 138.00 / 1 482.50."

### F5 OECD conventions for the occupational pension and the Berufskosten base
- kind: gov-error (OECD model), classified as convention / reading
- The OECD deducts an employee BVG contribution of 7.83 % of the wage above 26 460, uncapped (2024: 7.78 % above
  25 725), "an estimated representative rate" (TW 2025 p. 616); reproduced to 1e-10 for S67/S100/S167. The statutory
  minimum (BVG Art. 8, 16, 66) is half of 7-18 % of the coordinated wage capped at 90 720: age 40, 100 715: 3 213
  vs 5 814.
- The OECD takes the 3 % Berufskosten on the wage net of AHV/ALV only (S100: 3 % × 94 269 = 2 828.07); the
  Berufskostenverordnung (Anhang "3 % des Nettolohns") and the ESTV calculator use the Lohnausweis net wage after
  BVG (2 653.60 with the OECD's own BVG): 174 francs more deduction than the ordinance gives.
- `--oecd` applies both (55/56 exact); the statutory default differs (results/oecd_check_statutory.md).

### F6 The ESTV calculator leaves taxable family allowances out of the tax base
- kind: gov-error (official calculator), classified as convention
- Provisions: DBG Art. 17 Abs. 1 ("Zulagen"); StG ZH § 17; FamZG.
- With children, the ESTV calculator's taxable incomes contain no family allowances (married, two children,
  100 000: federal "Massgebendes Einkommen" 65 473) and it has no input for them; put into the gross wage, they
  would bear AHV/ALV/NBU/BVG (they are AHV-exempt). OECD one-earner family at the AW: federal + Zürich tax
  understated by 970 (187 + 5 221 with the allowances vs 0 + 4 438 without; NBU 0.4 % as the ESTV).
- Draft issue (not filed): "swisstaxcalculator: Kinder-/Ausbildungszulagen (FamZG) are taxable income (DBG Art. 17)
  but are neither added for the children entered nor available as an input separate from the AHV-liable gross
  wage."

### F7 The insurance-deduction increase "ohne Beiträge nach lit. d und e" read literally excludes every employee
- kind: statute-fault (wording broader than the practice)
- DBG Art. 33 Abs. 1bis lit. a; StG ZH § 31 Abs. 1 lit. g ("Für Steuerpflichtige ohne Beiträge gemäss lit. d und e
  erhöhen sich diese Abzüge um die Hälfte"). Lit. d covers AHV/IV as well as the pension fund, so literally no
  employee or self-employed person qualifies. The ESTV calculator grants it to employees paying AHV but no BVG/3a
  (wage 20 000: 2 700 federal, 4 350 Zürich). Model = practice; `--ins-literal` = the literal text.

### F8 One franc into Säule 3a costs a person without a pension fund 236 francs of tax (couple: 498)
- kind: loophole-new (trap; notch)
- Provisions: BVV 3 Art. 7 Abs. 1 lit. b; DBG Art. 33 Abs. 1 lit. e and Abs. 1bis lit. a; StG ZH § 31 Abs. 1 lit. e, g.
- Single employee without a fund, 60 000: federal + canton + City + Personalsteuer 4 860.35 with no 3a payment,
  5 096.77 after paying 1 franc, 4 847.15 after 1 450. Married one-earner, 90 000, no fund: 6 978.82 to 7 476.33
  for 1 franc. Any 3a payment removes the half-again increase (900 federal + 1 450 Zürich single; 1 850 + 2 900
  married); payments below about 1 400 (single) / 2 800 (couple) raise the tax.
- Who: self-employed without a fund, employees below the BVG threshold or without a fund, part-timers.
- Lean: `p3a_one_franc_costs`, `p3a_one_franc_costs_married`. Novelty: NOVEL.md N1.

### F9 The BVG entry threshold is a tax notch: one franc above 22 680 raises taxes by 84.63
- kind: loophole-new (notch)
- Provisions: BVG Art. 7 Abs. 1, Art. 8; BVV 2 Art. 5 (minimum coordinated wage 3 780); DBG Art. 33 Abs. 1bis lit. a;
  StG ZH § 31 Abs. 1 lit. g.
- Wage 22 680 to 22 681 (single, 40): the BVG minimum of 189 starts and the insurance deduction falls 2 700 to 1 800
  (federal) and 4 350 to 2 900 (Zürich): taxes 431.96 to 516.59. With 1 AW of dividends (METR scanner): 343
  (single), 553 (one-earner couple); METR 206-303 % over the 100-franc band. Lean: `bvg_threshold_notch`.

### F10 A family living on capital income unlocks the full family allowances with a 7 560 wage
- kind: loophole-new (notch, benefit)
- Provisions: FamZG Art. 13 Abs. 3 (employees: AHV-liable income at least half the minimum full AHV pension = 7 560;
  no income test); Art. 19 Abs. 1bis-2 (below it: non-employed; allowances only if taxable income at most 1.5 × the
  maximum full pension = 45 360).
- Married, children 6 and 11, 100 000 of dividends: wage 7 559, no allowances; 7 560, 5 160 a year (net +4 167
  after tax for one franc). A wealthy family qualifies through a minimal job, e.g. a 7 560 salary from its own
  company. Timing scanner: 4 194 two-year bunching gain at this edge.
- Lean: `famzg_notch` (`famzgEntitled` in Basic.lean). Assumes no EL. Novelty: NOVEL.md N3.

### F11 The two-earner deduction's minimum read literally exceeds the income it is taken from
- kind: statute-fault (wording)
- DBG Art. 33 Abs. 2: "vom niedrigeren Erwerbseinkommen 50 Prozent, jedoch mindestens 8600 Franken ... abgezogen":
  literally 8 600 even on 1 franc. The ESTV calculator caps it at the income (second earner 5 000: 2 660 = 4 660
  net wage - 2 000 Berufskosten, federal and Zürich). Model caps (`fedTwoEarnerRp`, `zhTwoEarnerRp`).

### F12 Marriage penalty (federal): up to +71 % (no children) and +135 % (two children)
- kind: loophole-known
- Provisions: DBG Art. 9 Abs. 1, Art. 36 Abs. 1-2, Art. 33 Abs. 2, Art. 35 Abs. 1 lit. c.
- 2 × 100 000: 5 998.00 married vs 2 × 1 750.80 unmarried (+2 496.40, +71 %). Two children, 2 × 75 000: 1 340
  married vs 569.76 unmarried (+135 %). Grid (results/marriage.md): federal penalty above 10 % at 318 of 485
  two-earner points without children and 350 of 485 with two; max +9 897 (2 × 210 000) / +10 909. One-earner couples
  get a bonus. Zürich layer: smaller penalty (+8 331 max), bonus up to -12 250 for one-earner couples.
- Authority: BGE 110 Ia 7 (1984); BGer 1C_315/2018 (10 April 2019) annulled the 2016 vote on the initiative "Für Ehe
  und Familie - gegen die Heiratsstrafe" because the Federal Council had published 80 000 instead of 454 000
  affected couples (a known government error).
- Lean: `marriage_penalty_2x100k`, `marriage_penalty_kids`. Scanner: unit.md (penalty at 52.7 % of points).

### F13 Owner-manager: dividends beat salary by 6-9 % of profit (AHV avoided, Teilbesteuerung)
- kind: loophole-known
- Provisions: DBG Art. 20 Abs. 1bis (70 %), StG ZH § 20 Abs. 1bis (50 %), DBG Art. 68 (8.5 %), StG ZH § 71 (7 %);
  no AHV on dividends (AHV practice requalifies excessive dividends as wage).
- City of Zürich, single: profit 200 000: all salary net 137 185, all dividend 148 621 (+11 436); 1 200 000:
  +103 860 (results/owner.md). The kernel's owner-manager scan found the opposite (salary best) because the
  contract's `dividends` are portfolio dividends taxed in full; with `"qualifying": true` the order flips (INBOX).

### F14 Pension-fund buy-in, then capital withdrawal at the reduced rate
- kind: loophole-known
- Provisions: DBG Art. 33 Abs. 1 lit. d, Art. 38 (1/5 of the tariff); StG ZH § 37 (rate of 1/20, min 2 %); BVG
  Art. 79b Abs. 3 (3-year lock; BGer 2C_658/2009).
- Single, 58, wage 150 000, buy-in 50 000: tax saved 13 890; extra capital tax 4 705 at withdrawal (on top of
  400 000): net +9 185 (18.4 %); wage 250 000, buy-in 100 000: +24 909 (24.9 %). Staggering a 600 000 withdrawal
  over two years saves 12 785 (results/recreate.md). Lean: `fed_capital_500k`, `zh_capital_min_50k`.

### F15 The 25-franc minimum federal tax is a notch
- kind: loophole-known (minor). DBG Art. 36 Abs. 3. Single, taxable 18 400 to 18 500: 0 to 25.41; married with two
  children 66 400 to 66 500: 0 to 25.00. Lean: `fed_min_notch`, `fed_min_notch_income`, `fed_kids_notch`.

### F16 Private capital gains are tax-free
- kind: loophole-known. DBG Art. 16 Abs. 3, StG ZH § 16 Abs. 3. 100 000 of gains on a 100 000 wage: total tax 11 864
  vs 43 096 as interest or dividends. Income-type scanner: +37 % of income at 5 AW. The "gewerbsmässiger
  Wertschriftenhandel" practice (ESTV KS Nr. 36) is not modelled.
