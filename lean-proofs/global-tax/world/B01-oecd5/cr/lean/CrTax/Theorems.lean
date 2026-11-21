import CrTax.Basic

/-! # Costa Rica: kernel theorems instantiated -/

namespace CrTax
open TaxKernel

theorem salary_progressive : salaryScale.progressive = true := by decide
theorem profit_progressive : profitScale.progressive = true := by decide
theorem salary_convex : Convex salaryScale.ticks := Schedule.ticks_convex _ salary_progressive
theorem salary_mono : Monotone' salaryScale.ticks := Schedule.ticks_mono_of_progressive _ salary_progressive
/-- Splitting a salary between two employees never costs more than one salary (convex monthly scale). -/
theorem split_ok (a b : Int) : splitting salaryScale.ticks a b ≤ separate salaryScale.ticks a b :=
  splitting_le_separate _ salary_convex salary_mono a b
/-- Territorial base: foreign income never raises the base (kernel). -/
theorem territorial_le {d f : Int} (h : 0 ≤ f) (t : Bool) : sourceBase true d f ≤ sourceBase t d f :=
  sourceBase_territorial_le h t
/-- FINDINGS CR-F2: the salary scale exempts 922.000 a month (11.064.000 a year) while the profits scale of personas
físicas exempts 4.094.000 a year (Decreto 44772-H art. 1 and 4): 6.970.000 CRC a year of income is taxed for the
self-employed and not for employees. -/
theorem exempt_gap : 12 * 922000 - 4094000 = 6970000 := by decide

end CrTax
