import SyTax.Basic

namespace SyTax
open TaxKernel

theorem wage_mono : Monotone' wageSched.ticks := Schedule.ticks_mono_of_progressive _ wageSched_progressive
theorem wage_convex : Convex wageSched.ticks := Schedule.ticks_convex _ wageSched_progressive
theorem wage_no_jump {x y : Int} (h : x ≤ y) : wageSched.ticks y - wageSched.ticks x ≤ wageSched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ wageSched_progressive h).2
/-- Art. 69: below the exempt minimum no tax at all (kernel `exemptTaxOf_below`). -/
theorem below_exempt {e x : Int} (h : x ≤ e) : exemptTaxOf wageSched.ticks e x = 0 := exemptTaxOf_below _ h
theorem biz_mono : Monotone' bizSched.ticks := Schedule.ticks_mono_of_progressive _ bizSched_progressive

end SyTax
