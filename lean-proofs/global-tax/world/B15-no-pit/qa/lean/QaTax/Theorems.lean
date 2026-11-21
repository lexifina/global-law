import QaTax.Basic

/-! # Qatar: statements about the model (no `sorry`) -/

namespace QaTax
open TaxKernel

theorem incomeTax_zero (c : Canon) : (out c).incomeTax = 0 := rfl

theorem pension_above_ceiling {x : Int} (h : 1200000 ≤ x) : pension.ticks x = 700 * 1200000 := by
  have := Contribution.ticks_above_ceiling pension (by decide) h
    (by simp [pension, Contribution.flatCapped, ceiling]; omega)
  rw [this]; decide

#guard pension.amount 240000 = 16800
#guard pension.amount 2000000 = 84000

end QaTax
