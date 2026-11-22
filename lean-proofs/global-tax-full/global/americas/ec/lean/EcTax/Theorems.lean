import EcTax.Basic

namespace EcTax
open TaxKernel

theorem bands_progressive : bands2025.progressive = true := by decide
theorem bands_mono : Monotone' bands2025.ticks := Schedule.ticks_mono_of_progressive _ bands_progressive
theorem bands_convex : Convex bands2025.ticks := Schedule.ticks_convex _ bands_progressive
theorem individual_ok (a b : Int) : splitting bands2025.ticks a b ≤ separate bands2025.ticks a b :=
  splitting_le_separate _ bands_convex bands_mono a b

/-- Each printed "impuesto fraccion basica" is the band sum rounded to the dollar; the jump of the literal table at
each threshold (ticks = USD x bp). -/
theorem tabla_jumps :
    cumJumps tabla2025 = [(0, 0), (12081, 0), (15387, -3000), (19978, -1000), (26422, 7200), (34770, -2000),
      (46089, 2000), (61359, -5000), (81817, 6000), (108810, -5500)] := by decide

/-- **EC-F1 (rounding, not an error).** The literal table is within 0,72 USD of its bands at every threshold; the largest
step is +0,72 USD at 26.422 (printed 1.398 vs 1.397,28) and the table falls by 0,55 USD at 108.810. -/
theorem tabla_close :
    cumAgrees tabla2025 bands2025 [0, 12081, 15387, 19978, 26422, 34770, 46089, 61359, 81817, 108810, 150000] 7200 = true := by
  decide

end EcTax
