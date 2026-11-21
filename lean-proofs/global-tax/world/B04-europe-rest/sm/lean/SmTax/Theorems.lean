import SmTax.Basic

/-! # San Marino: tariff theorems and the C1 c. 3 taper -/

namespace SmTax
open TaxKernel

theorem tariff_progressive : tariff.progressive = true := by decide
theorem tariff_mono : Monotone' tariff.ticks := Schedule.ticks_mono_of_progressive _ tariff_progressive
theorem tariff_convex : Convex tariff.ticks := Schedule.ticks_convex _ tariff_progressive
theorem individual_ok (a b : Int) : splitting tariff.ticks a b ≤ separate tariff.ticks a b :=
  splitting_le_separate _ tariff_convex tariff_mono a b

/-- The deduction is whole up to 9 000 € of income, gone at 40 000 €, half at 24 500 €. -/
theorem c3_points : (c3Deduction 900000, c3Deduction 4000000, c3Deduction 2450000) = (900000, 0, 450000) := by decide

/-- F1: inside the taper every euro of income removes 9 000/31 000 = 0,29 € of deduction, so the marginal rate is the
band rate × 1,29: on 1 000 € more income from 30 000 to 31 000 € (17 %/21 % bands) the tax rises by more than 210 €
(the 21 % band rate alone). -/
theorem taper_marginal_above_band :
    divR .halfUp (tariff.ticks (3100000 - c3Deduction 3100000)) BP - divR .halfUp (tariff.ticks (3000000 - c3Deduction 3000000)) BP
      > 21000 := by decide

end SmTax
