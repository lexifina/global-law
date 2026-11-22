import BnTax.Basic

/-! # Brunei: statements about the model (no `sorry`) -/

namespace BnTax
open TaxKernel

theorem incomeTax_zero (c : Canon) : (out c).incomeTax = 0 := rfl

/-- s. 10(2): no ceiling: a salary ten times higher pays ten times more. -/
theorem spk_no_ceiling : spk.amount 2400000 = 10 * spk.amount 240000 := by decide
/-- Ten more dollars of wages cost 85 cents: an exact 8.5 % at every level (no ceiling, no floor). -/
theorem spk_marginal : spk.ticks 1000010 - spk.ticks 1000000 = 850 * 10 := by decide

#guard spk.amount 24000 = 2040
#guard spk.amount 200 = 17

end BnTax
