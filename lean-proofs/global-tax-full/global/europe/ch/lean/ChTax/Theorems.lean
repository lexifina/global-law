import ChTax.Basic

/-!
# Proofs for the Swiss model (kernel one-liners + country facts)

Kernel theorems (API §5) instantiated for the Zürich tariffs (progressive: everything holds) and the federal
tariffs as band sums (NOT progressive: the marginal rate falls from 13.2 % to 11.5 % at the top because of the
constitutional maximum of 11.5 %, BV Art. 128 Abs. 1 lit. a; `Schedule.ticks_convex` and therefore
`splitting_le_separate` do not apply: kernel finding). Country facts: the printed Grundtarif is 4-7 Rappen below its
own band sum from 43 500 francs on; the 25-franc minimum is a notch; the federal top band; the City/canton
multipliers; Zürich capital-benefit minimum; marriage penalty and concubinage examples (households in FINDINGS).
-/

namespace ChTax
open TaxKernel

/-! ## Zürich: progressive tariffs (kernel §5) -/

theorem zhSingle_progressive : zhSingle.progressive = true := by decide
theorem zhMarried_progressive : zhMarried.progressive = true := by decide
theorem zhSingle_mono : Monotone' zhSingle.ticks := Schedule.ticks_mono_of_progressive _ zhSingle_progressive
theorem zhMarried_mono : Monotone' zhMarried.ticks := Schedule.ticks_mono_of_progressive _ zhMarried_progressive
theorem zhSingle_convex : Convex zhSingle.ticks := Schedule.ticks_convex _ zhSingle_progressive
theorem zhMarried_convex : Convex zhMarried.ticks := Schedule.ticks_convex _ zhMarried_progressive
theorem zhSingle_no_jump {x y : Int} (h : x ≤ y) : zhSingle.ticks y - zhSingle.ticks x ≤ zhSingle.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ zhSingle_progressive h).2
theorem zhSingle_le_13pct {x : Int} (h : 0 ≤ x) : zhSingle.ticks x ≤ 1300 * x := by
  have := Schedule.ticks_le_maxRate_mul _ zhSingle_progressive h
  have e : zhSingle.maxRate = 1300 := by decide
  rwa [e] at this
theorem zhMarried_le_13pct {x : Int} (h : 0 ≤ x) : zhMarried.ticks x ≤ 1300 * x := by
  have := Schedule.ticks_le_maxRate_mul _ zhMarried_progressive h
  have e : zhMarried.maxRate = 1300 := by decide
  rwa [e] at this
/-- Zürich's two tariffs are not a splitting pair: the married tariff is its own schedule. Splitting the single
tariff would still never cost more than separate assessment (kernel theorem), for comparison. -/
theorem zh_split_ok (a b : Int) : splitting zhSingle.ticks a b ≤ separate zhSingle.ticks a b :=
  splitting_le_separate _ zhSingle_convex zhSingle_mono a b
/-- Marginal rate of the simple tax is the band's (e.g. 9 % at 80 000 single). -/
theorem zhSingle_marginal_80k : zhSingle.ticks 80001 - zhSingle.ticks 80000 = 900 := by
  decide

/-! ## Federal: the band sums are monotone but not progressive -/

theorem fedSingle_nonneg : fedSingleSched.RatesNonneg := by unfold Schedule.RatesNonneg; decide
theorem fedSingle_mono : Monotone' fedSingleSched.ticks := fun _ _ h => Schedule.ticks_mono _ fedSingle_nonneg h
theorem fedSingle_not_progressive : fedSingleSched.progressive = false := by decide
theorem fedMarried_not_progressive : fedMarriedSched.progressive = false := by decide

/-- The kernel's convexity fails: one franc more costs 11.80 % just below 793 400 and 11.50 % just above. -/
theorem fedSingle_not_convex : ¬ Convex fedSingleSched.ticks := by
  intro h
  have := h 793399
  revert this; decide

theorem fedMarried_not_convex : ¬ Convex fedMarriedSched.ticks := by
  intro h
  have := h 940899
  revert this; decide

/-- Above the top step the federal tax is exactly 11.5 % of the (100-franc) income (printed table). -/
theorem fed_top_flat : tariffRp fedSingleRows 1000000 = 1150 * 1000000 / 100 := by decide
theorem fed_top_flat_married : tariffRp fedMarriedRows 2000000 = 1150 * 2000000 / 100 := by decide

