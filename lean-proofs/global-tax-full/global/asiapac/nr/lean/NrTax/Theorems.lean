import NrTax.Basic

namespace NrTax
open TaxKernel

/-- The per-period scale is a flat 20 % above a band: a one-band schedule, monotone. -/
def periodSched (p : String) : Schedule := Schedule.ofList [(0, 0), (zeroBand p * 100, rate)]
theorem periodSched_monthly_progressive : (periodSched "monthly").progressive = true := by decide
theorem periodSched_mono : Monotone' (periodSched "monthly").ticks :=
  Schedule.ticks_mono_of_progressive _ periodSched_monthly_progressive

end NrTax
