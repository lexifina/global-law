import XkTax.Basic

/-! # Kosovo: kernel theorems instantiated; the printed table checked against its bands -/

namespace XkTax
open TaxKernel

theorem sched_progressive : schedule.progressive = true := by decide
theorem sched_mono : Monotone' schedule.ticks := Schedule.ticks_mono_of_progressive _ sched_progressive
theorem sched_convex : Convex schedule.ticks := Schedule.ticks_convex _ sched_progressive
theorem individual_ok (a b : Int) : splitting schedule.ticks a b ≤ separate schedule.ticks a b :=
  splitting_le_separate _ sched_convex sched_mono a b

/-- The printed "192 €" at 5 400 is exactly 8 % of 2 400: the printed column equals the bands, no jump. -/
def probes : List Int := [0, 1, 2999, 3000, 3001, 5399, 5400, 5401, 10000, 100000]
theorem printed_eq_bands : cumAgrees printed schedule probes = true := by decide
theorem printed_no_jumps : (cumJumps printed).all (fun j => j.2 == 0) = true := by decide

/-- F2: the 2024 reform never raises the tax: on every probe the new table is at most the 2015 table, and the gain
is 81,60 € for every taxable income above 3 000 € (the 4 % band 960-3 000 removed). -/
theorem reform_never_worse : (probes.all fun x => schedule.ticks x ≤ schedule2015.ticks x) = true := by decide
theorem reform_gain_above_3000 : schedule2015.ticks 10000 - schedule.ticks 10000 = 816 * BP / 10 := by decide

end XkTax
