import GqTax.Basic

namespace GqTax
open TaxKernel

theorem baremo_mono : Monotone' baremo.ticks := Schedule.ticks_mono_of_progressive _ baremo_progressive
theorem baremo_convex : Convex baremo.ticks := Schedule.ticks_convex _ baremo_progressive
theorem baremo_no_jump {x y : Int} (h : x ≤ y) : baremo.ticks y - baremo.ticks x ≤ baremo.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ baremo_progressive h).2
theorem split_ok (a b : Int) : splitting baremo.ticks a b ≤ separate baremo.ticks a b :=
  splitting_le_separate _ baremo_convex baremo_mono a b

end GqTax
