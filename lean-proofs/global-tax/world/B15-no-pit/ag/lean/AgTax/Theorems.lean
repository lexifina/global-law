import AgTax.Basic

/-! # Antigua and Barbuda: statements about the model (no `sorry`) -/

namespace AgTax
open TaxKernel

theorem incomeTax_zero (c : Canon) : (out c).incomeTax = 0 := rfl

theorem ss_above_ceiling {x : Int} (h : 78000 ≤ x) : ssPrivate.ticks x = 700 * 78000 := by
  have := Contribution.ticks_above_ceiling ssPrivate (by decide) h
    (by simp [ssPrivate, Contribution.flatCapped, ceiling]; omega)
  rw [this]; decide

/-- Below the ceiling an employee under 60 pays 10.5 % (7 % social security + 3.5 % medical benefits). -/
theorem combined_below_ceiling : ssPrivate.amount 60000 + mbUnder60.amount 60000 = 6300 := by decide

#guard ssPrivate.amount 100000 = 5460
#guard mbUnder60.amount 100000 = 3500

end AgTax
