import UyTax.Basic

namespace UyTax
open TaxKernel

theorem scaleA_progressive : scaleA.progressive = true := by decide
theorem scaleA_mono : Monotone' scaleA.ticks := Schedule.ticks_mono_of_progressive _ scaleA_progressive
theorem scaleA_convex : Convex scaleA.ticks := Schedule.ticks_convex _ scaleA_progressive
theorem individual_ok (a b : Int) : splitting scaleA.ticks a b ≤ separate scaleA.ticks a b :=
  splitting_le_separate _ scaleA_convex scaleA_mono a b
theorem scaleA_thresholds :
    scaleA.bands.map (·.lo) = [0, 552384, 789120, 1183680, 2367360, 3945600, 5918400, 9074880] := by decide

/-- **UY-F1 (statute-visible notch).** At 180 BPC of nominal income the art. 38 deduction rate falls from 14 % to 8 %
of all deductions: one more peso of wage costs more than 10 000 pesos of IRPF (single person, no children). -/
theorem art38_notch :
    (person (180 * bpc + 1) 0 0 10).irpf - (person (180 * bpc) 0 0 10).irpf > 10000 := by decide

/-- **UY-F2 (statute-visible notch).** FONASA moves from 3 % to 4,5 % of the whole wage above 2,5 BPC a month
(Ley 18.211 art. 61). -/
theorem fonasa_notch : fonasaRate 16441 false - fonasaRate 16440 false = 150 := by decide

end UyTax
