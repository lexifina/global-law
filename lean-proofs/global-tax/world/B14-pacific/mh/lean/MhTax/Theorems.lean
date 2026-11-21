import MhTax.Basic

namespace MhTax
open TaxKernel

theorem schedOld_mono : Monotone' schedOld.ticks := Schedule.ticks_mono_of_progressive _ schedOld_progressive
theorem sched2024_mono : Monotone' sched2024.ticks := Schedule.ticks_mono_of_progressive _ sched2024_progressive
theorem sched2024_convex : Convex sched2024.ticks := Schedule.ticks_convex _ sched2024_progressive
theorem split_ok (a b : Int) : splitting sched2024.ticks a b ≤ separate sched2024.ticks a b :=
  splitting_le_separate _ sched2024_convex sched2024_mono a b

end MhTax
