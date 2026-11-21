# Netherlands (belastingjaar 2025): findings

Model: `lean/` (lib `NLTax`, exe `nltax`, on `TaxKernel`). Amounts in euros. "Levy" = income tax (Wet IB 2001) +
premies volksverzekeringen (Wfsv). Statute texts: `law/`. Runs: `results/`, `runs/`. Lean names refer to
`lean/NLTax/Theorems.lean` unless stated. Kinds as in CONTRACT20.

### F1 The OECD deducts an employee pension contribution of 6,19 % above € 17.794
- kind: model-fix (OECD convention, reproduced under `--oecd`)
- households: all eight OECD Taxing Wages types
- amounts: OSTA S67 1 761,37; S100 3 171,41; S167 6 034,23 = 6,19 % × (wage − 17 794) to the cent at all three wage
  levels (`results/oecd_exact_oecd.md`). Rate and franchise are not in the OECD tables we hold; derived from the OECD's
  own lines (the OECD country-note page answered HTTP 403). An employee's own contributions to an occupational pension
  are not loon (Wet LB 1964 art. 11 lid 1 c), so the deduction is right; its size is the OECD's assumption.
- provisions: Wet LB 1964 art. 11; `Params.oecdPensionRate`, `Params.oecdPensionFranchise`
- status: reproduced; with it the model matches the OECD to the cent on 32 of 40 lines (F2-F5 explain the rest).

### F2 The OECD's kinderbijslag for 2025 is € 5,12 too low for two children aged 6-11
- kind: gov-error (OECD Taxing Wages 2025 lines for NLD)
- households: SP67, M100_0, M100_100, M100_67 (CTGG)
- amounts: OECD 2 802,00; statute 2 × (2 × 347,83 + 2 × 353,95) = 2 807,12 (AKW art. 12 lid 3: € 347,83 per quarter
  from 2025-01-01, Stcrt. 2024, 42409; € 353,95 from 2025-07-01, Stcrt. 2025, 21953). 2 802 / 2 = 1 401 per child
  = 2 × 347,83 + 2 × 352,67: the OECD's second-half amount (352,67) is not the amount in force; it looks like a
  forecast of the July indexation.
- provisions: AKW art. 12 lid 3. Lean: `NLTax.kbQ1`, `NLTax.kbQ3`
- status: error (OECD), immaterial. Draft note to the OECD: "Taxing Wages 2025, Netherlands: kinderbijslag for a child
  aged 6-11 in Q3-Q4 2025 is € 353,95 per quarter (AKW art. 12 lid 3 as amended by Stcrt. 2025, 21953), so CTGG for two
  children is € 2 807,12, not € 2 802,00 (SP67, M100_0, M100_100, M100_67)."

### F3 Drempelinkomen of the kindgebonden budget: € 28.406 (published) vs € 28.405,728 (statute)
- kind: gov-error, classified convention
- households: SP67, M100_0 (kgb differs by € 0,02-0,03)
- amounts: Wkb art. 1 lid 1 d: 108 % × 12 × € 2.191,80 (WML art. 8 lid 1 b, January 2025) = 28 405,728; no rounding is
  stated. The OECD, and the AHK threshold of art. 8.10 (same formula, art. 10.6b lid 3), use 28 406.
- status: convention; the model uses the statute's figure (`Params.kgbDrempelMilli`).

### F4 OECD S167: arbeidskorting € 0,18 higher than art. 8.11 gives at the OECD's own taxable income
- kind: gov-error (unexplained, immaterial)
- households: S167; CGITFP +0,05, EECSSC +0,13 (model − OECD) at unrounded wages
- status: open; corresponds to an arbeidsinkomen € 2,77 below the OECD's CGTC. Not reproducible from the statute.

### F5 The OECD sums tax bands; the statute adds a rounded "kolom III"
- kind: gov-error, classified convention (OECD) / statute rounding
- households: every OECD type; CGITLETC (statute − OECD) −0,63 per taxpayer between € 38.441 and € 76.817 and −0,95
  above (`results/oecd_exact_oecdpension.md`)
