import HnTax.Basic

namespace HnTax
open TaxKernel

theorem tabla_progressive : tabla2025.progressive = true := by decide
theorem tabla_mono : Monotone' tabla2025.ticks := Schedule.ticks_mono_of_progressive _ tabla_progressive
theorem tabla_convex : Convex tabla2025.ticks := Schedule.ticks_convex _ tabla_progressive
theorem individual_ok (a b : Int) : splitting tabla2025.ticks a b ≤ separate tabla2025.ticks a b :=
  splitting_le_separate _ tabla_convex tabla_mono a b
theorem tabla_no_jump {x y : Int} (h : x ≤ y) : tabla2025.ticks y - tabla2025.ticks x ≤ tabla2025.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ tabla_progressive h).2

end HnTax
