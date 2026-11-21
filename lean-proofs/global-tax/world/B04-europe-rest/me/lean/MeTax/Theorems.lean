import MeTax.Basic

/-! # Montenegro: kernel theorems instantiated; the instruction's printed column checked -/

namespace MeTax
open TaxKernel

theorem monthly_progressive : monthlySchedule.progressive = true := by decide
theorem monthly_mono : Monotone' monthlySchedule.ticks := Schedule.ticks_mono_of_progressive _ monthly_progressive
theorem monthly_convex : Convex monthlySchedule.ticks := Schedule.ticks_convex _ monthly_progressive
theorem self_progressive : annualSelfSchedule.progressive = true := by decide

/-- The instruction's "27,00€+15%" is 9 % of 300 €: the printed column equals the bands. -/
def probes : List Int := [0, 1, 69999, 70000, 70001, 99999, 100000, 100001, 500000]
theorem printed_eq_bands : cumAgrees printedMonthly monthlySchedule probes = true := by decide

/-- F1: the self-employment tariff is the monthly wage tariff × 12 (8 400 = 12 × 700, 12 000 = 12 × 1 000): a year of
equal monthly pay and the same annual self-employment income pay the same tax. -/
theorem annual_is_12_months : annualSelfSchedule.ticks 1800000 = 12 * monthlySchedule.ticks 150000 := by decide

/-- F2: monthly taxation without annual reconciliation: 18 000 € paid evenly pays 12 × 102 € = 1 224 €; paid in one
month it pays 2 577 €. -/
theorem uneven_costs_more : wageTaxC 18000 = 122400 ∧ taxMonthC 1800000 = 257700 := by decide

end MeTax
