import IlTax.Basic

/-! # Israel: kernel theorems instantiated -/

namespace IlTax
open TaxKernel

theorem exertion_progressive : exertionScale.progressive = true := by decide
theorem other_progressive : otherScale.progressive = true := by decide
theorem exertion_convex : Convex exertionScale.ticks := Schedule.ticks_convex _ exertion_progressive
theorem exertion_mono : Monotone' exertionScale.ticks := Schedule.ticks_mono_of_progressive _ exertion_progressive
/-- Separate computation for spouses never costs more than one pooled computation (convex scale). -/
theorem separate_ok (a b : Int) : splitting exertionScale.ticks a b ≤ separate exertionScale.ticks a b :=
  splitting_le_separate _ exertion_convex exertion_mono a b
/-- Above 269.280 NIS the exertion and other scales coincide (s. 121(א) and (ב)). -/
theorem scales_meet : exertionScale.rate 300000 = otherScale.rate 300000 ∧ exertionScale.rate 600000 = otherScale.rate 600000 := by
  decide
/-- The resident's 2¼ points are worth 6.534 NIS a year: income tax starts at the income where the 10 % band's tax
reaches that (65.340 NIS, all in the 10 % band). -/
theorem zero_tax_point : exertionScale.ticks 65340 = quartersValue residentQuarters * BP := by decide
/-- Unused credit points are lost (kernel `applyCredits_waste`): the credits are non-refundable. -/
theorem credits_waste (t v : Int) (h : t < v) (h0 : 0 ≤ t) : applyCredits t [v] [] = 0 := by
  unfold applyCredits; simp [sumInts, pos]; omega

end IlTax
