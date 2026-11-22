import BhTax.Basic

/-! # Bahrain: statements about the model (no `sorry`) -/

namespace BhTax
open TaxKernel

theorem incomeTax_zero (c : Canon) : (out c).incomeTax = 0 := rfl

/-- Above 4,000 dinars a month the old-age contribution is constant: 7 % × 48,000 (kernel `ticks_above_ceiling`). -/
theorem oldAge_above_ceiling {x : Int} (h : 48000 ≤ x) : oldAge.ticks x = 700 * 48000 := by
  have := Contribution.ticks_above_ceiling oldAge (by decide) h
    (by simp [oldAge, Contribution.flatCapped, ceiling]; omega)
  rw [this]; decide

theorem combined_at_ceiling : oldAge.amount 48000 + unemployment.amount 48000 = 3840 := by decide

#guard oldAge.amount 12000 = 840
#guard unemployment.amount 100000 = 480

end BhTax