/-! ## The printed Grundtarif against its band sum (Rappen) -/

/-- At 43 500 the printed amount is 229.20; the band sum is 229.24. -/
theorem fed_printed_43500 : tariffRp fedSingleRows 43500 = 22920 ∧ fedSingleSched.ticks 43500 / 100 = 22924 := by
  decide
/-- At 76 100: printed 1 149.55, band sum 1 149.61. -/
theorem fed_printed_76100 : tariffRp fedSingleRows 76100 = 114955 ∧ fedSingleSched.ticks 76100 / 100 = 114961 := by
  decide
/-- From 82 000 on the printed table is 7 Rappen below its band sum (S100: OECD 1 618.87 = band sum; statute
1 618.80). -/
theorem fed_printed_83800 : tariffRp fedSingleRows 83800 = 161880 ∧ fedSingleSched.ticks 83800 / 100 = 161887 := by
  decide
/-- The married tariff's printed amounts equal its band sum at every row. -/
theorem fedMarried_rows_exact :
    fedMarriedRows.all (fun r => decide (fedMarriedSched.ticks r.lo / 100 = r.baseRp)) = true := by decide
/-- The Grundtarif's printed amounts differ from the band sum at 6 of its 10 rows (by 4 to 7 Rappen). -/
theorem fedSingle_rows_off :
    (fedSingleRows.map fun r => fedSingleSched.ticks r.lo / 100 - r.baseRp) = [0, 0, 4, 4, 6, 7, 7, 7, 7, 7] := by
  decide
/-- Despite the rounding, the printed table never falls at a row boundary (step from the last 100 below). -/
theorem fedSingle_rows_step_pos :
    fedSingleRows.tail.all (fun r => decide (tariffRp fedSingleRows r.lo - tariffRp fedSingleRows (r.lo - 100) > 0)) = true := by
  decide
theorem fedMarried_rows_step_pos :
    fedMarriedRows.tail.all (fun r => decide (tariffRp fedMarriedRows r.lo - tariffRp fedMarriedRows (r.lo - 100) > 0)) = true := by
  decide

/-! ## Notches and the child reduction -/

/-- DBG Art. 36 Abs. 3: a tax of 24.99 is not levied, 25.00 is: a 25-franc notch. -/
theorem fed_min_notch : fedFinalRp 2500 0 - fedFinalRp 2499 0 = 2500 := by decide
/-- In income terms (single, Grundtarif): 100 francs more taxable income at 18 400 → 18 500 raise the federal tax
from 0 to 25.41 (marginal 25.4 % on that step, against 0.77 % in the tariff). -/
theorem fed_min_notch_income : fedFinalRp (tariffRp fedSingleRows 18500) 0 = 2541 ∧
    fedFinalRp (tariffRp fedSingleRows 18400) 0 = 0 := by decide
/-- A married couple with two children (526 of child reductions): the reduced tax crosses 25 francs between
taxable 66 400 (548 - 526 = 22, not levied) and 66 500 (551 - 526 = 25.00, levied). -/
theorem fed_kids_notch : fedFinalRp (tariffRp fedMarriedRows 66400) 2 = 0 ∧
    fedFinalRp (tariffRp fedMarriedRows 66500) 2 = 2500 := by decide
/-- The child reduction is not refundable: unused reduction is lost (kernel `applyCredits_waste` pattern). -/
theorem fed_child_credit_wasted : fedFinalRp (tariffRp fedMarriedRows 47500) 2 = 0 ∧ tariffRp fedMarriedRows 47500 = 17800 := by
  decide

/-! ## Multipliers -/

theorem canton_mult_mono {a b : Int} (h : a ≤ b) : zhCantonMult.amount a ≤ zhCantonMult.amount b :=
  Multiplier.amount_mono _ (by decide) (by decide) (by unfold Round.isMonotoneMode; decide) h
/-- Canton + City of Zürich = 217 % of the simple tax, the factor the OECD's SLT implies. -/
theorem zh_total_multiplier : zhCantonMult.rate + zhCityMult.rate = 21700 := by decide

/-! ## Capital benefits (pension lump sums) -/

/-- DBG Art. 38: 1/5 of the tariff. A single person's 500 000 lump sum pays 1/5 of the tax on 500 000. -/
theorem fed_capital_500k : fedCapitalRp false 500000 = tariffRp fedSingleRows 500000 / 5 := by decide
/-- StG ZH § 37: the 2 % minimum binds for small lump sums (simple tax on 50 000 = 1 000). -/
theorem zh_capital_min_50k : zhCapitalSimpleRp false 50000 = 100000 := by decide

