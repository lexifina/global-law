import FiTax.Tests

/-!
# Finland 2025: the findings as theorems (FINDINGS.md F-numbers), checked by `decide` (cents, Helsinki 5,30 %,
age 40 unless stated, no church tax)
-/

namespace FiTax
open TaxKernel

/-- Everything one person pays (state + capital + YLE + municipal + church tax, contributions), no spouse. -/
def personTotal (r : Rates) (p : Person) : Int :=
  let x := finishAlone (stage r p) p 0
  x.stateTotal + x.st.yle + x.local + x.employee

def helsinki : Rates := {}

/-- F1: one cent of pay at 16 861,99 € costs 141,64 € of päivärahamaksu; the pay must reach 17 022 € before the
worker is as well off as at 16 861,99 € (a 160 € dead zone). -/
theorem f1_daily_notch :
    personTotal helsinki { wages := 1686200 } - personTotal helsinki { wages := 1686199 } = 14164 ∧
    1702100 - personTotal helsinki { wages := 1702100 } < 1686199 - personTotal helsinki { wages := 1686199 } ∧
    1702200 - personTotal helsinki { wages := 1702200 } ≥ 1686199 - personTotal helsinki { wages := 1686199 } := by
  decide

/-- F2: the 2025 work credit is still withdrawn (3,44 %) up to 125 240 € of pay, so 10 000 € more pay at 110 000 €
costs more than at 400 000 € (55,99 % vs 54,85 %: above the top rate). -/
theorem f2_hump :
    personTotal helsinki { wages := 12000000 } - personTotal helsinki { wages := 11000000 }
      > personTotal helsinki { wages := 41000000 } - personTotal helsinki { wages := 40000000 } := by decide

/-- F3: because the tax is not convex there, bunching pays: 155 000 € + 97 000 € over two years costs 950,36 € less
than 126 000 € in each. -/
theorem f3_bunching :
    2 * personTotal helsinki { wages := 12600000 }
      - (personTotal helsinki { wages := 15500000 } + personTotal helsinki { wages := 9700000 }) = 95036 := by decide

/-- F4: an owner with no salary and no net assets takes 20 000 € of dividend: 15 000 € is earned income (TVL 33 b §
2 mom) covered by the perusvähennys and the work credit, no contributions: 0 € of personal tax. With net assets of
250 000 € or more the same dividend is 5 000 € of capital income: 1 500 €. -/
theorem f4_owner_zero_assets :
    personTotal helsinki { earnedDiv := 1500000 } = 0 ∧ personTotal helsinki { capital := 500000 } = 150000 := by
  decide
theorem f4_split_zero : unlistedSplit 2000000 0 = (0, 1500000) := by decide
theorem f4_split_250k : unlistedSplit 2000000 25000000 = (500000, 0) := by decide

/-- F5: 60 000 € of capital gains in one year cost 1 040 € more than 30 000 € in each of two (30/34 %). -/
theorem f5_capital_timing :
    personTotal helsinki { capital := 6000000 } - 2 * personTotal helsinki { capital := 3000000 } = 104000 := by
  decide

/-- F6: the same 25 000 € taxed as pension (age 70) or as pay (age 40): the pensioner pays 750,23 € more. -/
theorem f6_pension_vs_pay :
    personTotal helsinki { age := 70, pension := 2500000 } - personTotal helsinki { wages := 2500000 } = 75023 := by
  decide

/-- F7: a single parent of two (5 and 9) who marries loses the child-benefit supplement (1 759,20 €/year) and half of
the doubled work-credit increase (100 €). -/
theorem f7_marriage_cb : 12 * (childBenefitMonth [9, 5] true - childBenefitMonth [9, 5] false) = 175920 := by decide
theorem f7_marriage_wc :
    workCreditMaxOf { wages := 3000000, kids := 2, sole := true } - workCreditMaxOf { wages := 3000000, kids := 2 } = 10000 := by
  decide

/-- F8: a 2 000 € capital deficit of a low earner (12 000 € pay) gives a 600 € credit that no tax can absorb this
year (it becomes a capital loss to carry forward, TVL 60 § 2 mom); a spouse could have used it (134 §). -/
theorem f8_deficit_lost :
    (finishAlone (stage helsinki { wages := 1200000, capital := -200000 }) { wages := 1200000, capital := -200000 } 0).deficitLost
      = 60000 := by decide

/-- G1 (HE 98/2025, 2025 law): "Kun puhdas ansiotulo ylittää noin 125 300 euroa, työtulovähennystä ei enää myönnetä."
The credit already ends at a puhdas ansiotulo of 124 490 €: at 124 500 € it is 0 (125 240 € is the *pay*). -/
theorem g1_he98_threshold :
    netEarned { wages := 12525000 } = 12450000 ∧ workCredit { wages := 12525000 } = 0 ∧
    0 < workCredit { wages := 12523000 } := by decide

/-- G2 (HE 108/2024, 2024 law): "Ansiotulovähennystä ei myönnetä osittaisenakaan, jos ... puhtaan ansiotulon määrä
ylittää noin 94 084 euroa." TVL 105 a § (1123/2022): max 3 570 €, "pienenee 4,5 prosentilla puhtaan ansiotulon
14 000 euroa ylittävältä osalta": it ends at 93 333,33 € of puhdas ansiotulo (94 083,33 € is the pay). -/
def earnedIncomeDeduction2024 : Taper := { full := eur 3570, start := eur 14000, num := 45, den := 1000 }
theorem g2_he108_threshold :
    earnedIncomeDeduction2024.amount 9333334 = 0 ∧ 0 < earnedIncomeDeduction2024.amount 9333300 ∧
    earnedIncomeDeduction2024.amount 9408400 = 0 := by decide

end FiTax
