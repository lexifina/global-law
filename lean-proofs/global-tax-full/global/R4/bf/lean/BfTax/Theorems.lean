import BfTax.Basic

/-! # Burkina Faso: kernel theorems instantiated; the family reduction's structure proved -/

namespace BfTax
open TaxKernel

theorem monthly_progressive : monthly.progressive = true := by decide
theorem monthly_mono : Monotone' monthly.ticks := Schedule.ticks_mono_of_progressive _ monthly_progressive
theorem monthly_convex : Convex monthly.ticks := Schedule.ticks_convex _ monthly_progressive
theorem irf_progressive : irfMonthly.progressive = true := by decide

/-- Art. 112: 250 000 F of monthly net pay bears 2 420 + 4 170 + 6 280 + 9 200 + 17 360 = 39 430 F. -/
theorem month_250k : divR .down (monthly.ticks 250000) BP = 39430 := by decide

/-- Art. 111: below a gross of about 43 165 F a month (net 30 000 after 5,5 % CNSS and 25 %) no IUTS is due. -/
theorem zero_band : iutsMonth abatOrdinary 0 43000 = 0 ∧ iutsMonth abatOrdinary 0 43200 > 0 := by decide

/-- F1: the family reduction is a share of the tax (8-14 %), so it is worth most to the highest earners: four charges
save 14 % of the tax, 718 F a month at a 100 000 F wage and 45 420 F a month at 2 000 000 F. -/
theorem charges_regressive :
    iutsMonth abatOrdinary 0 100000 - iutsMonth abatOrdinary 4 100000 = 718 ∧
    iutsMonth abatOrdinary 0 2000000 - iutsMonth abatOrdinary 4 2000000 = 45420 := by decide

end BfTax
