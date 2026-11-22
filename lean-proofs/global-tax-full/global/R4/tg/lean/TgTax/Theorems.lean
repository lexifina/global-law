import TgTax.Basic

namespace TgTax
open TaxKernel

theorem bareme_mono : Monotone' bareme.ticks := Schedule.ticks_mono_of_progressive _ bareme_progressive
theorem bareme_convex : Convex bareme.ticks := Schedule.ticks_convex _ bareme_progressive
theorem bareme_no_jump {x y : Int} (h : x ≤ y) : bareme.ticks y - bareme.ticks x ≤ bareme.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ bareme_progressive h).2
theorem split_ok (a b : Int) : splitting bareme.ticks a b ≤ separate bareme.ticks a b :=
  splitting_le_separate _ bareme_convex bareme_mono a b

end TgTax
