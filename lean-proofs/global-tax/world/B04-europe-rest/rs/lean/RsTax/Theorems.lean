import RsTax.Basic

/-! # Serbia: the salary tax and the annual tax's structure -/

namespace RsTax
open TaxKernel

def salarySchedule : Schedule := Schedule.flatAbove monthlyNonTaxable wageRate
theorem salary_progressive : salarySchedule.progressive = true := by decide
theorem salary_mono : Monotone' salarySchedule.ticks := Schedule.ticks_mono_of_progressive _ salary_progressive
theorem salary_convex : Convex salarySchedule.ticks := Schedule.ticks_convex _ salary_progressive

/-- F1: the salary tax is levied month by month with no annual reconciliation, so one income paid unevenly over the year
pays more than the same income paid evenly: 12 × 50 000 evenly pays 12 × 2 158 = 25 896 RSD; paid as 600 000 in one
month and nothing in eleven it pays 57 158 RSD (the eleven unused monthly non-taxable amounts are lost). -/
theorem uneven_costs_more :
    salaryTax 600000 = 25896 ∧ salaryTaxMonth 600000 = 57158 := by decide

/-- F2: the annual tax (art. 87-89) with an illustrative `A` (not the 2025 value) is zero up to three average salaries
of net income, and for a person under 40 up to six (art. 87 ст. 4). -/
theorem annual_zero_below_3A : annualTax 1000000 2999999 false 0 = 0 := by decide
theorem annual_under40_zero_below_6A : annualTax 1000000 5999999 true 0 = 0 := by decide

end RsTax
