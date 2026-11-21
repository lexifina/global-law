import AeTax.Basic

/-! # UAE: statements about the model (no `sorry`) -/

namespace AeTax
open TaxKernel

/-- No household pays personal income tax (FDL 47/2022 art. 11-12; FTA: wages are not Business). -/
theorem incomeTax_zero (c : Canon) : (out c).incomeTax = 0 := rfl

/-- FDL 57/2023 art. 5(2): the 70,000 a month ceiling caps the employee pension at 11 % × 840,000 = 92,400 a year. -/
theorem pension2023_at_cap : pension2023 840000 = 92400 := by decide
theorem pension2023_above_cap : pension2023 2000000 = 92400 := by decide
/-- The Dh3,000 minimum contribution salary: a part-time salary of 12,000 a year pays as if it were 36,000. -/
theorem pension2023_floor : pension2023 12000 = 3960 := by decide
/-- FL 7/1999: 5 % up to Dh50,000 a month. -/
theorem pension1999_at_cap : pension1999 600000 = 30000 := by decide

/-- The ILOE premium doubles when the basic salary passes 16,000 a month: one more dirham costs 60 a year (a notch). -/
theorem iloe_notch : iloe (iloeThreshold + 1) - iloe iloeThreshold = 60 := by decide

#guard pension2023 120000 = 13200
#guard iloe 120000 = 60

end AeTax
