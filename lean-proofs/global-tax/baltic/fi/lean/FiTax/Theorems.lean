import FiTax.Household

/-!
# Finland 2025: the kernel's generic theorems instantiated, and properties the statute claims (no `sorry`)
-/

namespace FiTax
open TaxKernel

/-! ## State scale (Asteikkolaki 701/2024) -/

theorem state_progressive : stateSchedule.progressive = true := by decide
theorem state_mono : Monotone' stateSchedule.ticks := Schedule.ticks_mono_of_progressive _ state_progressive
theorem state_convex : Convex stateSchedule.ticks := Schedule.ticks_convex _ state_progressive
theorem state_no_jump {x y : Int} (h : x ≤ y) :
    stateSchedule.ticks y - stateSchedule.ticks x ≤ stateSchedule.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ state_progressive h).2
theorem state_maxRate : stateSchedule.maxRate = 4425 := by decide
theorem state_le_top {x : Int} (h : 0 ≤ x) : stateSchedule.ticks x ≤ 4425 * x := by
  have := Schedule.ticks_le_maxRate_mul _ state_progressive h
  rwa [state_maxRate] at this
theorem state_zero : stateSchedule.ticks 0 = 0 := by decide
/-- Individual assessment: taxing a couple's incomes jointly on this scale would never cost less (kernel
`separate_le_joint`); splitting would never cost more (`splitting_le_separate`). Finland has neither. -/
theorem state_separate_le_joint {a b : Int} (ha : 0 ≤ a) (hb : 0 ≤ b) :
    separate stateSchedule.ticks a b ≤ joint stateSchedule.ticks a b :=
  separate_le_joint _ state_convex state_zero ha hb
theorem state_split_le_separate (a b : Int) :
    splitting stateSchedule.ticks a b ≤ separate stateSchedule.ticks a b :=
  splitting_le_separate _ state_convex state_mono a b

/-- The published table (701/2024 1 §, "Vero alarajan kohdalla") equals the rates at every lower limit. -/
theorem state_table_points : stateTable.all (fun (l, t) => stateSchedule.ticks l == t * BP) = true := by decide

/-- The table equals the formula on every band: tax = tax at the lower limit + rate × the excess (cents × bp). -/
theorem state_table_eq_formula (x : Int) :
    (0 ≤ x → x ≤ eur 21200 → stateSchedule.ticks x = 1264 * x) ∧
    (eur 21200 ≤ x → x ≤ eur 31500 → stateSchedule.ticks x = 267968 * BP + 1900 * (x - eur 21200)) ∧
    (eur 31500 ≤ x → x ≤ eur 52100 → stateSchedule.ticks x = 463668 * BP + 3025 * (x - eur 31500)) ∧
    (eur 52100 ≤ x → x ≤ eur 88200 → stateSchedule.ticks x = 1086818 * BP + 3400 * (x - eur 52100)) ∧
    (eur 88200 ≤ x → x ≤ eur 150000 → stateSchedule.ticks x = 2314218 * BP + 4175 * (x - eur 88200)) ∧
    (eur 150000 ≤ x → stateSchedule.ticks x = 4894368 * BP + 4425 * (x - eur 150000)) := by
  simp only [Schedule.ticks, stateSchedule, Schedule.ofList, List.map, bandsTicks, pos, eur, BP]
  omega

/-! ## Capital income (TVL 124 § 2 mom) -/

theorem capital_progressive : capitalSchedule.progressive = true := by decide
theorem capital_mono : Monotone' capitalSchedule.ticks := Schedule.ticks_mono_of_progressive _ capital_progressive
theorem capital_convex : Convex capitalSchedule.ticks := Schedule.ticks_convex _ capital_progressive
/-- Splitting a capital gain over two years never costs more than realising it in one (convexity): the timing
lever of the 30/34 % threshold (FINDINGS). -/
theorem capital_spread_le (a b : Int) :
    splitting capitalSchedule.ticks a b ≤ separate capitalSchedule.ticks a b :=
  splitting_le_separate _ capital_convex capital_mono a b

/-! ## Allowances and credits -/

theorem basic_wf : basicTaper.WellFormed := by unfold Taper.WellFormed basicTaper; decide
theorem basic_antitone {x y : Int} (h : x ≤ y) : basicTaper.amount y ≤ basicTaper.amount x :=
  Taper.amount_antitone _ basic_wf h
theorem basic_le_full (x : Int) : basicTaper.amount x ≤ eur 4115 := Taper.amount_le_full _ basic_wf x
/-- Inside the perusvähennys band, 100 cents more income remove exactly 18 cents of deduction (kernel
`Taper.amount_step`): every euro there is taxed at 1,18 × the rates. -/
theorem basic_step {inc : Int} (hs : eur 4115 ≤ inc) (hin : 0 < basicTaper.amount (inc + 100)) :
    basicTaper.amount (inc + 100) = basicTaper.amount inc - 18 :=
  Taper.amount_step _ basic_wf hs hin
/-- The perusvähennys ends at 4 115 + 4 115 / 0,18 = 26 976,11 € of income. -/
theorem basic_end : basicTaper.amount 2697611 = 1 ∧ basicTaper.amount 2697612 = 0 := by decide

theorem workTaper_progressive : workCreditTaper.progressive = true := by decide
theorem workTaper_mono : Monotone' workCreditTaper.ticks :=
  Schedule.ticks_mono_of_progressive _ workTaper_progressive
/-- The eläketulovähennys is withdrawn at 51 % and then, above 22 500 €, at only 19,6 %: its withdrawal schedule is
not progressive, so the pensioner's marginal rate peaks inside 11 030-22 500 € and falls after (FINDINGS). -/
theorem pensionReduction_not_progressive : pensionReduction.progressive = false := by decide
theorem pensionReduction_nonneg : pensionReduction.RatesNonneg := by
  unfold Schedule.RatesNonneg pensionReduction; decide
theorem pensionReduction_mono {x y : Int} (h : x ≤ y) : pensionReduction.ticks x ≤ pensionReduction.ticks y :=
  Schedule.ticks_mono _ pensionReduction_nonneg h
theorem pensionFull_value : pensionDeductionFull = eur 11030 := by decide

/-- TVL 125 §: the work credit never exceeds its maximum (with the increases). -/
theorem workCredit_le_max (p : Person) (h : workCreditTaper.tax Rule.unitHalfUp (netEarned p) ≥ 0)
    (hM : 0 ≤ workCreditMaxOf p) : workCredit p ≤ workCreditMaxOf p := by
  unfold workCredit pos; omega

/-- The yleisradiovero never exceeds 160 € (2 § 1 mom). -/
theorem yle_le_max (p : Person) : yle p ≤ yleMax := by
  unfold yle; split
  · decide
  · exact Int.min_le_left _ _

/-! ## Contributions -/

/-- The päivärahamaksu floor is a notch (kernel `Contribution.floor_notch`): reaching 16 862 € charges 0,84 % on the
whole base at once, 141,64 €. -/
theorem daily_floor_notch :
    dailyContribution.ticks dailyContribution.floor - dailyContribution.ticks (dailyContribution.floor - 1)
      = dailyContribution.sched.ticks (dailyContribution.base dailyContribution.floor) :=
  Contribution.floor_notch dailyContribution
theorem daily_notch : dailyAllowance { wages := 1686199 } = 0 ∧ dailyAllowance { wages := 1686200 } = 14164 := by
  decide

end FiTax
