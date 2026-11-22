import GnTax.Basic

/-! # Guinea: kernel theorems instantiated; the cost of uneven monthly pay under a final monthly withholding -/

namespace GnTax
open TaxKernel

theorem monthly_progressive : monthly.progressive = true := by decide
theorem monthly_mono : Monotone' monthly.ticks := Schedule.ticks_mono_of_progressive _ monthly_progressive
theorem monthly_convex : Convex monthly.ticks := Schedule.ticks_convex _ monthly_progressive

/-- Art. 63: 5 000 000 GNF a month bears 100 000 + 160 000 = 260 000 GNF. -/
theorem month_5m : monthTax 5000000 = 260000 := by decide

/-- F1 (arts. 63-64: the monthly withholding is final, with no annual reconciliation): 24 000 000 GNF paid as twelve
months of 2 000 000 bear 600 000 GNF; the same sum paid as 12 000 000 in two months bears 2 120 000 GNF. -/
theorem uneven_pay : 12 * monthTax 2000000 = 600000 ∧ 2 * monthTax 12000000 = 2120000 := by decide

end GnTax
