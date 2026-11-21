import BaTax.Basic

/-! # Federation of BiH: kernel theorems instantiated; the family deductions checked -/

namespace BaTax
open TaxKernel

theorem sched_progressive : schedule.progressive = true := by decide
theorem sched_mono : Monotone' schedule.ticks := Schedule.ticks_mono_of_progressive _ sched_progressive
theorem sched_convex : Convex schedule.ticks := Schedule.ticks_convex _ sched_progressive
/-- A flat 10 % tax: splitting income between spouses changes nothing except through the deductions. -/
theorem flat_additive_probe : schedule.ticks 30000 = schedule.ticks 10000 + schedule.ticks 20000 := by decide
theorem individual_ok (a b : Int) : splitting schedule.ticks a b ≤ separate schedule.ticks a b :=
  splitting_le_separate _ sched_convex sched_mono a b

/-- Član 24 (2): one child adds 1 800 KM, two add 4 320, three add 7 560, four add 10 800. -/
theorem child_amounts : (childDed 1, childDed 2, childDed 3, childDed 4) = (1800, 4320, 7560, 10800) := by decide

/-- F1: the dependent-spouse deduction (1 800 KM, worth 180 KM of tax) is lost when the spouse's own income passes
3 600 KM: one KM more of the spouse's net income costs the household 180 KM. -/
theorem spouse_value : taxOf (20000 - 3600) - taxOf (20000 - 3600 - 1800) = 180 := by decide

end BaTax
