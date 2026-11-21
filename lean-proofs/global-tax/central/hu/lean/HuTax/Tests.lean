import HuTax.Household

/-!
# Official worked figures, checked by the kernel (`decide`)

Sources: NAV information booklet 73 "Szja adóalap-kedvezmények" (published 2025-09-16, `refs/nav/nav73.txt`),
NAV 100 "Az egyéni vállalkozók átalányadózásának alapvető szabályai" (2025-01-24, `refs/nav/nav100.txt`), NAV 99 KATA
(2025-01-14, `refs/nav/nav99.txt`), and the OECD Taxing Wages 2025 country table for Hungary (M100_0).
-/

namespace HuTax
open TaxKernel

/-! ## NAV 73 § 5.2 and § 6.2: under-25 and under-30 mothers' caps -/
/-- "656 785 forint, ami 98 518 forinttal csökkentheti a fizetendő adót" -/
theorem nav73_youth_month : pct pitRate youthCapMonthly = 98518 := by decide
/-- "az adóalap legfeljebb 7 881 420 forinttal csökkenthető, ami adóban kifejezve 1 182 213 forintot jelent" -/
theorem nav73_youth_year : 12 * youthCapMonthly = 7881420 ∧ pct pitRate (12 * youthCapMonthly) = 1182213 := by decide

/-! ## NAV 73 § 7: personal allowance; § 8: first marriage -/
/-- "a teljes évre 1 162 800 forinttal csökkenthető az összevont adóalap. Adóban kifejezve ez 174 420 forint" -/
theorem nav73_personal : 12 * personalMonthly = 1162800 ∧ pct pitRate (12 * personalMonthly) = 174420 := by decide
/-- "33 335 forint, ami azt jelenti, hogy az általuk fizetendő adó összege 5 ezer forinttal csökken" -/
theorem nav73_first_marriage : pct pitRate firstMarriageMonthly = 5000 := by decide

/-! ## NAV 73 § 9.4: the monthly family allowance table (allowance, tax value) before and from July 2025 -/
theorem nav73_table_h1 :
    (famMonth famH1 famDisabledH1 1 1 0, pct pitRate (famMonth famH1 famDisabledH1 1 1 0)) = (66670, 10001) ∧
    (famMonth famH1 famDisabledH1 2 1 0, pct pitRate (famMonth famH1 famDisabledH1 2 1 0)) = (133330, 20000) ∧
    (famMonth famH1 famDisabledH1 2 2 0, pct pitRate (famMonth famH1 famDisabledH1 2 2 0)) = (266660, 39999) ∧
    (famMonth famH1 famDisabledH1 3 1 0, pct pitRate (famMonth famH1 famDisabledH1 3 1 0)) = (220000, 33000) ∧
    (famMonth famH1 famDisabledH1 3 2 0, pct pitRate (famMonth famH1 famDisabledH1 3 2 0)) = (440000, 66000) ∧
    (famMonth famH1 famDisabledH1 3 3 0, pct pitRate (famMonth famH1 famDisabledH1 3 3 0)) = (660000, 99000) := by
  decide
theorem nav73_table_h2 :
    (famMonth famH2 famDisabledH2 1 1 0, pct pitRate (famMonth famH2 famDisabledH2 1 1 0)) = (100000, 15000) ∧
    (famMonth famH2 famDisabledH2 2 1 0, pct pitRate (famMonth famH2 famDisabledH2 2 1 0)) = (200000, 30000) ∧
    (famMonth famH2 famDisabledH2 2 2 0, pct pitRate (famMonth famH2 famDisabledH2 2 2 0)) = (400000, 60000) ∧
    (famMonth famH2 famDisabledH2 3 1 0, pct pitRate (famMonth famH2 famDisabledH2 3 1 0)) = (330000, 49500) ∧
    (famMonth famH2 famDisabledH2 3 2 0, pct pitRate (famMonth famH2 famDisabledH2 3 2 0)) = (660000, 99000) ∧
    (famMonth famH2 famDisabledH2 3 3 0, pct pitRate (famMonth famH2 famDisabledH2 3 3 0)) = (990000, 148500) := by
  decide

