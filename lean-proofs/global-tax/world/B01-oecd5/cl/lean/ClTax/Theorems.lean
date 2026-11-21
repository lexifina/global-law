import ClTax.Basic

/-! # Chile: kernel theorems instantiated and parameter checks -/

namespace ClTax
open TaxKernel

/-- The art. 43 / 52 scale is progressive at every 2025 unit value. -/
theorem scale_progressive_dec : (scale utaDec).progressive = true := by decide
theorem scale_progressive_all : (utm.all fun u => (scale u).progressive) = true := by decide
theorem gc_convex : Convex (scale utaDec).ticks := Schedule.ticks_convex _ scale_progressive_dec
theorem gc_mono : Monotone' (scale utaDec).ticks := Schedule.ticks_mono_of_progressive _ scale_progressive_dec
/-- Individual assessment never costs more than pooling both incomes (the scale is convex). -/
theorem individual_ok (a b : Int) : splitting (scale utaDec).ticks a b ≤ separate (scale utaDec).ticks a b :=
  splitting_le_separate _ gc_convex gc_mono a b
/-- The overlay with the impuesto único credit: the household pays exactly the larger of the two (kernel). -/
theorem overlay_max (f : Int → Int) (cs : List Cedula) :
    cedularTotal cs + overlayTax f cs true = max (cedularTotal cs) (f (cedularBase cs)) :=
  overlay_credit_total f cs

/-- The 2025 topes reproduce the statutory adjustment of DL 3.500 art. 16 / Ley 19.728 art. 6 from the 2024 values
(Res. SP 224/225 de 2024: 84,3 and 126,6 UF) with the INE index variation of 4,1 % given in the resolutions, rounded
to a tenth of a UF. -/
theorem tope_check : divR .halfUp (843 * 1041) 1000 = topeUFTenths ∧ divR .halfUp (1266 * 1041) 1000 = topeAFCUFTenths := by
  decide
/-- The February re-set with the definitive 4,2 % (Res. 253/254 de 2025): the AFP tope stays 87,8 UF, the cesantía
tope moves to 131,9 UF. -/
theorem tope_check_feb : divR .halfUp (843 * 1042) 1000 = topeUFTenths ∧ divR .halfUp (1266 * 1042) 1000 = topeAFCUFTenthsFeb := by
  decide

/-- UTA = 12 × UTM of December (SII). -/
theorem uta_check : utaDec = 834504 := by decide

/-- The top rate is 40 % (art. 43 N° 1, art. 52). -/
theorem top_rate : (scale utaDec).topRate = 4000 := by decide

end ClTax
