import TaxCode.Indexing.Formula
import TaxCode.Indexing.CPI
import TaxCode.Indexing.RP24_40
import TaxCode.Indexing.RP25_32
import TaxCode.Indexing.RP23_34
import TaxCode.Indexing.RP22_38
import TaxCode.Indexing.Findings
import TaxCode.Indexing.SSA
import TaxCode.Indexing.PTC
import TaxCode.Indexing.Retirement
import TaxCode.Indexing.Withholding

open TaxCode.Indexing in
#print axioms incDown_eq_amtDown
#print axioms TaxCode.Indexing.Findings.sd_hoh_never_24150
#print axioms TaxCode.Indexing.Findings.levy_never_round_hundreds
#print axioms TaxCode.Indexing.Findings.ltc_never_round_tens
#print axioms TaxCode.Indexing.Findings.ltc_2026_splice
#print axioms TaxCode.Indexing.Findings.est_first_bracket_2026
#print axioms TaxCode.Indexing.Findings.base2024_revised_values_used
#print axioms TaxCode.Indexing.Findings.ccpiu_2026_incomplete
#print axioms TaxCode.Indexing.RP24_40.br_single_1_matches
#print axioms TaxCode.Indexing.RP25_32.sd_hoh_differs
#print axioms TaxCode.Indexing.RP25_32.taxcol_mfj
#print axioms TaxCode.Indexing.Findings.qualifying_relative_2023
#print axioms TaxCode.Indexing.SSA.cbb_2026
#print axioms TaxCode.Indexing.PTC.table_2026_consistent
#print axioms TaxCode.Indexing.Retirement.limits415_2026
#print axioms TaxCode.Indexing.Retirement.hsa_2026
#print axioms TaxCode.Indexing.Withholding.plain_w4_2026hoh
#print axioms TaxCode.Indexing.Withholding.checkbox_never_under_2026
#print axioms TaxCode.Indexing.Withholding.wb_2026_monthly_single_std_bound
#print axioms TaxCode.Indexing.Withholding.sd_gap_2025single
