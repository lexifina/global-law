import PgTax.Basic

namespace PgTax
open TaxKernel

theorem table1_mono : Monotone' table1.ticks := Schedule.ticks_mono_of_progressive _ table1_progressive
theorem table1_convex : Convex table1.ticks := Schedule.ticks_convex _ table1_progressive
theorem split_ok (a b : Int) : splitting table1.ticks a b ≤ separate table1.ticks a b :=
  splitting_le_separate _ table1_convex table1_mono a b

end PgTax
