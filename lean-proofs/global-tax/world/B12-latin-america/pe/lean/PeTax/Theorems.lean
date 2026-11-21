import PeTax.Basic

namespace PeTax
open TaxKernel

theorem art53_progressive : art53.progressive = true := by decide
theorem art53_mono : Monotone' art53.ticks := Schedule.ticks_mono_of_progressive _ art53_progressive
theorem art53_convex : Convex art53.ticks := Schedule.ticks_convex _ art53_progressive
theorem art53_no_jump {x y : Int} (h : x ≤ y) : art53.ticks y - art53.ticks x ≤ art53.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ art53_progressive h).2
/-- Individual taxation never costs a couple more than pooling would (art. 53 convex). -/
theorem individual_ok (a b : Int) : splitting art53.ticks a b ≤ separate art53.ticks a b :=
  splitting_le_separate _ art53_convex art53_mono a b
/-- The art. 53 thresholds in soles at UIT 5 350. -/
theorem art53_thresholds : art53.bands.map (·.lo) = [0, 26750, 107000, 187250, 240750] := by decide

end PeTax
