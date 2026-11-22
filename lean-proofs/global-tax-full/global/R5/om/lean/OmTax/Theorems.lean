import OmTax.Basic

/-! # Oman: statements about the model (no `sorry`) -/

namespace OmTax
open TaxKernel

theorem incomeTax_zero (c : Canon) : (out c).incomeTax = 0 := rfl

theorem oldAge_above_ceiling {x : Int} (h : 36000 ≤ x) : oldAge.ticks x = 750 * 36000 := by
  have := Contribution.ticks_above_ceiling oldAge (by decide) h
    (by simp [oldAge, Contribution.flatCapped, ceiling]; omega)
  rw [this]; decide

/-- Above the 3,000 a month ceiling only the uncapped 0.5 % job-security share still rises with pay. -/
theorem marginal_above_ceiling :
    (oldAge.amount 50000 + jobSecurity.amount 50000) - (oldAge.amount 40000 + jobSecurity.amount 40000) = 50 := by
  decide

#guard oldAge.amount 12000 = 900
#guard jobSecurity.amount 12000 = 60

end OmTax
