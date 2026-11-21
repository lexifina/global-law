import BzTax.Basic

namespace BzTax
open TaxKernel

/-- The 25 % rate of s. 6(3) as a one-band schedule (the kernel's progressive-schedule theorems apply to it). -/
def sched : Schedule := Schedule.ofList [(0, 2500)]
theorem sched_progressive : sched.progressive = true := by decide
theorem sched_mono : Monotone' sched.ticks := Schedule.ticks_mono_of_progressive _ sched_progressive
theorem sched_convex : Convex sched.ticks := Schedule.ticks_convex _ sched_progressive

/-- The phase-in band 29,000-32,000 has a 100 % marginal rate (in cents: 100 more cents of tax per dollar). -/
theorem phase_in_100 : taxCents 31001 - taxCents 31000 = 100 := by decide

end BzTax
