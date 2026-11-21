import VaTax.Basic

namespace VaTax
open TaxKernel

/-- No household pays income tax. -/
theorem no_income_tax (c : Canon) : (out c).incomeTax = 0 := rfl

end VaTax
