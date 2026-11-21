# Denmark (København), indkomståret 2025: findings

Model: `lean/DKTax` (PSL, AMBL, LL §§ 8 A, 9 J-L, 13, børne- og ungeydelsesloven, grøn check, børnetilskud;
2023-2026 parameters, `refs/PARAMS.md`). Referees: OECD Taxing Wages country table 2023-2025 (`runs/oecd_check.json`),
Skatteministeriet's 2023 worked examples (27 `#guard`s, `lean/DKTax/Tests.lean`), Skatteministeriet's marginal-rate
table 2025-2026 (`runs/skm_marginal.json`). Searches: `harness/scans.py` (`runs/scans.json`) and the kernel's
generic scanners (`results/search/SUMMARY.md`). Theorems: `lean/DKTax/Theorems.lean`, `Loopholes.lean` (no `sorry`;
`#print axioms`: propext, Classical.choice, Quot.sound at most). Burden = state + local income tax + AM-bidrag +
ATP − cash benefits.

## Government and statute

### F1 The Global law record of personskatteloven stops at the 2021 consolidation
- kind: model-fix
- what: `denmark/national/acts/lov/1986/151` holds LBK nr. 1284 af 14/06/2021 but none of the amending acts lov nr.
  252/2022, 610/2023, 1564/2023, 108/2024 (bundskat 12,10 → 12,09 → 12,06 → 12,01 %), 482/2024 (2026 reform),
  1691/2024 (aktieindkomst 51.500 / 57.800 / 63.400 kr. (2010)). Read for 2025-06-30 it shows bundskat "12,10", and
  `compare_dates` 2025-06-30 → 2026-05-20 on § 7 reports "0 change(s)", while retsinformation's XML of LBK
  1284/2021 lists all of them as changes. Ligningsloven's 2024 § 9 J amendment is likewise absent.
- effect: a model built from the record would charge 12,10 % bundskat (about +450 kr. for an average worker) and miss
  the 2025 beskæftigelsesfradrag (12,3 %, 55.600 kr.).
- fix used: statute from retsinformation.dk XML (`refs/web/`). For the Global law owner.
- status: confirmed.

### F2 The OECD's basic-tax-credit line counts a one-earner couple's personfradrag three times
- kind: gov-error (OECD Taxing Wages country table; presentation only)
- household M100_0, every year 2022-2025: BTC 2025 = 18.591,48 = 3 × 6.197,16 (51.600 × 12,01 %); the OECD's own
  CGITFP 89.913,43 = CGITLETC 59.342,06 − 2 × 6.197,16 + AM 42.965,69. Statute: one personfradrag per person, the
  unused part to the spouse (PSL §§ 9, 10 stk. 1 and 3, 12). Tax and THP right; the BTC line is wrong.
- the Lean model (OECD mode) reproduces every other M100_0 line to 1 kr.; its BTC is 12.394.

### F3 The OECD's Danish worker: an unstated 15 % occupational pension, and ATP kept in the tax bases
- kind: gov-error (OECD; one error, two conventions)
- reproduced exactly (2025 THP 8/8 within 1 kr., 53/56 lines) only with three changes to the statute model:
  1. Assumed pension (convention, undocumented in the data): employer pension contributions of 15,086 % of gross pay
     (2025; 14,982 % 2024; 14,962 % 2023) are implied by S67's ST_ETCD (54.275,65 = 12,3 % × 417.688 + 2.900; the
     single parent's 11,5 % uses the same base) and by CGTC (S100's extra 9.338,60 = LL § 9 L 12 % × 92 % × (ATP
     3.564 + 81.024); S167 the cap 0,12 × 83.800). The 8 % AM-bidrag on those contributions (AMBL § 2, stk. 1, nr. 4)
     is not charged (DSSCIT = 8 % × GEBT + 1.188 exactly): 6.482 kr. for S100. The deductions a pension brings are
     counted, the tax on it is not.
  2. ATP (error): AM-bidrag is charged on pay including the employee's ATP contribution and ATP stays in personal
     income (bundskat base = 92 % × GEBT); Skatteministeriet's example removes it first ("[4]
     Arbejdsmarkedsbidragsgrundlag = [1]-[2]-[3]"). Over-taxation about 227 kr. (S67, S100), 373 kr. (S167), 0,04-0,07 %
     of pay.
  3. Municipal rate (convention): unrounded average 25,06798 % (PSKAT prints 25,07 %), no church tax.
- draft issue (not filed): "Taxing Wages, Denmark: (i) deduct the employee ATP contribution (DKK 1,188 in 2025) from
  the labour market contribution base and from personal income (AMBL § 2(1)(1); Skatteministeriet,
  Skatteberegningseksempel 2023, line [4]); (ii) document the assumed occupational pension (15.09 % of earnings in
  2025, implied by ST_ETCD and CGTC) and either charge the 8 % labour market contribution on it (AMBL § 2(1)(4)) or
  leave it out of the allowance bases; (iii) BTC for M100_0 shows three personal allowances (F2)."
- status: confirmed by exact reproduction (`oecd := true`).