- amounts: art. 2.10 kolom III is € 3.140 (band sum 3 140,6297) and € 17.523 (band sum 17 523,9545)
- Lean: `t210_bands_gap` (0 ≤ band sum − statute ≤ € 0,9545 for every income)
- status: the statute governs; the OECD overstates income tax by these cents.

### F6 The statutory tariff falls when income crosses € 38.441 (and box 2 at € 67.804)
- kind: statute-fault
- households: single employee with € 38.441 vs € 38.442: levy 5 843,06 vs 5 842,86 (exe); tax part 3 140,63 vs
  3 140,37. Box 2: € 67.804 → € 67.805 lowers the box-2 tax from 16 611,98 to 16 611,31.
- provisions: Wet IB art. 2.10 lid 1, 2.12 (kolom III rounded down to whole euros by the yearly regeling, art. 10.1
  "de nodig geachte afronding"); Wfsv art. 8 lid 3 (premie stops at € 38.441)
- Lean: `t210_drop`, `t210_drop_euro`, `levy_drop_euro`, `t210_drop_top`, `t210_not_monotone`, `t210_not_convex`,
  `box2_drop`. The kernel's `Schedule.ticks_mono` / `ticks_convex` hold for the band sum but fail for the statute's
  table (reported to `~/cmp20/kernel/INBOX.md`).
- status: real but tiny (marginal rate −26 % on one euro, −62 % on one cent). Not found in the 20 results of a targeted
  search (WebSearch "38.441" "3.140" schijf belasting daalt afronding kolom III, 2026-11-19), nor in the Belastingdienst
  rekenvoorschriften (whose withholding table floors the combined amount and so has no drop).
- Draft issue (Ministerie van Financiën, inflatiecorrectie regeling): "In art. 2.10 lid 1 Wet IB 2001 (2025) kolom III
  (€ 3.140, € 17.523) is lower than the tax at the end of the previous row (€ 3.140,63; € 17.523,95), so the tax falls by
  € 0,63 / € 0,95 when the income passes € 38.441 / € 76.817; likewise art. 2.12 (€ 16.611 against 16 611,98). Rounding
  kolom III up, or writing the table as rates on bands, removes the drop."

### F7 The arbeidskorting never reaches its own maximum of € 5.599
- kind: statute-fault
- amounts: art. 8.11 lid 2: the 2,258 % build-up from € 26.288 would reach € 5.599 only at € 43.072,77, but the 6,51 %
  afbouw starts at € 43.071; the maximum is € 5.598,96 (at € 43.071). The same text is in Wet LB art. 22a.
- Lean: `ak_below_cap` (for every income the arbeidskorting is below € 5.599), `ak_max_value`
- status: the three amounts are indexed and rounded separately (art. 10.1); € 0,04 for a worker at € 43.071.

### F8 The algemene heffingskorting ends at € 76.820,08, not at the top-bracket start € 76.817
- kind: statute-fault (rounding by design) / gov reading
- amounts: art. 10.6b lid 2 sets the afbouw at AHK / (€ 76.817 − € 28.406) "rekenkundig afgerond op drie decimalen":
  3 068 / 48 411 = 6,3374 % → 6,337 %, so € 0,19 of AHK remains at € 76.817. The Belastingdienst's AHK table 2025 and
  the loonbelasting rekenregel (tabel 3, "inhaalafbouw") set it to € 0 from € 76.818.
- Lean: `ahk_alive_at_top`, `ahk_zero_after`
- status: at most € 0,13 per taxpayer between € 76.818 and € 76.820.

### F9 Combined statutory marginal rates above the 49,50 % top rate
- kind: loophole-known (METR)
- amounts (employee under 67, wage = income): 50,327 % on € 43.073-76.817 (37,48 + 6,337 AHK + 6,51 AK); 56,01 % on
  € 76.821-129.077 (49,50 + 6,51). Single parent with two children: 63,11 % (+ 7,10 % kgb). AOW pensioner 60,92 % near
  € 45.308-58.875 (ouderenkorting afbouw 15 %). Self-employed 60,54 % near € 80.000. No income band above 100 % without
  toeslagen (scan of seven household types, € 1 steps to € 160.000: `runs/scan.json`).
