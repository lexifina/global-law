import PaTax.Basic

namespace PaTax
open TaxKernel

theorem bands_progressive : art700Bands.progressive = true := by decide
theorem bands_mono : Monotone' art700Bands.ticks := Schedule.ticks_mono_of_progressive _ bands_progressive
theorem bands_convex : Convex art700Bands.ticks := Schedule.ticks_convex _ bands_progressive
theorem individual_ok (a b : Int) : splitting art700Bands.ticks a b ≤ separate art700Bands.ticks a b :=
  splitting_le_separate _ bands_convex bands_mono a b
/-- The printed B/. 5.850 is exactly 15 % of B/. 39.000: no jump at B/. 50.000. -/
theorem art700_no_jump : (cumJumps art700).all (fun j => j.2 == 0) = true := by decide

end PaTax