### F4 Seven misprints in Skatteministeriet's 2023 worked examples (totals unaffected)
- kind: gov-error (guidance, minor). Sources: "Skatteberegningseksempel for en ugift skatteyder i 2023" and "… for et
  ægtepar i 2023" (svmn.dk, 07-08-2023; refs/web).
  1. ugift Tabel 1: line "[8]" is labelled "Personlig indkomst [6]+[7]-[8]"; the ratepension line (60.900) is missing.
  2. ugift [59] "3.243,25": 15 % of 21.625 is 3.243,75 (as [63] and [65] use).
  3. ugift [60] "Nettokapitalindkomst over 48.000": the 2023 grundbeløb is 48.800.
  4. ægtepar [24] spouse 2 "302.712": [9] is 302.721 ([27] uses 302.721).
  5. ægtepar [41] "706.117": [4] is 706.114.
  6. ægtepar [49] "(25,4 pct. + 0,72 pct.)": Ballerup's rate is 25,5 % (the amount uses it).
  7. ægtepar Tabel 3 IV "bundfradraget på 45.800 kr.": the 2020 amount; 2023's is 48.800 ([69] uses it).
- reading (not counted): both apply 8 % AM-bidrag to ATP in the ekstra pensionsfradrag base ([36]); ATP is not in
  AMBL § 2, stk. 1, nr. 4. At most 33 kr. of deduction, capped away in both examples.
- every consistent printed figure is reproduced to the øre (27/27 `#guard`s).

### F5 Skatteministeriet's marginal-rate page dates the toptopskat to 2025
- kind: gov-error (guidance, minor). "Marginalskatteprocenter siden 1993" (16-01-2026): "Eksempel (toptopskatteyder)
  … marginalskatten for lønindkomst i 2025 … 0,08 + (1 - 0,08) x (0,25049 + 0,1201 + 0,075 + 0,075 + 0,05) = 0,605".
  Toptopskat applies from 2026 only (lov 482/2024 § 10, stk. 4), and 25,049 % is the 2026 average. The table's 16
  rates for 2025-2026 are reproduced within printed rounding.

### F6 The reform renamed "topskat" to "mellemskat" in two other laws 19 months early
- kind: statute-fault (known; corrected)
- lov 482/2024 § 8 (grøn check § 2) and § 9 (skattekontrolloven § 73) took effect 1 June 2024 because § 10, stk. 4
  gave 2026 effect only to §§ 1, 2 nr. 2 and 4, and 4-6; until February 2025 the grøn check referred to a "mellemskat
  efter personskattelovens § 7" that did not exist. The bill L 117 (2024-25, bemærkninger, retsinformation
  eli/ft/202412L00117) says the change was "gennemført for tidligt"; lov 96/2025 § 3 and § 5 reversed it; lov
  1642/2025 § 3 made it again with effect from 2026. No tax effect (same base).
- found by reading the amending acts' effect clauses against each other (versioned law).

### F7 A dead cross-reference in the 2025 topskat base
- kind: statute-fault (minor; removed from 2026)
- PSL § 7, stk. 1, 3, 7 and § 13, stk. 3-5 add back "beløb omfattet af beløbsgrænsen i pensionsbeskatningslovens
  § 16, stk. 1, 4. pkt.": the kapitalpension cap, "0 kr." for every year after 2012 (PBL, LBK 1327/2020). Empty since
  2013; deleted by lov 482/2024 § 1 nr. 2-4, 11-14 from 2026. A reader taking it for today's ratepension cap (§ 16,
  stk. 2) would add ratepension back into the topskat base; Skatteministeriet's example rightly does not.
- caveat: amendments of PBL § 16, stk. 1 after 2020 not checked sentence by sentence.

### F8 The grøn check's 140 kr. supplement has no year in the statute but is not paid after 2022
- kind: reading (open; not counted)
- LBK 1306/2022 § 1, stk. 4: "Til personer, som opfylder betingelserne i stk. 1, ydes et skattefrit tillæg på 140 kr."
  (withdrawn above a topskat base of 212.000 kr. (2010), § 2, stk. 3); stk. 1 gives non-pensioners an amount "for
  indkomståret 2022" only. Skatteministeriet's history table shows "-" for non-pensioners in 2023-2024. If the year
  does not carry over, low-income adults (topskat base up to 277.800 kr. in 2025) would be owed 140 kr. The model
  follows the ministry.

## Loopholes and traps (known: recreated without being told; new: not found in the sources searched)

### F9 Marriage taxes a spouse's interest income in the other spouse's topskat
- kind: loophole-known (a trap). Found by the marriage-toggle scan (40.000 random couples: 3.874 penalties, max
  24.362 kr.; `runs/scans.json` B); every large penalty is this one.