- Lean: `levy_step_middle`, `middle_exceeds_top`, `levy_step_top`
- status: known (Gielen and Beens 2023, cited in ESB, "Versimpelen belastingstelsel leidt altijd tot
  inkomensverschuivingen", https://esb.nu/versimpelen-belastingstelsel-leidt-altijd-tot-inkomensverschuivingen/: most
  workers below 60 %).

### F10 A parent with a child under 12 pays no levy on a wage up to € 30.000 (as lower earner, or alone)
- kind: loophole-new (a property of the statute)
- households: second earner with children 6 and 11 (partner at € 69.028); single parent with the same children
- amounts: AHK + AK + IACK ≥ 35,82 % of the wage for every wage up to € 30.000, so the art. 8.8 cap leaves no income tax
  and no premies; the second earner's marginal rate is then only the household's kgb afbouw (7,1 %). Without the IACK the
  levy starts at € 11.049.
- Lean: `parent_no_levy`, `no_iack_levy_at_11100`; scan: `second` METR 0,071 from 0 to 30 000; `sp` 0 to 28 300
- status: not found as such in 3 searches; the wider "niet-verzilverde heffingskortingen" issue is a known policy topic.

### F11 Rekenvoorschriften 2025: a stale example and a corrected Lmax
- kind: gov-error
- amounts: §2.2.5 of both 2025 editions (LH 099-1Z51FD and -1Z52FD, "Uitgave januari 2025") explains the Lmax margin
  with "Lmax € 125.010 / 260 = € 480,807" and a day wage of € 480,81 "× 260 = € 125.010,60", but the 2025 Lmax is
  € 129.330 (tabel 1a). The first edition printed Lmax € 129.078 (the arbeidskorting's end point arkg4), corrected in
  Z52FD (also reported by Salaris Vanmorgen).
- status: error (example not updated). Draft issue (Belastingdienst): "Rekenvoorschriften 2025 §2.2.5 uses Lmax
  € 125.010 and a day wage of € 480,81; for 2025 Lmax is € 129.330 (tabel 1a), i.e. € 497,42 per day."

### F12 Belastingdienst AHK above the AOW age: € 1.536, and a € 1,37 notch the statute does not have
- kind: gov-error, classified reading
- amounts: statute: the AOW-aged keep the IB, Anw and Wlz parts of the AHK (Wet IB art. 8.3-8.6; Wfsv art. 12 lid 1 a):
  3 068 × 17,92 / 35,82 = € 1.534,86, ending (like the full AHK) at € 76.820. Belastingdienst (AHK table 2025, "U hebt in
  2025 het hele jaar de AOW-leeftijd"; rekenvoorschriften bijlage ahkm1.2): € 1.536 − 3,170 % × (verzamelinkomen −
  28.406) up to € 76.817 (= € 1,37 there) and € 0 from € 76.818. 1 536 = 700 + 836, the IB and premium parts each
  rounded up (bijlage columns BH, AG); no rounding rule for these parts found in the Global law record.
- status: the table gives AOW-aged taxpayers € 1,14 more than the statute below € 28.406 and a € 1,37 notch at
  € 76.817/76.818. Draft issue (Belastingdienst): "The AOW-age AHK table 2025 ends at € 1,37 on € 76.817 and € 0 on
  € 76.818; under art. 8.10 with art. 8.3-8.6 the korting is 1 792/3 582 of the full AHK and ends at € 76.820."

### F13 The withholding table under-withholds by € 0 - 3,05 a year and never over-withholds by more than € 0,30
- kind: gov-error, classified convention (tables are binding; the IB assessment settles)
- households: single employee under 67, every annual table wage 0-129 330 in steps of € 54 (2 396 wages)
- amounts: monthly table × 12 − statute: min −2,64, max +0,06, mean −1,05 (`results/lb_grid.json`); kortingen rounded
  up, X rounded down (rekenvoorschriften §2.2.3-2.2.4)
- Lean: `NLTax.Withholding` (the rekenregel), `lb_vs_statute` (for every L ≤ Lmax: statute − 3,05 ≤ table ≤ statute + 0,30)
- status: convention; within these cents the rekenregel is the statute.

### F14 Wet LB art. 22a lid 2 c speaks of "arbeidsinkomen", a term the Wet LB does not define
- kind: statute-fault
- provisions: Wet LB 1964 art. 22a lid 2: a, b and d count "dat loon" / "tijdvakloon op jaarbasis"; c "2,258% van het
  arbeidsinkomen" (2026: "1,950% van het arbeidsinkomen"). "arbeidsinkomen" occurs nowhere else in the Wet LB 1964
  (Global law search, text of 2026-11-05); it is the Wet IB's term (art. 8.1 e). In the text since 2020-01-01
  (Stcrt. 2019, 66707), still in force.
- status: drafting fault (copied from Wet IB art. 8.11); harmless in practice. Draft issue: "Art. 22a lid 2 onderdeel c
  Wet LB 1964: replace 'van het arbeidsinkomen voor zover dat meer bedraagt' by 'van dat loon voorzover dit bij een
  tijdvakloon op jaarbasis meer bedraagt', as in b and d."

### F15 Art. 10.6b lid 3 Wet IB cites "artikel 8,10"
- kind: statute-fault (typo)
- provisions: art. 10.6b lid 3 "Het in artikel 8,10, tweede lid, laatstvermelde bedrag" (comma for point), added by
  Stb. 2024, 434 with effect from 2025-01-01, still in the text of 2026-11-05 (Global law phrase history). Also art.
  10.1 lid 1 "5.10,5.13".
- status: typo.

### F16 Box-3 allocation, box-2 split and the kgb wealth cliff (found by the model's own optimiser)
- kind: loophole-known
- amounts: box-3 grondslag on the non-earning partner saves € 1.675,77 (€ 250.000 of shares, partner 1 at € 45.000):
  her AHK absorbs the box-3 tax (art. 8.8: the gecombineerde inkomensheffing includes box 3). Box-2 dividend shared
  with a partner saves € 4.968,62 (two 24,5 % bands). One euro of wealth above € 179.429 on 1 January costs a couple
  with two children € 4.225,23 of kindgebonden budget (Wkb art. 1 lid 4).
- status: recreated (`runs/recreate.json`, CATALOGUE.md K2, K3, K7).

### F17 Bunching income across the end of the arbeidskorting afbouw saves up to € 3.540 (single) / € 8.234 (parent)
- kind: loophole-new (timing; found by the kernel's `timing` scanner, checked with the exe)
- households: single employee, € 129.083 in each of two years vs € 198.112 + € 60.055: levy 108 047,20 vs 104 507,06;
  single parent with children 6 and 11, € 146.616 twice vs € 215.645 + € 77.588: gain € 8.234,35
- provisions: Wet IB art. 8.11 lid 2 d, 2.10; Wkb art. 2 lid 7 (the afbouw bands end, so the levy is concave there)
- Lean: `levy_step_top` (56,01 % up to € 129.077); top rate 49,50 % above
- status: not found in the sources read (4 web searches); NOVEL N7.

### F18 Box 3 is taxed at 42-49 % of the deemed return for incomes in an afbouw band
- kind: loophole-known (rate stacking; priority box-3 scan)
- amounts: the deemed return is part of the verzamelinkomen (art. 2.18 c), on which the AHK (6,337 %) and the kgb
  (7,10 %) are phased out: 36 % + 6,337 % (+ 7,10 %). € 500.000 of shares: € 11.011 for an employee at € 50.000
  (2,20 % of wealth); effective rate on an actual 4 % return 55 %, on 2 % 110 % (`runs/box3.json`).
- provisions: art. 2.13, 2.18, 5.2, 8.10; Wkb art. 2; HR 24-12-2021 ECLI:NL:HR:2021:1963 (actual return route, not
  modelled)
- status: recreated; NOVEL N8.
