import CvTax.Basic

/-! # Cabo Verde: kernel theorems instantiated; splitting proved; the whole-income reading of art. 46.º measured -/

namespace CvTax
open TaxKernel

theorem sched_progressive : sched.progressive = true := by decide
theorem sched_mono : Monotone' sched.ticks := Schedule.ticks_mono_of_progressive _ sched_progressive
theorem sched_convex : Convex sched.ticks := Schedule.ticks_convex _ sched_progressive
/-- Art. 45.º 2. (quociente conjugal): splitting never costs a married couple more than separate assessment. -/
theorem split_ok (a b : Int) : splitting sched.ticks a b ≤ separate sched.ticks a b :=
  splitting_le_separate _ sched_convex sched_mono a b

/-- F1: a one-earner married couple with 3 000 000 CVE pays 157 300 CVE less than the same earner single
(a second mínimo de existência and splitting, which halves the income taxed at 27,5 %). -/
theorem marriage_bonus : irps 1 3000000 0 - irps 2 3000000 0 = 157300 := by decide

/-- F2 (statute ambiguity): if art. 46.º 1. is read as a rate on the whole income ("16,5% para rendimentos até
960.000$00; 23,1% para rendimentos superiores a 960.000$00"), one escudo above 960 000 of taxable income costs
63 360 CVE (6,6 % of 960 000). -/
def wholeRate (x : Int) : Int :=
  if x ≤ 960000 then x * 1650 / BP else if x ≤ 1800000 then x * 2310 / BP else x * 2750 / BP
theorem whole_rate_notch : wholeRate 960001 - wholeRate 960000 = 63360 := by decide

/-- The dependant credit is capped at five persons (25 000 CVE). -/
theorem dependant_cap : irps 1 2000000 5 = irps 1 2000000 8 := by decide

end CvTax
