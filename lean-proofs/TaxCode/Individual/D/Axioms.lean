import TaxCode.Individual.D.Ordering

/-! Axiom check for every theorem in group D (expected: only propext, Classical.choice, Quot.sound, or none). -/

namespace TaxCode.Individual.D

#print axioms pos_nonneg
#print axioms ctc_bounds
#print axioms ctcReduction_mono
#print axioms ctc_antitone
#print axioms ctc_step_le_50
#print axioms ctc_notch_at_threshold
#print axioms actc_le_cap
#print axioms ctc_split_le
#print axioms actc_le_child_credit
#print axioms form_ge_statute
#print axioms form_exceeds_statute
#print axioms taxpayer_ssn_cost
#print axioms cdcc2025_pct_bounds
#print axioms cdcc2025_pct_antitone
#print axioms cdcc2026_pct_bounds
#print axioms cdcc2026_pct_antitone
#print axioms cdcc2026_ge_2025
#print axioms cdcc2025_bounds
#print axioms cdcc2025_notch
#print axioms cdcc2025_step_le_60
#print axioms cdcc2026_notch
#print axioms maxCredit_is_rounded
#print axioms completed_phaseout_consistent
#print axioms eicScaled_bounds
#print axioms eicScaled_le_max
#print axioms eicScaled_antitone_agi
#print axioms eicScaled_step
#print axioms worksheet_rule_exact
#print axioms table_vs_statute_0
#print axioms table_vs_statute_1
#print axioms table_vs_statute_2
#print axioms table_vs_statute_3
#print axioms table_vs_statute_tight
#print axioms table_notch
#print axioms table_step_le_12
#print axioms zero_child_tail
#print axioms investment_income_cliff
#print axioms table_le_max
#print axioms aotcPerStudent_bounds
#print axioms eduPhase_bounds
#print axioms eduPhase_step
#print axioms form_vs_statute_aotc
#print axioms form_vs_statute_example
#print axioms kiddie_cliff
#print axioms useAll_eq
#print axioms nonrefundable_eq_min
#print axioms nonrefundable_same_either_order
#print axioms forms_order_dominates
#print axioms forms_order_strictly_better
#print axioms actc_le_unused
#print axioms actc_statute_eq_form_no_others
#print axioms actc_full
#print axioms forms_order_matches_statute
#print axioms rate2025_step
#print axioms contrib2025_step
#print axioms ptc2025_continuous
#print axioms roundDollar_step
#print axioms ptc2025_step
#print axioms ptc2025_no_400_cliff
#print axioms ptc2025_cliff_at_100
#print axioms form_notch_2025
#print axioms form_vs_statute_2025
#print axioms repayment_cliff_2025
#print axioms repayment_le
#print axioms ptc2026_cliff_400
#print axioms ptc2026_zero_above_400
#print axioms ptc2026_at_400
#print axioms ptc2025_same_point
#print axioms ptc2026_jump_133
#print axioms saverPercent_antitone
#print axioms saverPerson_bounds
#print axioms saverPerson_antitone
#print axioms saver_cliffs
#print axioms saverPerson_step_le_600

end TaxCode.Individual.D
