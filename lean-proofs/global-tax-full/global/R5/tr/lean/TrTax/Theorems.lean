import TrTax.Basic

/-! # Türkiye: kernel theorems instantiated, and the printed tariff checked against its bands -/

namespace TrTax
open TaxKernel

theorem tariff_progressive : tariffTL.progressive = true := by decide
theorem wageTariff_progressive : wageTariffTL.progressive = true := by decide
theorem tariffK_progressive : tariff.progressive = true := by decide
theorem wageTariffK_progressive : wageTariff.progressive = true := by decide

theorem wageT_mono : Monotone' wageTariff.ticks := Schedule.ticks_mono_of_progressive _ wageTariffK_progressive
theorem wage_convex : Convex wageTariff.ticks := Schedule.ticks_convex _ wageTariffK_progressive
theorem gen_convex : Convex tariff.ticks := Schedule.ticks_convex _ tariffK_progressive

/-- The printed column "tax at the lower limit" of Tebliğ 41166 m. 3 (3) equals the band sums exactly, for both
tariffs (no rounding in the printed column, unlike CO ET art. 241). Checked at every threshold and between. -/
def probes : List Int := [0, 1, 157999, 158000, 158001, 329999, 330000, 330001, 799999, 800000, 800001,
  1199999, 1200000, 1200001, 4299999, 4300000, 4300001, 10000000]
theorem printed_eq_bands : cumAgrees printedTL tariffTL probes = true := by decide
theorem printedWage_eq_bands : cumAgrees printedWageTL wageTariffTL probes = true := by decide
theorem printed_no_jumps : (cumJumps printedTL).all (fun j => j.2 == 0) = true := by decide
theorem printedWage_no_jumps : (cumJumps printedWageTL).all (fun j => j.2 == 0) = true := by decide

/-- The wage tariff never taxes more than the general tariff (its 27 % band is longer). -/
theorem wage_le_general : (probes.all fun x => wageTariffTL.ticks x ≤ tariffTL.ticks x) = true := by decide

/-- Splitting a wage base between two persons never costs more than one person earning both (convex tariff). -/
theorem individual_ok (a b : Int) : splitting wageTariff.ticks a b ≤ separate wageTariff.ticks a b :=
  splitting_le_separate _ wage_convex wageT_mono a b

/-- The minimum-wage exemption written as an exempt tax (kernel `exemptTaxOf`): never more than the tax. -/
theorem wage_nonneg (y : Int) : 0 ≤ wageTariff.ticks y :=
  Schedule.ticks_nonneg _ (by unfold Schedule.RatesNonneg; decide) (by unfold Schedule.LosNonneg; decide) y
theorem exemption_le (e x : Int) : exemptTaxOf wageTariff.ticks e x ≤ wageTariff.ticks x :=
  exemptTaxOf_le _ wage_nonneg e x

/-- Cumulative withholding telescopes: the year's instalments sum to the tariff on the year's base. -/
theorem cumulative_sum (p : Int) (cs : List Int) :
    listSum (cumWithholdings wageT p cs) = wageT (lastOr p cs) - wageT p :=
  cumWithholdings_sum wageT p cs

end TrTax
