import KnTax.Basic

/-! # Saint Kitts and Nevis: statements about the model (no `sorry`) -/

namespace KnTax
open TaxKernel

theorem incomeTax_zero (c : Canon) : (out c).incomeTax = 0 := rfl

/-- The HSDL notch (s. 3(2)(a)-(b)): one dollar above the $27,040 threshold the employee owes 3.5 % of the whole
wage, $946 a year (one-year reading under Act 14 of 2025). -/
theorem hsdl_notch : hsdlYear thresholdH2 (thresholdH2 + 1) - hsdlYear thresholdH2 thresholdH2 = 946 := by decide

/-- The notch costs more than the extra dollar: the marginal rate at the threshold is far above 100 %. -/
theorem hsdl_notch_metr : hsdlYear thresholdH2 (thresholdH2 + 1) > 1 + hsdlYear thresholdH2 thresholdH2 := by decide

/-- Above $96,000 the employee's marginal levy rate is 12 %. -/
theorem hsdl_top_marginal : hsdlTicks thresholdH2 100001 - hsdlTicks thresholdH2 100000 = 1200 := by decide

/-- 2025 weighting: a wage between the two thresholds pays half a year's levy. -/
theorem hsdl2025_between : hsdl2025 25000 = 437 := by decide

theorem ss_above_ceiling {x : Int} (h : 78000 ≤ x) : ss.ticks x = 500 * 78000 := by
  have := Contribution.ticks_above_ceiling ss (by decide) h
    (by simp [ss, Contribution.flatCapped, ssCeiling]; omega)
  rw [this]; decide

#guard hsdl2025 60000 = 2100
#guard hsdl2025 120000 = 2730 + 1800 + 2880

end KnTax