/-- NAV 73 § 9.4: two children, one severely disabled: "az év első felében 333 330 forint", "A második félévben
a kedvezmény összege 500 000 forint". -/
theorem nav73_disabled_child :
    famMonth famH1 famDisabledH1 2 2 1 = 333330 ∧ famMonth famH2 famDisabledH2 2 2 1 = 500000 := by decide

/-- NAV 73 § 13, the Kedves family: three dependants all year, three beneficiaries January-July and two from August:
"(3x6x220 000+3*330 000+2x5x330 000 =) 8 250 000 forint"; less 667 % of the 135 000 + 50 000 contribution allowance
used during the year: "8 250 000–900 450–333 500 = 7 016 050". -/
def kedvesMonths : List (Nat × Nat × Nat × Nat) :=
  [(1,3,3,0),(2,3,3,0),(3,3,3,0),(4,3,3,0),(5,3,3,0),(6,3,3,0),(7,3,3,0),
   (8,3,2,0),(9,3,2,0),(10,3,2,0),(11,3,2,0),(12,3,2,0)]
theorem nav73_kedves_frame : famFrameMonths kedvesMonths = 8250000 := by decide
theorem nav73_kedves_after_credit : frameAfterInYearCredit 8250000 (135000 + 50000) = 7016050 := by decide

/-- NAV 73 § 12, the tutor: two children, allowance shared equally, January-March income 3 × 140 000:
"(3x133 330 =) 399 990 ... (420 000–399 990 =) 20 010 forint jövedelme és (20 010x0,15 =) 3 002 forint". -/
theorem nav73_tutor : 3 * famRate famH1 2 = 399990 ∧ pct pitRate (420000 - 3 * famRate famH1 2) = 3002 := by decide

/-! ## NAV 100 § 3-4: átalányadó -/
/-- "7 000 000 forint vállalkozói bevétele ... 4 200 000 forint ... 1 744 800 forint adómentes, tehát a 2 455 200
forint 15%-át, azaz 368 280 forintot" -/
theorem nav100_graphic_designer :
    atalanyIncome 7000000 atalanyCostDefault = 4200000 ∧ atalanyFree = 1744800 ∧
    pct pitRate (atalanyTaxable (atalanyIncome 7000000 atalanyCostDefault)) = 368280 := by decide
/-- First quarter: "1 860 000 forint. Az 1 744 800 forintos adómentes értékhatárt meghaladóan 115 200 forint összegű
adóköteles jövedelme keletkezett, ezért ebben a negyedévben 17 280 forint adóelőleget" -/
theorem nav100_first_quarter :
    atalanyIncome 3100000 atalanyCostDefault = 1860000 ∧ atalanyTaxable 1860000 = 115200 ∧
    pct pitRate 115200 = 17280 := by decide
/-- "a szociális hozzájárulási adó alapja havonta legalább 327 150 forint, garantált bérminimum alkalmazásakor
392 400 forint" = 112.5 % of 290 800 and of 348 800. -/
theorem nav100_szocho_min : szochoMinMonthly * 1000 = 1125 * minWage ∧
    szochoMinMonthlySkilled * 1000 = 1125 * guaranteedMinWage := by decide

/-! ## NAV 99 § 4.2: KATA -/
/-- "2025. március 1-jétől a kata alanya, év végéig 17 millió forint bevételre ... (10 hónap x 1,5 millió forint),
2 millió forint után 40 százalékos különadót kell fizetnie" (+ 10 × 50 000 tételes adó). -/
theorem nav99_kata : kataTax { kata := true, kataRevenue := 17000000, kataMonths := 10 } = 500000 + 800000 := by
  decide

/-! ## OECD Taxing Wages 2025, Hungary, M100_0 (one earner at the average wage, two children):
CGTC 4 455 527.31, CGITFP 668 329.10, EECSSC 1 564 265.15, CTGG 319 200 (OECD.CTP.TPS DF_TW_COU, 2025). -/
def oecdM100_0 : House :=
  { persons := [{ wages := 8455487 }, {}], couple := true, deps := 2, bens := 2, disabledKids := 0 }
theorem oecd_m100_0 :
    (compute oecdM100_0).taxable = [4455527, 0] ∧ (compute oecdM100_0).szja = [668329, 0] ∧
    (compute oecdM100_0).tb = [1564265, 0] ∧ (compute oecdM100_0).csp = 319200 := by decide

end HuTax
