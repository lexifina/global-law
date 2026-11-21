import TaxKernel
open TaxKernel
-- Every generic theorem depends only on Lean's standard axioms (propext, Quot.sound, Classical.choice at most): no sorry.
#print axioms Schedule.ticks_succ
#print axioms Schedule.ticks_convex
#print axioms Schedule.ticks_lipschitz_of_progressive
#print axioms Schedule.ticks_le_maxRate_mul
#print axioms Taper.taper_marginal
#print axioms Surcharge.withSurcharge_mono
#print axioms Surcharge.exempt_notch
#print axioms splitting_le_separate
#print axioms separate_le_joint
#print axioms Contribution.floor_notch
#print axioms toMultiple_halfUp_bounds
#print axioms Rule.ofTicks_mono
-- added in 1.2
#print axioms atAverageRate_self
#print axioms rateSplitting_two
#print axioms allocateOrdered_total_le
#print axioms attributeIncome_sum
#print axioms lowBand_le_zeroBand
#print axioms taxAfterLowBand_slice
#print axioms SteppedTaper.proportional_le_stepped
#print axioms SteppedTaper.stepped_notch
#print axioms Multiplier.amount_mono
#print axioms Taper.amount_antitoneM
#print axioms spillAllowanceCapped_le
