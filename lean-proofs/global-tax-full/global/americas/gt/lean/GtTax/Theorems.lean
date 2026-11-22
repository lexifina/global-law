import GtTax.Basic

namespace GtTax
open TaxKernel

theorem bands_progressive : art73Bands.progressive = true := by decide
theorem bands_mono : Monotone' art73Bands.ticks := Schedule.ticks_mono_of_progressive _ bands_progressive
theorem bands_convex : Convex art73Bands.ticks := Schedule.ticks_convex _ bands_progressive
theorem individual_ok (a b : Int) : splitting art73Bands.ticks a b ≤ separate art73Bands.ticks a b :=
  splitting_le_separate _ bands_convex bands_mono a b
/-- The printed fixed amount Q 15.000 is exactly 5 % of Q 300.000: the art. 73 column has no jump. -/
theorem art73_no_jump : cumJumps art73 = [(0, 0), (300000, 0)] := by decide
theorem art73_is_bands : cumAgrees art73 art73Bands [0, 1, 299999, 300000, 300001, 1000000] = true := by decide

end GtTax
