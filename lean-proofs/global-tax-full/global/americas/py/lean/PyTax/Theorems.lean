import PyTax.Basic

namespace PyTax
open TaxKernel

theorem art69_progressive : art69.progressive = true := by decide
theorem art69_mono : Monotone' art69.ticks := Schedule.ticks_mono_of_progressive _ art69_progressive
theorem art69_convex : Convex art69.ticks := Schedule.ticks_convex _ art69_progressive
theorem individual_ok (a b : Int) : splitting art69.ticks a b ≤ separate art69.ticks a b :=
  splitting_le_separate _ art69_convex art69_mono a b

/-- **PY-F1 (statute-visible notch).** Arts. 62 and 69: the IRP is due on the whole renta neta once gross income
passes G 80.000.000, nothing at or below it: one guarani of extra wage costs G 6.052.000 of tax (no expenses
claimed). -/
theorem threshold_notch : (person 80000001 0 0).tax - (person 80000000 0 0).tax = 6052000 := by decide

/-- Documented personal expenses can bring the renta neta of a wage to zero (art. 64 sets no cap): a wage of
G 500.000.000 with as much documented spending pays no IRP. -/
theorem expenses_cancel : (person 500000000 0 500000000).tax = 0 := by decide

end PyTax
