import NiTax.Basic

namespace NiTax
open TaxKernel

theorem bands_progressive : art23Bands.progressive = true := by decide
theorem bands_mono : Monotone' art23Bands.ticks := Schedule.ticks_mono_of_progressive _ bands_progressive
theorem bands_convex : Convex art23Bands.ticks := Schedule.ticks_convex _ bands_progressive
theorem individual_ok (a b : Int) : splitting art23Bands.ticks a b ≤ separate art23Bands.ticks a b :=
  splitting_le_separate _ bands_convex bands_mono a b
/-- The printed "impuesto base" column equals the band sums exactly: no jump at any threshold. -/
theorem art23_no_jump : (cumJumps art23).all (fun j => j.2 == 0) = true := by decide
theorem art23_is_bands : cumAgrees art23 art23Bands [0, 100000, 150000, 200000, 350000, 500000, 900000] = true := by decide

end NiTax