- household: one spouse lives on 400.000 kr. of interest, the other earns 1.000.000 kr.: married they pay 19.159 kr.
  more than unmarried (`Loopholes.marriage_capital_penalty`). PSL § 7, stk. 8-10: the couple's positive
  nettokapitalindkomst over 2 × 52.400 kr. is taxed "hos den af ægtefællerne, der har det højeste beregningsgrundlag",
  at 6,49 % in København (15 % cut by the 42 % skatteloft); unmarried, the low earner's 347.600 kr. over the
  grundbeløb stays below her own 611.800 kr. threshold.
- known: stated in a Folketing answer to Skatteudvalget (ft.dk, found in 1 search). The kernel's unit scanner (wages
  only) finds no penalty: it takes capital income.

### F10 Owner-managers: salary to the top, then dividends up to 67.500 kr.
- kind: loophole-known (recreated by scan C): for any profit above about 700.000 kr. the best split is salary up to
  profit − 90.000 kr. and 90.000 × 78 % = 70.200 kr. of dividend (22 % selskabsskat, SEL § 17), worth 9.863 kr. a
  year for a single and 19.741 kr. for spouses who each hold half the shares (`Loopholes.owner_manager_dividend_band`).
  Dividends within the progressionsgrænse bear 43,06 % against 54,47 % on København pay. Above it dividends (54,76 %)
  are slightly dearer than København pay (54,47 %) but cheaper than pay in the average municipality (55,90 %): the
  ordering depends on the kommuneskat.

### F11 Dividends bunched in one year cost 15 % of the excess over 67.500 kr.
- kind: loophole-known (recreated): 135.000 kr. in one year instead of 67.500 kr. in each of two costs 10.125 kr.
  (`Loopholes.dividend_bunching`; PSL § 8 a, stk. 1-2 per indkomstår).

### F12 Timing across the 2025→2026 reform
- kind: loophole-known (consequence of the enacted rates; recreated by scan D)
- moving 100.000 kr. of pay from 2025 to 2026 saves 6.776 kr. at 750.000 kr. (`defer_bonus_2026`) and about 100 kr.
  at most other incomes; above about 2,7 mio. kr. paying in 2025 is cheaper (4.498 kr. at 3,0 mio.,
  `accelerate_bonus_2025_toptop`; toptopskat 5 % from 2026). PSL §§ 7-8 as amended by lov 482/2024.

### F13 Parents' marginal rate exceeds the skatteloft: 56,3 % from 997.878 kr. of pay
- kind: loophole-known (a trap). The kernel's phase-out scanner flags bands above the statutory top rate (54,47 % in
  København) for every family with children: 8 % + 92 % × 50,51 % + 92 % × 2 % (børne- og ungeydelse § 1 a taper on
  the topskat base above 917.000 kr.) = 56,3 %, until a parent's share is gone (with ligedeling a parent's half,
  14.976 kr. for children aged 6 and 11, lasts 748.800 kr. of base: pay 997.878-1.812.078 kr.). The skatteloft
  (§ 19) caps tax rates, not the taper (`Theorems.buy_step`: 50 kr. more base, 1 kr. less ydelse). The mechanism is
  statutory; the excess over the skatteloft was not found stated in the 3 Skatteministeriet pages read.

### F14 Bunching pays at the end of the børne- og ungeydelse taper
- kind: loophole-new (small; not found in the 3 Skatteministeriet pages and 2 statutes read)
- the kernel's timing scanner: a one-earner couple with two children gains up to 6.193 kr. (1,15 % of AW) by earning
  2.148.284 kr. and 1.104.218 kr. in two years instead of 1.626.251 kr. in each, because the 2 % taper ends:
  bunching exhausts the ydelse in one year and keeps it whole in the other. Any finite taper is non-convex; the Danish
  one is large enough to matter at 2-4 × AW. Lean: the taper step is `Theorems.buy_step`; the household figures are
  in `results/search/timing.json`.

### F15 Dividend-only taxpayers lose their personfradrag
- kind: loophole-known (a trap): the income-type scanner finds dividends costing up to 16 % of income more than the
  same wages at 0,25 AW. PSL § 9 sets the personfradrag against §§ 6-8 and § 8 a, stk. 2 only; the 27 %
  aktieindkomstskat (§ 8 a, stk. 1, "endelig skat") cannot absorb it. Married, the unused value goes to the spouse
  (§ 10, stk. 3).

### F16 Marriage bonus from transferable allowances
- kind: loophole-known (recreated): the unit scanner's bonus of up to 18.324 kr. (one earner, 0,45 AW) is the
  non-earning spouse's personfradrag value (51.600 × (12,01 + 23,50) %) transferred under § 10, stk. 3
  (`Theorems.pf_transfer_never_costs`). No marriage penalty on wages alone (0 points of the kernel's grid); penalties
  need capital income (F9).

### F17 Model notes (not findings)
- kind: model-fix. (a) METR above 100 % at the first krone of pay in every scanner: the canonical household gets the
  full-time ATP contribution (1.188 kr.) from 1 kr. of pay; ATP is charged by hours, which the contract does not
  carry. (b) Edge scanner: falls of 1 kr. from rounding the beskæftigelsesfradrag to the nearest krone as
  Skatteministeriet's example does (the statute gives no rounding). (c) rentalIncome is not modelled.
