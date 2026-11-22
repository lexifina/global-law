import GwTax.Basic

namespace GwTax
open TaxKernel

theorem marginal_mono : Monotone' ipMarginal.ticks := Schedule.ticks_mono_of_progressive _ marginal_progressive
theorem marginal_convex : Convex ipMarginal.ticks := Schedule.ticks_convex _ marginal_progressive
theorem self_mono : Monotone' selfSchedule.ticks := Schedule.ticks_mono_of_progressive _ self_progressive
/-- The printed art. 27(1) table is not monotone: one franc more a month above 400.500 lowers the tax by 16.020. -/
theorem printed_table_falls : ipMonth 400501 < ipMonth 400500 := by decide

end GwTax
