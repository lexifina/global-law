import MtTax.Model

/-! # Malta: the kernel's generic theorems instantiated, and what the statute claims -/

namespace MtTax
open TaxKernel

/-! ## The three YA 2026 tables are progressive schedules (kernel `Schedule`) -/

theorem married_progressive : marriedSched.progressive = true := by decide
theorem single_progressive : singleSched.progressive = true := by decide
theorem parent_progressive : parentSched.progressive = true := by decide

theorem married_mono : Monotone' marriedSched.ticks := Schedule.ticks_mono_of_progressive _ married_progressive
theorem single_mono : Monotone' singleSched.ticks := Schedule.ticks_mono_of_progressive _ single_progressive
theorem parent_mono : Monotone' parentSched.ticks := Schedule.ticks_mono_of_progressive _ parent_progressive

theorem married_convex : Convex marriedSched.ticks := Schedule.ticks_convex _ married_progressive
theorem single_convex : Convex singleSched.ticks := Schedule.ticks_convex _ single_progressive
theorem parent_convex : Convex parentSched.ticks := Schedule.ticks_convex _ parent_progressive

/-- No jump anywhere in the YA 2026 tables (unlike YA 2025, FINDINGS F3): one more euro costs at most 35 cents. -/
theorem single_no_jump {x y : Int} (h : x ≤ y) :
    singleSched.ticks y - singleSched.ticks x ≤ singleSched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ single_progressive h).2
theorem married_no_jump {x y : Int} (h : x ≤ y) :
    marriedSched.ticks y - marriedSched.ticks x ≤ marriedSched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ married_progressive h).2
theorem parent_no_jump {x y : Int} (h : x ≤ y) :
    parentSched.ticks y - parentSched.ticks x ≤ parentSched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ parent_progressive h).2

theorem single_le_top {x : Int} (h : 0 ≤ x) : singleSched.ticks x ≤ 3500 * x := by
  have := Schedule.ticks_le_maxRate_mul _ single_progressive h
  have e : singleSched.maxRate = 3500 := by decide
  rwa [e] at this

theorem single_zero : singleSched.ticks 0 = 0 := by decide

/-- Marginal rate = band rate (kernel `ticks_succ`). -/
theorem single_marginal (x : Int) : singleSched.ticks (x + 1) - singleSched.ticks x = singleSched.rate x :=
  Schedule.ticks_succ _ x

/-! ## Table = statute formula ("multiply by r% and then subtract €s"), for every chargeable income -/

theorem single_eq_formula (x : Int) (h : 0 ≤ x) : singleSched.ticks x = 100 * singleFormula x := by
  simp only [singleSched, Schedule.ticks, Schedule.ofList, List.map, bandsTicks, pos, singleFormula,
    formulaCents]
  repeat' split
  all_goals omega

theorem married_eq_formula (x : Int) (h : 0 ≤ x) : marriedSched.ticks x = 100 * marriedFormula x := by
  simp only [marriedSched, Schedule.ticks, Schedule.ofList, List.map, bandsTicks, pos, marriedFormula,
    formulaCents]
  repeat' split
  all_goals omega

theorem parent_eq_formula (x : Int) (h : 0 ≤ x) : parentSched.ticks x = 100 * parentFormula x := by
  simp only [parentSched, Schedule.ticks, Schedule.ofList, List.map, bandsTicks, pos, parentFormula,
    formulaCents]
  repeat' split
  all_goals omega

/-- The three tables are ordered for every income: married ≤ parent ≤ single. -/
theorem married_le_parent (x : Int) (h : 0 ≤ x) : marriedFormula x ≤ parentFormula x := by
  simp only [marriedFormula, parentFormula, formulaCents]
  repeat' split
  all_goals omega

theorem parent_le_single (x : Int) (h : 0 ≤ x) : parentFormula x ≤ singleFormula x := by
  simp only [singleFormula, parentFormula, formulaCents]
  repeat' split
  all_goals omega

/-- Above €60,000 the married table saves exactly €1,150 over the single one and €850 over the parent one. -/
theorem married_single_top (x : Int) (h : 60000 ≤ x) : singleFormula x - marriedFormula x = 115000 := by
  simp only [singleFormula, marriedFormula, formulaCents]
  repeat' split
  all_goals omega

/-! ## Joint vs separate computation (art. 49 vs art. 50), every split of every couple income -/

/-- The most separate computation (art. 50, two single tables) can save over the default joint computation:
€8,250, reached at €60,000 + €60,000 (grid search, FINDINGS F6); proved for every split. -/
theorem separate_saving_le (a b : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    marriedFormula (a + b) - (singleFormula a + singleFormula b) ≤ 825000 := by
  simp only [singleFormula, marriedFormula, formulaCents]
  repeat' split
  all_goals omega

/-- The most the joint computation can save over two single tables: €1,150 (one earner, €23,000 or more). -/
theorem joint_saving_le (a b : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    (singleFormula a + singleFormula b) - marriedFormula (a + b) ≤ 115000 := by
  simp only [singleFormula, marriedFormula, formulaCents]
  repeat' split
  all_goals omega

/-! ## Class One contribution: never above the category D maximum, never negative -/

/-- With children (parent tables each, art. 56(1)(b) last proviso) separate computation saves up to €8,850 and
joint at most €850. -/
theorem separate_parent_saving_le (a b : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    marriedFormula (a + b) - (parentFormula a + parentFormula b) ≤ 885000 := by
  simp only [parentFormula, marriedFormula, formulaCents]
  repeat' split
  all_goals omega

theorem joint_parent_saving_le (a b : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    (parentFormula a + parentFormula b) - marriedFormula (a + b) ≤ 85000 := by
  simp only [parentFormula, marriedFormula, formulaCents]
  repeat' split
  all_goals omega

theorem class1_le_max (age : Nat) (w : Int) : class1Weekly age w ≤ c1MaxNew := by
  unfold class1Weekly
  split
  · decide
  · simp only []
    split
    · split <;> decide
    · split <;> simp [c1MaxOld, c1MaxNew] <;> omega

/-! ## Children's Allowance: never below the fixed €8.66 a week per child -/

theorem ca_ge_fixed (inc : Int) : caFixedWeekly ≤ caWeeklyPerChild inc := by
  unfold caWeeklyPerChild
  simp only []
  split
  · exact Int.le_refl _
  · exact Int.le_max_left _ _

end MtTax
