import HrTax.Household

/-! # Croatia 2025: kernel theorems instantiated, and country properties for all inputs -/

namespace HrTax
open TaxKernel

/-! ## The local schedule (ZPD čl. 19, 19.a) -/
theorem zagreb_progressive : (annualSched zagreb2025).progressive = true := by decide
theorem zagreb_mono : Monotone' (annualSched zagreb2025).ticks :=
  Schedule.ticks_mono_of_progressive _ zagreb_progressive
theorem zagreb_convex : Convex (annualSched zagreb2025).ticks := Schedule.ticks_convex _ zagreb_progressive
theorem zagreb_no_jump {x y : Int} (h : x ≤ y) :
    (annualSched zagreb2025).ticks y - (annualSched zagreb2025).ticks x ≤ (annualSched zagreb2025).maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ zagreb_progressive h).2
theorem zagreb_le_top {x : Int} (h : 0 ≤ x) : (annualSched zagreb2025).ticks x ≤ 3300 * x := by
  have := Schedule.ticks_le_maxRate_mul _ zagreb_progressive h
  have e : (annualSched zagreb2025).maxRate = 3300 := by decide
  rwa [e] at this
/-- Individual taxation: two spouses never gain from a joint (splitting) assessment the law does not have; the kernel
theorem says splitting of a convex schedule would never cost more than separate assessment. -/
theorem zagreb_split_le (a b : Int) :
    splitting (annualSched zagreb2025).ticks a b ≤ separate (annualSched zagreb2025).ticks a b :=
  splitting_le_separate _ zagreb_convex zagreb_mono a b

/-- Every rate pair a city may set (ZPD čl. 19.a st. 2, NN 152/24 čl. 4) gives a progressive schedule: each lower
rate ceiling (20/21/22/23 %) is below every higher rate floor (25 %). For all rates, not only Zagreb's. -/
theorem allowed_rates_progressive (r : Rates) (k : Nat)
    (hl : (rateRange k).1 ≤ r.lower ∧ r.lower ≤ (rateRange k).2.1)
    (hh : (rateRange k).2.2.1 ≤ r.higher ∧ r.higher ≤ (rateRange k).2.2.2) :
    (annualSched r).progressive = true := by
  have hk : (rateRange k).1 = 1500 ∧ (rateRange k).2.1 ≤ 2300 ∧ (rateRange k).2.2.1 = 2500 := by
    unfold rateRange; split <;> decide
  simp only [Schedule.progressive, annualSched, Schedule.ofList, List.map, bandsSorted, ratesMono, List.all,
    bandLimitAnnual, Bool.and_eq_true, decide_eq_true_eq, Bool.and_true]
  omega

/-- The default rates of čl. 19.a st. 5 and every unit's maximum are progressive too. -/
theorem default_progressive : (annualSched defaultRates).progressive = true := by decide

/-! ## The 2024 pension-base reduction (ZD čl. 21.a) -/
theorem baseReduction_wf : baseReduction.WellFormed := by unfold Taper.WellFormed baseReduction; decide
/-- No jump at 700 € or at 1.300 €: the reduction is 300 € up to 700 € and 0 from 1.300 € (continuous). -/
theorem baseReduction_edges :
    (baseReduction.amount 70000, baseReduction.amount 70001, baseReduction.amount 129999, baseReduction.amount 130000) =
    (30000, 30000, 1, 0) := by decide
/-- Inside the band, 2 cents more pay remove 1 cent of reduction (kernel `Taper.amount_step`): the pillar-I base
rises by 3 cents, so the marginal pillar-I rate is 15 % × 1,5 = 22,5 % (total employee rate 27,5 %, not 20 %). -/
theorem baseReduction_step {m : Int} (h1 : 70000 ≤ m) (h2 : m + 2 ≤ 129999) :
    baseReduction.amount (m + 2) = baseReduction.amount m - 1 := by
  have hin : baseReduction.floor < baseReduction.amount (m + baseReduction.den) := by
    simp only [baseReduction, Taper.amount, Taper.reduction, divR, pos]; omega
  simpa [baseReduction] using Taper.amount_step baseReduction baseReduction_wf h1 hin
/-- The reduction never exceeds 300 € (kernel `Taper.amount_le_full`). -/
theorem baseReduction_le (m : Int) : baseReduction.amount m ≤ 30000 := by
  have := Taper.amount_le_full baseReduction baseReduction_wf m; simpa [baseReduction] using this
/-- ... and never raises a contribution: the reduced pillar-I base is at most the pay (for any pay). -/
theorem pillar1Base_le (m : Int) : pillar1Base m ≤ pos m := by
  unfold pillar1Base reducedBase monthBase pos
  have h0 : 0 ≤ baseReduction.amount (min (max 0 m) maxMonthlyBase) := by
    simp only [Taper.amount, baseReduction]; omega
  omega

/-! ## Personal allowance -/
/-- The child coefficients rise with rank (each further child is worth more than the previous one). -/
theorem childCoefs_increasing : childCoefs = [5, 7, 10, 14, 19, 25, 32, 40, 49] ∧
    (List.range 8).all (fun i => childCoefs.getD i 0 < childCoefs.getD (i + 1) 0) = true := by decide
/-- Ten children under the reading of r.br. 11 (+1,1 for the 10th): 26,1 × 600 € = 15.660 € a month. -/
theorem ten_children : childCoefTotal 10 = 261 ∧ childAllowanceMonthly 10 = 1566000 := by decide

/-! ## Young workers' relief (ZPD čl. 46 st. 2): never more than the tax -/
theorem youngReliefBp_le (a : Nat) : youngReliefBp a ≤ 10000 ∧ 0 ≤ youngReliefBp a := by
  unfold youngReliefBp; split <;> (try split) <;> decide

end HrTax
