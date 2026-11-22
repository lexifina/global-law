import RoTax.Basic

/-!
# Romania: properties proved

* the art. 77 alin. (4) table, transcribed row by row, is contiguous, falls row by row, and equals the formula
  "first-row percentage minus 0,5 points per started 50 lei above the minimum wage" (table = formula);
* the kernel's generic theorems for the flat 10 % tax and the 25 %/10 % contributions;
* properties of the monthly wage rule for all inputs (deduction never exceeds the net wage, nothing above the band,
  the non-taxable sum is at most 300 lei, the tax is never negative);
* the published worked figures (EUROMOD 2025 deduction amounts, July 2026 payroll example) reproduced exactly.
-/

namespace RoTax
open TaxKernel

/-! ## art. 77 alin. (4): table = formula -/

/-- The formula behind the statute's table: the first-row percentage less 50 bp for every started 50 lei above the
minimum wage. -/
def tableFormula (n : Nat) (off : Int) : Int := firstRow.getD (min n 4) 0 - 50 * ((off + 49) / 50)

theorem table_rows : (List.range 5).all (fun n => (stepTable n).length == 40) = true := by decide
theorem table_contiguous : (List.range 5).all (fun n => (stepTable n).contiguous) = true := by decide
theorem table_falls : (List.range 5).all (fun n => (stepTable n).valuesAnti) = true := by decide
theorem table_eq_formula_lo :
    (List.range 5).all (fun n => (stepTable n).agreesWith (tableFormula n) (·.lo)) = true := by decide
theorem table_eq_formula_hi :
    (List.range 5).all (fun n => (stepTable n).agreesWith (tableFormula n) (·.hi)) = true := by decide
theorem table_spans : (List.range 5).all (fun n =>
    ((stepTable n).head?.map (·.lo) == some 1) && ((stepTable n).getLast?.map (·.hi) == some 2000)) = true := by decide
/-- The last row of the no-dependant column is 0 %: the deduction reaches 0 exactly at the band's end. -/
theorem table_last_zero : (stepTable 0).getLast?.map (·.value) = some 0 := by decide
/-- With 1-4+ dependants the last row is still 5 %-25 %: the deduction does NOT reach 0 at the end of the band, it
drops to 0 at 2.001 lei above the minimum wage (a cliff; see `Findings.lean`). -/
theorem table_last_dependants :
    (List.range 4).map (fun n => ((stepTable (n + 1)).getLast?.map (·.value)).getD 0) = [500, 1000, 1500, 2500] := by
  decide

/-- EUROMOD CR RO (Y16) Table 2.14, 2025 column: 810, 1013, 1215, 1418, 1823 lei for 0..4+ dependants at the
minimum wage. -/
theorem euromod_2025_amounts :
    (List.range 5).map (fun n => pctOf (firstRow.getD n 0) minWage2025) = [810, 1013, 1215, 1418, 1823] := by decide

/-! ## Kernel parts -/

def taxSched : Schedule := Schedule.flat taxRate
def casC : Contribution := { name := "CAS", sched := Schedule.flat casRate, round := Rule.unitHalfUp }
def cassC : Contribution := { name := "CASS", sched := Schedule.flat cassRate, round := Rule.unitHalfUp }

theorem taxSched_progressive : taxSched.progressive = true := by decide
theorem taxSched_mono : Monotone' taxSched.ticks := Schedule.ticks_mono_of_progressive _ taxSched_progressive
theorem taxSched_convex : Convex taxSched.ticks := Schedule.ticks_convex _ taxSched_progressive
theorem taxSched_no_jump {x y : Int} (h : x ≤ y) : taxSched.ticks y - taxSched.ticks x ≤ taxSched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ taxSched_progressive h).2
theorem taxSched_split_ok (a b : Int) : splitting taxSched.ticks a b ≤ separate taxSched.ticks a b :=
  splitting_le_separate _ taxSched_convex taxSched_mono a b
theorem cas_mono {x y : Int} (h : x ≤ y) : casC.ticks x ≤ casC.ticks y :=
  Contribution.ticks_mono casC (by intro b hb; simp [casC, Schedule.flat] at hb; subst hb; decide)
    (by intro b hb; simp [casC, Schedule.flat] at hb; subst hb; decide) h
