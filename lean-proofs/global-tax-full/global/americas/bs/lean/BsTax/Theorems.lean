import BsTax.Basic

/-! # The Bahamas: statements about the model (no `sorry`) -/

namespace BsTax
open TaxKernel

theorem incomeTax_zero (c : Canon) : (out c).incomeTax = 0 := rfl

/-- The 2024 regulations split the 1.5-point increase equally: the employee's rate is 4.65 %. -/
theorem rate_2025 : rate = 390 + 150 / 2 := by decide

#guard ni.amount 20000 = 930
#guard ni.amount 31200 = 1450

end BsTax
