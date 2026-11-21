import MkTax.Basic

/-! # North Macedonia: kernel theorems instantiated -/

namespace MkTax
open TaxKernel

theorem sched_progressive : schedule.progressive = true := by decide
theorem sched_mono : Monotone' schedule.ticks := Schedule.ticks_mono_of_progressive _ sched_progressive
theorem sched_convex : Convex schedule.ticks := Schedule.ticks_convex _ sched_progressive
theorem individual_ok (a b : Int) : splitting schedule.ticks a b ≤ separate schedule.ticks a b :=
  splitting_le_separate _ sched_convex sched_mono a b

/-- F1: the employee's contribution rate (28 %) is almost three times the tax rate; above the reduction the
combined marginal rate on gross pay is 28 % + 10 % × 72 % = 35,2 %. -/
theorem combined_marginal : contrib 1000000 + taxOf (wageBase 1000000) - (contrib 990000 + taxOf (wageBase 990000)) = 3520 := by decide

end MkTax