theorem cass_mono {x y : Int} (h : x ≤ y) : cassC.ticks x ≤ cassC.ticks y :=
  Contribution.ticks_mono cassC (by intro b hb; simp [cassC, Schedule.flat] at hb; subst hb; decide)
    (by intro b hb; simp [cassC, Schedule.flat] at hb; subst hb; decide) h
/-- The kernel contribution with half-up rounding is the model's `pctOf` (spot checks at the payroll figures). -/
theorem cas_kernel_agrees : [4050, 4051, 3750, 4125, 4326, 9968].all
    (fun x => casC.amount x == pctOf casRate x && cassC.amount x == pctOf cassRate x) = true := by decide

/-! ## The monthly wage rule, for all inputs -/

theorem untaxed_le (L : MonthLaw) (w : WageIn) (h : 0 ≤ L.untaxed) : untaxedSum L w ≤ L.untaxed := by
  unfold untaxedSum; split <;> omega

theorem untaxed_zero_above (L : MonthLaw) (w : WageIn) (h : L.untaxedCeiling < w.gross) : untaxedSum L w = 0 := by
  unfold untaxedSum; split <;> omega

theorem untaxed_zero_off_minimum (L : MonthLaw) (w : WageIn) (h : w.baseWage ≠ L.mw) : untaxedSum L w = 0 := by
  unfold untaxedSum; split
  · rename_i hc; exact absurd hc.2.1 h
  · rfl

theorem ded_le_net (L : MonthLaw) (w : WageIn) :
    (wageMonth L w).ded ≤ pos ((pos (w.gross - untaxedSum L w)) - pctOf casRate (pos (w.gross - untaxedSum L w))
      - pctOf cassRate (pos (w.gross - untaxedSum L w))) := by
  simp only [wageMonth]; omega

theorem base_ded_zero_above (L : MonthLaw) (w : WageIn) (h : L.mw + dedBand < w.gross) :
    (wageMonth L w).dedBase = 0 ∧ (wageMonth L w).dedYoung = 0 := by
  have : decide (w.gross ≤ L.mw + dedBand) = false := by simp; omega
  simp [wageMonth, this]

theorem pctOf_nonneg {p x : Int} (hp : 0 ≤ p) (hx : 0 ≤ x) : 0 ≤ pctOf p x := by
  unfold pctOf divR BP
  have : 0 ≤ p * x := Int.mul_nonneg hp hx
  exact Int.ediv_nonneg (by omega) (by decide)

theorem wage_tax_nonneg (L : MonthLaw) (w : WageIn) : 0 ≤ (wageMonth L w).tax := by
  simp only [wageMonth]
  exact pctOf_nonneg (by decide) (pos_nonneg _)

/-! ## Published worked figures reproduced -/

/-- July 2026 (Newsweek România, 6 Aug 2026, figures by ImpozitSalariu.ro): gross 4.325 lei at the minimum wage with
200 lei untaxed: CAS 1.031, CASS 413, deduction 865, tax 182, net 2.699; gross 4.326 lei: 1.082, 433, 843, 197,
net 2.614 ("1 leu brut ... scade netul cu 85 lei"). -/
theorem jul2026_example_4325 :
    let o := wageMonth lawJul2026 { gross := 4325, baseWage := 4325, deps := 0, young := false, schoolKids := 0 }
    (o.untaxed, o.cas, o.cass, o.ded, o.tax) = (200, 1031, 413, 865, 182) := by decide
theorem jul2026_example_4326 :
    let o := wageMonth lawJul2026 { gross := 4326, baseWage := 4326, deps := 0, young := false, schoolKids := 0 }
    (o.untaxed, o.cas, o.cass, o.ded, o.tax) = (0, 1082, 433, 843, 197) := by decide
theorem jul2026_minus_85 :
    wageNet lawJul2026 { gross := 4325, baseWage := 4325, deps := 0, young := false, schoolKids := 0 }
      - wageNet lawJul2026 { gross := 4326, baseWage := 4326, deps := 0, young := false, schoolKids := 0 } = 85 := by
  decide

end RoTax
