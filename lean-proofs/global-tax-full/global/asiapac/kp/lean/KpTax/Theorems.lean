import KpTax.Basic

namespace KpTax
open TaxKernel

/-- Constitution art. 25: no household pays income tax. -/
theorem no_income_tax (c : Canon) : (out c).incomeTax = 0 := rfl

end KpTax
