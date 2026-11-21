import AdTax.Basic

/-! # Andorra: the effective tariff of the 10 % tax with the art. 46 bonus -/

namespace AdTax
open TaxKernel

/-- The effective tariff on the general base of a single person (no children): 0 % to 24 000, 5 % to 40 000, 10 %
above, as a kernel schedule. -/
def effective : Schedule := Schedule.ofList [(0, 0), (24000, 500), (40000, 1000)]
theorem effective_progressive : effective.progressive = true := by decide
theorem effective_mono : Monotone' effective.ticks := Schedule.ticks_mono_of_progressive _ effective_progressive
theorem effective_convex : Convex effective.ticks := Schedule.ticks_convex _ effective_progressive

/-- The literal rules (art. 35, 41, 46, 47) equal the effective tariff on probes across the bands. -/
def probes : List Int := [0, 1000, 23999, 24000, 24001, 30000, 39999, 40000, 40001, 60000, 200000]
theorem literal_eq_effective :
    (probes.all fun g => divR .halfUp (person g personalMin 0).tax 100 == divR .halfUp (effective.ticks g) BP) = true := by decide

/-- F1: with children the reductions lower the 10 % quota but the bonus keeps being computed on the base less 24 000 €
only (art. 46), so above 40 000 € each 750 € child reduction is worth 75 €, and between 24 000 and 40 000 € it is
worth 75 € minus nothing: the bonus does not shrink. -/
theorem child_worth_75 : (person 50000 personalMin 0).tax - (person 50000 (personalMin + 750) 0).tax = 7500 := by decide

end AdTax
