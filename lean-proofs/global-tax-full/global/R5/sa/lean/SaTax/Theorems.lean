import SaTax.Basic

/-! # Saudi Arabia: statements about the model (no `sorry`) -/

namespace SaTax
open TaxKernel

theorem incomeTax_zero (c : Canon) : (out c).incomeTax = 0 := rfl

theorem annuities_above_ceiling {x : Int} (h : 540000 ≤ x) : annuities.ticks x = 900 * 540000 := by
  have := Contribution.ticks_above_ceiling annuities (by decide) h
    (by simp [annuities, Contribution.flatCapped, ceiling]; omega)
  rw [this]; decide

#guard annuities.amount 120000 = 10800
#guard annuities.amount 600000 = 48600

end SaTax
