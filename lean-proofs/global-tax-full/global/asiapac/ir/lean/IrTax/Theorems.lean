import IrTax.Basic

namespace IrTax
open TaxKernel

theorem salary_mono : Monotone' salarySched.ticks := Schedule.ticks_mono_of_progressive _ salarySched_progressive
theorem salary_convex : Convex salarySched.ticks := Schedule.ticks_convex _ salarySched_progressive
theorem salary_no_jump {x y : Int} (h : x ≤ y) :
    salarySched.ticks y - salarySched.ticks x ≤ salarySched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ salarySched_progressive h).2
theorem split_ok (a b : Int) : splitting salarySched.ticks a b ≤ separate salarySched.ticks a b :=
  splitting_le_separate _ salary_convex salary_mono a b

end IrTax
