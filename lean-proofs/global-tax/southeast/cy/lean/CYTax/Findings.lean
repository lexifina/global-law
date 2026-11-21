import CYTax.Basic

/-! # Cyprus 2025: the findings of FINDINGS.md as statements about the model (cents; concrete households,
`native_decide`). Names match the `Lean:` lines in FINDINGS.md. -/

namespace CYTax
open TaxKernel

/-- 2026 tax on taxable income (Second Schedule 1(γ)), for the timing findings. -/
def scaleTax26 (ti : Int) : Int := divR .halfUp (scale2026.ticks ti) 10000

/-! ## F2: ITL art. 8(23Α): one cent of pay above €55.000 exempts half the pay -/
/-- At 55.000,00 € the newcomer pays 7.495,75 € income tax; at 55.000,01 € he pays 500,00 €. -/
theorem notch23A :
    (person {} {w := 5500000, ex := "23A"}).tax = 749575 ∧
    (person {} {w := 5500001, ex := "23A"}).tax = 50000 := by native_decide

/-! ## F3: the art. 14 one-fifth cap bites on the 23Α newcomer (contributions on exempt pay lost) -/
/-- At 55.000,01 € under 23Α: SI + GESY = 6.297,50 € but only 5.500,00 € (one fifth of 27.500,01 €) is
deductible. -/
theorem cap23A_bites :
    let r := person {} {w := 5500001, ex := "23A"}
    r.art14Claim = 629750 ∧ r.art14Cap = 550000 ∧ r.art14 = 550000 := by native_decide

/-! ## F4: child benefit and single-parent benefit cliffs (CBL Schedule para 2, 4, 8) -/
theorem cb_cliff_one_child : childBenefit 1 4900000 = 47879 ∧ childBenefit 1 4900001 = 0 := by native_decide
theorem cb_cliff_two_children : childBenefit 2 5900000 = 86996 ∧ childBenefit 2 5900001 = 0 := by native_decide
theorem cb_cliff_three_children : childBenefit 3 6400000 = 260991 ∧ childBenefit 3 6400001 = 0 := by native_decide
theorem cb_cliff_four_children : childBenefit 4 6900000 = 572100 ∧ childBenefit 4 6900001 = 0 := by native_decide
/-- Lone parent, one child: 2.310,36 € single-parent benefit + 478,79 € child benefit lost at 49.000,01 €. -/
theorem sp_cliff_one_child :
    singleParent true 1 4900000 + childBenefit 1 4900000 = 278915 ∧
    singleParent true 1 4900001 + childBenefit 1 4900001 = 0 := by native_decide
/-- Five or more children: no income limit at all (CBL Schedule para 2 proviso). -/
theorem cb_five_no_limit : childBenefit 5 100000000 = 5 * 143025 := by native_decide

/-! ## F5: SDC interest: the €12.000 total-income test is a notch (art. 3(2)(β)(iii)) -/
theorem sdc_interest_notch :
    (sdc {} {i := 1200000}).2.1 = 36000 ∧ (sdc {} {i := 1200001}).2.1 = 204000 := by native_decide

/-! ## F1: social insurance rate printed in SIL art. 5(1)(στ) (8,9 %) vs applied (8,8 %) -/
theorem si_statute_vs_applied :
    siEmployee {statuteSI := true} siCeiling = 592847 ∧ siEmployee {} siCeiling = 586186 := by native_decide

/-! ## F6: owner-manager, non-domiciled: no SDC at all on dividends, interest or rent (SDC Law art. 2) -/
theorem nondom_no_sdc (x : Person) : sdc {nonDom := true} x = (0, 0, 0) := by
  simp [sdc]

/-! ## F7: individual taxation: moving rent to a spouse with no income -/
/-- 20.000 € of rent costs a 60.000 € earner 5.071 € of income tax; the same rent in a non-earning spouse's name
costs 0 € (80 % of it, 16.000 €, is inside the 0 % band). -/
theorem rent_to_spouse :
    (person {} {w := 6000000, r := 2000000}).tax - (person {} {w := 6000000}).tax = 507100 ∧
    (person {} {r := 2000000}).tax = 0 := by native_decide

/-! ## F8: the 2026 scale as a timing lever -/
/-- A 12.000 € bonus on top of 60.000 €: 4.200 € tax in 2025, 3.600 € in 2026. -/
theorem bonus_deferral_gain :
    scaleTax 7200000 - scaleTax 6000000 = 420000 ∧ scaleTax26 7200000 - scaleTax26 6000000 = 360000 := by
  native_decide
/-- At 72.000 € of taxable income or more, the same income costs 1.585 € less in 2026. -/
theorem scale_2025_minus_2026_top : scaleTax 7200000 - scaleTax26 7200000 = 158500 := by native_decide

/-! ## F9: EUROMOD's "maximum deduction of 3,060" is the 2019 first-phase GESY rate (1,70 %) -/
theorem gesy_max_deduction : mulBp gesyCap gesyIncome = 477000 ∧ mulBp gesyCap 170 = 306000 := by native_decide

/-! ## F10: the reform's six-year sunset on the 17 % SDC for pre-2026 profits -/
/-- SDC Law art. 3(1)(α) as replaced by 245(I)/2025 (from 1.1.2026): "σε ποσοστό πέντε τοις εκατό (5%)", except
proviso (ii): dividends "μέχρι και έξι (6) έτη από την ημερομηνία έναρξης της ισχύος" of that law and "από κέρδη
των φορολογικών ετών μέχρι και το φορολογικό έτος 2025" pay 17 %. -/
def sdcDividend2026 : Int := 500
/-- 10.000 € of 2025 after-tax profit: paid out by 2031, 1.700 € SDC; retained, 70 % is deemed distributed at
31.12.2027 (art. 3Γ, 17 %) and the other 30 % paid after 31.12.2031 at 5 %: 1.340 € (−21 %). -/
theorem sunset_saving :
    mulBp 1000000 sdcDividend = 170000 ∧
    mulBp 700000 sdcDividend + mulBp 300000 sdcDividend2026 = 134000 := by native_decide

end CYTax