/-! ## Households (findings; values in Rappen) -/

/-- Federal + canton + City + Personalsteuer of one return (Rp), default options. -/
def totalRp (r : Ret) : Int := let x := assess {} {} none r; x.fedRp + x.cantonRp + x.cityRp + 100 * x.personal
def fedOnlyRp (r : Ret) : Int := (assess {} {} none r).fedRp
/-- An employee aged 40 with the statutory contributions (AHV/IV/EO, ALV, BVG minimum). -/
def emp (w : Int) : Person := { wage := w, ahvRp := ahvWageRp 40 w, alvRp := alvRp 40 w, bvgRp := bvgStatutoryRp 40 w }
/-- An employee aged 40 without a pension fund. -/
def empNoFund (w : Int) : Person := { wage := w, ahvRp := ahvWageRp 40 w, alvRp := alvRp 40 w }

/-- F-notch (BVG threshold): one franc of wage above 22 680 starts the BVG minimum (189 francs, BVV 2 Art. 5 / BVG
Art. 7-8) and with it removes the half-again insurance deduction (DBG Art. 33 Abs. 1bis lit. a, StG ZH § 31 lit. g):
taxes rise by 84.63 francs for one franc of pay. -/
theorem bvg_threshold_notch : totalRp { persons := [emp 22680] } = 43196 ∧ totalRp { persons := [emp 22681] } = 51659 := by
  decide

/-- F-notch (Säule 3a): a single employee without a pension fund (60 000) who pays ONE franc into Säule 3a pays
236.42 francs more tax (federal + canton + City): the 1-franc deduction removes 900 (federal) and 1 450 (Zürich)
of insurance deduction. Only from about 1 450 francs does a 3a payment start to save tax. -/
theorem p3a_one_franc_costs : totalRp { persons := [empNoFund 60000] } = 486035 ∧
    totalRp { persons := [{ empNoFund 60000 with p3a := 1 }] } = 509677 ∧
    totalRp { persons := [{ empNoFund 60000 with p3a := 1450 }] } = 484715 := by
  decide
/-- The same for a one-earner married couple (90 000, no pension fund): one franc into 3a costs 497.51 francs. -/
theorem p3a_one_franc_costs_married :
    totalRp { persons := [empNoFund 90000, {}], married := true } = 697882 ∧
    totalRp { persons := [{ empNoFund 90000 with p3a := 1 }, {}], married := true } = 747633 := by
  decide

/-- Marriage penalty (federal, DBG Art. 9 + Art. 36 Abs. 2): two employees earning 100 000 each pay 5 998.00 of
direct federal tax married and 2 × 1 750.80 = 3 501.60 unmarried (+71 %). -/
theorem marriage_penalty_2x100k :
    fedOnlyRp { persons := [emp 100000, emp 100000], married := true } = 599800 ∧
    fedOnlyRp { persons := [emp 100000] } = 175080 := by
  decide
/-- With two children (2 × 75 000): married 1 340.00; unmarried, the parent who keeps the children (Elterntarif,
263 per child) pays 0 and the other 569.76 (+135 % for the married couple). -/
theorem marriage_penalty_kids :
    fedOnlyRp { persons := [emp 75000, emp 75000], married := true, kidHalves := 4, kidCredits := 2, famAllow := 5160 } = 134000 ∧
    fedOnlyRp { persons := [emp 75000], parent := true, kidHalves := 2, kidCredits := 2, famAllow := 5160 } = 0 ∧
    fedOnlyRp { persons := [emp 75000], kidHalves := 2 } = 56976 := by
  decide


/-- FamZG notch: a family living on 100 000 of taxable capital income gets no family allowances while its earner
earns 7 559 (non-employed: income test of Art. 19 Abs. 2 fails), and the full allowances from 7 560 (employee: no
income test, Art. 13 Abs. 3): one franc of pay is worth 5 160 a year for children aged 6 and 11 (2 × 215 × 12). -/
theorem famzg_notch : famzgEntitled [7559] 100000 2 = false ∧ famzgEntitled [7560] 100000 2 = true ∧
    famAllowance false 6 + famAllowance false 11 = 5160 := by decide

end ChTax
