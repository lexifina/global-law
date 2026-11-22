import SETax.Table

/-!
# Official worked examples (Skatteverket, *Teknisk beskrivning SKV 433, 2025*, 2024-12-16), checked by `decide`

Each test quotes the example's input and result and the section it is in. The table examples use table 34
("skatte- och avgiftssats av 34 %", municipal rate 34 − 1,16 = 32,84 %: `tableParams 34`). The OECD's 2025 figures
for Sweden are referee (a) and are checked by `harness/oecd_check.py` (56 of 56 lines equal); two of them are
repeated here as theorems.
-/

namespace SETax
open TaxKernel

-- 6.1 Exempel 1: "Bruttolön för hela året 120 000 ... grundavdraget 37 300 kr"
theorem skv_ga_ex1 : ga p2025 false 120000 = 37300 := by decide
-- 6.1 Exempel 2: "Bruttolön för hela året 324 000 ... grundavdraget 31 200 kr"
theorem skv_ga_ex2 : ga p2025 false 324000 = 31200 := by decide
-- 6.2 Exempel 1 (>66 år): "Fastställd förvärvsinkomst (FFI) 200 000 ... 110 100 kr"
theorem skv_fga_ex1 : ga p2025 true 200000 = 110100 := by decide
-- 6.2 Exempel 2: "Fastställd förvärvsinkomst 90 000 kr ... 71 700 kr"
theorem skv_fga_ex2 : ga p2025 true 90000 = 71700 := by decide
-- 6.2 Exempel 3: "Fastställd förvärvsinkomst 390 000 ... 147 100 kr"
theorem skv_fga_ex3 : ga p2025 true 390000 = 147100 := by decide
-- 7.2: "20 % x(695 000 – 625 800) 69 200 = 13 840 kr"
theorem skv_state_ex : (stateSchedule p2025).ticks 695000 / BP = 13840 := by decide
-- 7.4: "Årsinkomsten uppgår till 181 200 kr. Den allmänna pensionsavgiften blir 12 700 kr"
theorem skv_fee_ex : pensionFeeOn p2025 181200 0 = 12700 := by decide
-- 7.4: "Den högsta avgift som kan tas ut för 2025 är 45 500 kr"
theorem skv_fee_max : pensionFeeOn p2025 1000000 0 = 45500 := by decide
-- 7.4 / Bilaga: no fee below 24 873 kr; 7.5.2 Exempel 1 (låg inkomst): 28 000 kr gives "Allmän pensionsavgift 2 000"
theorem skv_fee_low : pensionFeeOn p2025 24800 0 = 0 ∧ pensionFeeOn p2025 28000 0 = 2000 := by decide
-- 7.5.2 Exempel 2 (låg inkomst), 55 000 kr: "Allmän pensionsavgift 3 800" (3 850 "slutar på 50", rounded down)
theorem skv_fee_tie : pensionFeeOn p2025 55000 0 = 3800 := by decide
-- 7.5.2 Exempel 1: "Arbetsinkomst 90 000 ... Skattereduktionen blir då 11 935 kr."
theorem skv_jsa_ex1 : jsa (tableParams 34) false 90000 (ga p2025 false 90000) = 11935 := by decide
-- 7.5.2 Exempel 2: "Arbetsinkomst 240 000 ... Skattereduktionen blir då 25 238 kr."
theorem skv_jsa_ex2 : jsa (tableParams 34) false 240000 (ga p2025 false 240000) = 25238 := by decide
-- 7.5.2 Exempel 3 (sjöman, fjärrfart): arbetsinkomst 250 000 − 36 000 = 214 000, grundavdrag 38 600: "23 867 kr"
theorem skv_jsa_ex3 : jsa (tableParams 34) false 214000 38600 = 23867 := by decide
-- 7.5.4 Exempel 1 and 2: BFI 200 000 gives "1200 kr per år", BFI 400 000 gives "1500 kr"
theorem skv_fi_ex : fiCredit 200000 = 1200 ∧ fiCredit 400000 = 1500 := by decide
-- 7.6 Exempel 1 and 2: BFI 120 000 gives 1 200 kr; BFI 175 000 gives "1 249 kr"
theorem skv_ps_ex : publicService p2025 true 120000 = 1200 ∧ publicService p2025 true 175000 = 1249 := by decide
-- 7.5.2 "Exempel 1 Under 66 år Årsinkomst (arbetsinkomst) 28 000 ... Summa skatt 2 066"
theorem skv_total_28000 : (person (tableParams 34) false 40 28000 0 0 0 0).total = 2066 := by decide
-- 7.5.2 "Exempel 2 Under 66 år Årsinkomst (arbetsinkomst) 55 000 ... Summa skatt 4 450"
theorem skv_total_55000 : (person (tableParams 34) false 40 55000 0 0 0 0).total = 4450 := by decide
-- the same example: "Avgår skattereduktion för arbets-Inkomst (9 584 kr men kan endast nyttja 6 084 kr)"
theorem skv_jsa_55000 :
    (person (tableParams 34) false 40 55000 0 0 0 0).jsaAmount = 9584 ∧
    (person (tableParams 34) false 40 55000 0 0 0 0).used.jobb = 6084 := by decide

-- Skatteverket open-data table 34, column 1, "inkomst fr.o.m. 20001 t.o.m. 20200": 3 632 kr (one of 26 936 cells
-- checked by harness/table_check.py)
theorem table34_20200 : tableMonthly 34 1 20200 = 3632 := by decide
theorem table34_80000 : tableMonthly 34 1 80000 = 27976 := by decide

-- OECD Taxing Wages 2025, SWE, S100 (average wage 557 053 kr): SLT 174 916, CGTC 539 700, EECSSC 39 000,
-- other tax credits 87 795 (pensionsavgift 39 000 + jobbskatteavdrag 47 295 + förvärvsinkomst 1 500)
theorem oecd_s100 :
    let r := person p2025oecd false 40 557053 0 0 0 0
    r.bfi = 539700 ∧ r.municipalTax = 174916 ∧ r.fee = 39000 ∧
      r.used.pension + r.used.jobb + r.used.forvarv = 87795 := by decide
-- S167 (930 279 kr): CGITLETC 57 420, CGITFP −36 875
theorem oecd_s167 :
    let r := person p2025oecd false 40 930279 0 0 0 0
    r.stateTaxEarned = 57420 ∧ r.stateTaxEarned - (r.used.pension + r.used.jobb + r.used.forvarv) = -36875 := by
  decide

end SETax
