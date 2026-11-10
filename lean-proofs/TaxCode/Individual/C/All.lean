import TaxCode.Individual.C.AMT

/-! Group C (the tax itself): imports every file and prints the axioms of the main theorems. -/

open TaxCode.Individual.C

#print axioms sched_ok
#print axioms tcw_eq_schedule
#print axioms scheduleCents_marginal
#print axioms scheduleTax_step
#print axioms scheduleTax_mono
#print axioms no_marriage_penalty
#print axioms mfs_half_mfj
#print axioms table_within_6
#print axioms table_ge_minus5
#print axioms line16Tax_step
#print axioms worksheet_lines_eq
#print axioms regularTax_le
#print axioms capGainSum_excess_max
#print axioms more_dividends_more_tax
#print axioms regularTax_near
#print axioms line7_shortcut
#print axioms tmt_marginal
#print axioms tmt_le_schedule
#print axioms amt_unreachable
#print axioms hoh_salt_amt
#print axioms tmt_capgain_le
