import BjTax.Basic

/-! # Benin: kernel theorems instantiated; the June ORTB notch proved -/

namespace BjTax
open TaxKernel

theorem monthly_progressive : monthly.progressive = true := by decide
theorem monthly_mono : Monotone' monthly.ticks := Schedule.ticks_mono_of_progressive _ monthly_progressive
theorem monthly_convex : Convex monthly.ticks := Schedule.ticks_convex _ monthly_progressive

/-- Art. 125: 500 000 F a month bears 9 000 + 15 000 + 47 500 = 71 500 F. -/
theorem month_500k : monthTax 500000 = 71500 := by decide

/-- F1 (art. 125 2)): one franc of June pay above 60 000 F costs 3 000 F of ORTB levy (plus 0 F of ITS): the June pay
of 60 001 F nets 2 999 F less than 60 000 F. -/
theorem june_notch : (ortb 6 60001 + monthTax 60001) - (ortb 6 60000 + monthTax 60000) = 3000 := by decide

/-- On an even annual wage, the notch sits at 720 000 F a year: one more franc a year costs 3 000 F. -/
theorem annual_notch : ortbYear 720012 - ortbYear 720000 = 3000 := by decide

end BjTax
