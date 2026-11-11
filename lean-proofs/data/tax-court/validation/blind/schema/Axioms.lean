import LegalProofs.USTax.TaxCourt.Theorems

/-! Axioms used by the main theorems: each uses only `propext`, `Classical.choice` and `Quot.sound`, or none. -/

open Legal.USTax.TaxCourt Legal.USTax.TaxCourt.Theorems

#print axioms rateSched_ok
#print axioms eic_max_consistent
#print axioms eic_completed_consistent
#print axioms params_years
#print axioms schedule_marginal
#print axioms schedule_mono
#print axioms eicTable_bounds
#print axioms eicTabY_rounded
#print axioms eic_childless_under25
#print axioms tieBreak_claims
#print axioms tieBreak_parent
#print axioms tieBreak_no_parent
#print axioms determineStatus_allowed
#print axioms married_separate_only
#print axioms substantial_iff
#print axioms substantial_iff_5pct
#print axioms not_substantial_le_5000
#print axioms substantial_mono
#print axioms accuracyPenalty_le
#print axioms lateFiling_le
#print axioms earlyDistTax_no_exception
#print axioms earlyDistTax_bounds
#print axioms seTaxY_eq_2025
#print axioms seTaxY_mono
#print axioms no_deficiency_on_same_facts
