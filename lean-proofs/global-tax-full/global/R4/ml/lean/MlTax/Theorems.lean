import MlTax.Basic

/-! # Mali: kernel theorems instantiated; the two-point reduction's zero band proved -/

namespace MlTax
open TaxKernel

theorem sched_progressive : sched.progressive = true := by decide
theorem sched_mono : Monotone' sched.ticks := Schedule.ticks_mono_of_progressive _ sched_progressive
theorem sched_convex : Convex sched.ticks := Schedule.ticks_convex _ sched_progressive
theorem split_ok (a b : Int) : splitting sched.ticks a b ≤ separate sched.ticks a b :=
  splitting_le_separate _ sched_convex sched_mono a b

/-- Art. 10: the barème's band limits are odd numbers (578 400, 1 789 733, 2 384 195, 3 494 130): the tax at the
top-band threshold is 693 219 F (whole francs, rounded down). -/
theorem tax_top_threshold : divR .down (sched.ticks 3494130) BP = 693219 := by decide

/-- F1 (art. 12-A, reading): with the two points taken off, a single person pays no ITS up to an income of about
550 000 F (5 % on the excess over 330 000 F is less than 2 % of the income), well above the 330 000 F zero band. -/
theorem two_point_zero : its false 0 550000 = 0 ∧ its false 0 560000 > 0 := by decide

end MlTax
