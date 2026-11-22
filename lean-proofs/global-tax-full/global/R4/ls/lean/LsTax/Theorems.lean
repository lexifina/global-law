import LsTax.Basic

namespace LsTax
open TaxKernel

theorem sched_mono : Monotone' sched.ticks := Schedule.ticks_mono_of_progressive _ sched_progressive
theorem sched_convex : Convex sched.ticks := Schedule.ticks_convex _ sched_progressive
theorem sched_no_jump {x y : Int} (h : x ≤ y) : sched.ticks y - sched.ticks x ≤ sched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ sched_progressive h).2
theorem split_ok (a b : Int) : splitting sched.ticks a b ≤ separate sched.ticks a b :=
  splitting_le_separate _ sched_convex sched_mono a b

end LsTax
