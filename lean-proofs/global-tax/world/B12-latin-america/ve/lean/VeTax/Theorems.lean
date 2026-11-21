import VeTax.Basic

namespace VeTax
open TaxKernel

theorem tarifa1_progressive : tarifa1.progressive = true := by decide
theorem tarifa1_mono : Monotone' tarifa1.ticks := Schedule.ticks_mono_of_progressive _ tarifa1_progressive
theorem tarifa1_convex : Convex tarifa1.ticks := Schedule.ticks_convex _ tarifa1_progressive
theorem individual_ok (a b : Int) : splitting tarifa1.ticks a b ≤ separate tarifa1.ticks a b :=
  splitting_le_separate _ tarifa1_convex tarifa1_mono a b
theorem tarifa1_no_jump {x y : Int} (h : x ≤ y) : tarifa1.ticks y - tarifa1.ticks x ≤ tarifa1.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ tarifa1_progressive h).2

end VeTax
