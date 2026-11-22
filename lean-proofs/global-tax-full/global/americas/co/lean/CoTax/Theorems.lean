import CoTax.Basic

/-! # Colombia: the art. 241 table checked against its bands; kernel theorems -/

namespace CoTax
open TaxKernel

theorem bands_progressive : art241Bands.progressive = true := by decide
theorem bands_convex : Convex art241Bands.ticks := Schedule.ticks_convex _ bands_progressive
theorem bands_mono : Monotone' art241Bands.ticks := Schedule.ticks_mono_of_progressive _ bands_progressive

/-- **Finding CO-F1.** The fixed amounts printed in ET art. 241 are the band sums rounded to whole UVT (115,9 → 116;
1.508,1 + 788 → 2.296; 10.352,1 → 10.352), so the literal table jumps at three thresholds (ticks = UVT × bp):
+0,1 UVT at 1.700 UVT, −0,1 UVT at 8.670 UVT and −0,1 UVT at 31.000 UVT. -/
theorem art241_jumps :
    cumJumps art241 = [(0, 0), (1090, 0), (1700, 1000), (4100, 0), (8670, -1000), (18970, 0), (31000, -1000)] := by
  decide

/-- At 8.670 UVT the literal table gives less tax than one unit below it: the tax falls as the base rises. -/
theorem art241_falls_at_8670 : cumTicks art241 8670 < cumTicks art241 8669 + 3300 := by decide

/-- Everywhere else the table is within 0,1 UVT of its bands. -/
def probes : List Int := [0, 1090, 1500, 1700, 2000, 4100, 6000, 8670, 10000, 18970, 25000, 31000, 40000]
theorem art241_close : cumAgrees art241 art241Bands probes 1000 = true := by decide

/-- Individual assessment never costs more than pooling (bands convex). -/
theorem individual_ok (a b : Int) : splitting art241Bands.ticks a b ≤ separate art241Bands.ticks a b :=
  splitting_le_separate _ bands_convex bands_mono a b

end CoTax
