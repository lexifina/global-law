import KwTax.Basic

/-! # Kuwait: statements about the model (no `sorry`) -/

namespace KwTax
open TaxKernel

theorem incomeTax_zero (c : Canon) : (out c).incomeTax = 0 := rfl

/-- Up to 1,500 a month a Kuwaiti employee pays 10.5 %: 5 + 2.5 + 2.5 + 0.5. -/
theorem rate_below_ceiling : person 18000 = 1890 := by decide
/-- Between 1,500 and 2,750 a month the marginal employee rate is 5.5 % (supplementary 5 % + unemployment 0.5 %). -/
theorem marginal_supplementary : person 19000 - person 18000 = 55 := by decide
/-- Above 2,750 a month (33,000 a year) nothing more is due. -/
theorem flat_above : person 33000 = person 100000 := by decide

#guard person 0 = 0
#guard person 33000 = 1890 + 750 + 75

end KwTax
