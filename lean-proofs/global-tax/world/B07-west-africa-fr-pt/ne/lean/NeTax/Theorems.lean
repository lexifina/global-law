import NeTax.Basic

/-! # Niger: kernel theorems instantiated; the seventh-dependant cliff and the absence of a zero band proved -/

namespace NeTax
open TaxKernel

theorem monthly_progressive : monthly.progressive = true := by decide
theorem monthly_mono : Monotone' monthly.ticks := Schedule.ticks_mono_of_progressive _ monthly_progressive
theorem monthly_convex : Convex monthly.ticks := Schedule.ticks_convex _ monthly_progressive

/-- Art. 66: no zero band: the first 25 000 F of monthly net income already bear 1 %; a monthly pay of 2 000 F pays
ITS once rounded (base 1 000 F, tax 10 F). -/
theorem no_zero_band : itsMonth 0 2000 = 10 := by decide

/-- F1 (art. 65): the seventh dependant doubles the family abatement (15 % → 30 % of net income): at a monthly pay of
500 000 F the seventh charge alone saves 19 500 F a month, the sixth only 1 500 F. -/
theorem seventh_charge :
    itsMonth 6 500000 - itsMonth 7 500000 = 19500 ∧ itsMonth 5 500000 - itsMonth 6 500000 = 1500 := by decide

end NeTax
