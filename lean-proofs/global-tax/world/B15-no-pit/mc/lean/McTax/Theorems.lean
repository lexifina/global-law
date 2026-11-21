import McTax.Basic

/-! # Monaco: statements about the model (no `sorry`) -/

namespace McTax
open TaxKernel

theorem incomeTax_zero (c : Canon) : (out c).incomeTax = 0 := rfl

/-- The employee's CMRC rates are 40 % of the published totals. -/
theorem cmrcA_split : cmrcA * 100 = 40 * (78700 + 21500) := by decide
theorem cmrcB_split : cmrcB * 100 = 40 * (215900 + 27000) := by decide

/-- Below every ceiling C.A.R. is 6,85 % and unemployment insurance 2,40 % of the wage. -/
theorem car_60000 : car 60000 = 4110 := by decide
theorem unemp_60000 : unemp 60000 = 1440 := by decide
/-- CMRC at 60,000 € a year: TA on the 9/3-month weighted ceilings, TB on the rest. -/
theorem cmrc_60000 : cmrc 60000 = 3121 := by decide

/-- Above 8 × TA and the unemployment ceiling (188,400 € a year) nothing more is due. -/
theorem flat_above : car 400000 + unemp 400000 + cmrc 400000 = car 500000 + unemp 500000 + cmrc 500000 := by decide

end McTax
