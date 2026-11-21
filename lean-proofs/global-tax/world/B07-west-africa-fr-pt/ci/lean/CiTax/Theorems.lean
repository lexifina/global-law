import CiTax.Basic

/-! # Côte d'Ivoire: kernel theorems instantiated; the printed RICF and part tables checked -/

namespace CiTax
open TaxKernel

theorem monthly_progressive : monthly.progressive = true := by decide
theorem monthly_mono : Monotone' monthly.ticks := Schedule.ticks_mono_of_progressive _ monthly_progressive
theorem monthly_convex : Convex monthly.ticks := Schedule.ticks_convex _ monthly_progressive
theorem monthly_no_jump {x y : Int} (h : x ≤ y) : monthly.ticks y - monthly.ticks x ≤ monthly.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ monthly_progressive h).2

/-- Art. 120 1°: the printed annual RICF column is 12 times the monthly column (66 000 ... 528 000). -/
theorem ricf_annual : 12 * ricfMonthly 3 = 66000 ∧ 12 * ricfMonthly 4 = 132000 ∧ 12 * ricfMonthly 10 = 528000 := by decide

/-- Art. 120 2°: the part table, row by row. -/
theorem parts_table :
    halfParts false 0 = 2 ∧ halfParts true 0 = 4 ∧ halfParts false 1 = 4 ∧ halfParts true 1 = 5 ∧
    halfParts false 2 = 5 ∧ halfParts true 2 = 6 ∧ halfParts false 3 = 6 ∧ halfParts true 3 = 7 ∧
    halfParts false 4 = 7 ∧ halfParts true 9 = 10 := by decide

/-- Barème check (art. 119 bis): 240 000 F a month bears 16 % of 165 000 = 26 400 F. -/
theorem month_240k : monthTax 240000 = 26400 := by decide

/-- F1: a married employee (2 parts) pays no ITS up to a monthly pay of 143 750 F (16 % of 68 750 = 11 000 = RICF). -/
theorem married_zero : monthNet 4 143750 = 0 ∧ monthNet 4 143760 > 0 := by decide

/-- F2: marriage is worth 11 000 F a month (132 000 F a year) of RICF to each married employee with enough tax: two
cohabiting earners with 300 000 F each pay 2 × 132 000 F a year more than the same couple married (reading of art. 120). -/
theorem marriage_bonus : 12 * (monthNet 2 300000 - monthNet 4 300000) = 132000 := by decide

end CiTax
