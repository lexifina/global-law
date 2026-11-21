import BgTax.Household

/-!
# Proofs: the kernel's generic theorems instantiated for Bulgaria, and the properties the statutes claim

Generic (API §5): the 10 % schedule of ЗДДФЛ чл. 48 is progressive, monotone, convex, has no jump, never exceeds 10 %,
and splitting cannot beat separate assessment (a flat schedule gains nothing from splitting: equality, proved below);
every contribution fund is constant above its monthly ceiling.

Country-specific: the employee total is 13.78 % for both pension cohorts (КСО чл. 6, ал. 3, т. 8-9 + чл. 157, ал. 3 +
ЗЗО чл. 40); the child relief's transfer to the other parent (чл. 22в, ал. 4) makes the couple's relief
`min R (room1 + room2)` whoever claims first; the allowance's income limits are notches.
-/

namespace BgTax
open TaxKernel

/-! ## The 10 % schedule (ЗДДФЛ чл. 48, ал. 1) -/

theorem pit_progressive : pitSchedule.progressive = true := by decide
theorem pit_mono : Monotone' pitSchedule.ticks := Schedule.ticks_mono_of_progressive _ pit_progressive
theorem pit_convex : Convex pitSchedule.ticks := Schedule.ticks_convex _ pit_progressive
theorem pit_no_jump {x y : Int} (h : x ≤ y) :
    pitSchedule.ticks y - pitSchedule.ticks x ≤ pitSchedule.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ pit_progressive h).2
theorem pit_le_10pct {x : Int} (h : 0 ≤ x) : pitSchedule.ticks x ≤ 1000 * x := by
  have := Schedule.ticks_le_maxRate_mul _ pit_progressive h
  have e : pitSchedule.maxRate = 1000 := by decide
  rwa [e] at this
theorem pit_split_ok (a b : Int) : splitting pitSchedule.ticks a b ≤ separate pitSchedule.ticks a b :=
  splitting_le_separate _ pit_convex pit_mono a b

/-- The marginal rate is 10 % at every base (kernel `ticks_succ`). -/
theorem pit_marginal (x : Int) : pitSchedule.ticks (x + 1) - pitSchedule.ticks x = pitSchedule.rate x :=
  Schedule.ticks_succ pitSchedule x

theorem pit_rate_const (x : Int) (h : 0 ≤ x) : pitSchedule.rate x = 1000 := by
  simp [pitSchedule, Schedule.flat, Schedule.rate, bandsRate, pitRate]
  omega

/-- A flat tax on non-negative bases is additive: splitting income with a spouse changes nothing (ЗДДФЛ has no
joint assessment and none would help). -/
theorem pit_ticks_additive (a b : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    pitSchedule.ticks (a + b) = pitSchedule.ticks a + pitSchedule.ticks b := by
  simp [pitSchedule, Schedule.flat, Schedule.ticks, bandsTicks, pitRate, pos]
  omega

/-! ## Contributions -/

/-- Every fund is constant above the month's ceiling (kernel `ticks_above_ceiling`). -/
theorem fund_above_ceiling (n : String) (r : Int) (m : Nat) {x : Int} (hx : maxInsurable m ≤ x) :
    (fund n r m).ticks x = (fund n r m).sched.ticks (maxInsurable m) := by
  have hc : 0 ≤ maxInsurable m := by unfold maxInsurable LEV; split <;> omega
  have := Contribution.ticks_above_ceiling (fund n r m) hc hx (by simp [fund]; omega)
  simpa [fund] using this

/-- The employee total is 13.78 % for persons born after 1959 (6.58 + 1.4 + 0.4 + 2.2 + 3.2) … -/
theorem ee_total_1960 : (eeRates false).foldl (fun a p => a + p.2) 0 = 1378 := by decide
/-- … and for persons born before 1960 (8.78 + 1.4 + 0.4 + 3.2). -/
theorem ee_total_pre1960 : (eeRates true).foldl (fun a p => a + p.2) 0 = 1378 := by decide

/-- The year's ceiling: 3 × 3 750 + 9 × 4 130 = 48 420 лв.; the self-insured minimum 3 × 933 + 9 × 1 077 = 12 492 лв. -/
theorem max_year : maxInsurableYear = 48420 * LEV := by decide
theorem min_self_year : minSelfInsuredYear = 12492 * LEV := by decide

/-- Employer side 18.92 % (lowest work-accident group). -/
theorem er_total : erTotal = 1892 := by decide

/-! ## Child relief shared by the parents (ЗДДФЛ чл. 22в, ал. 4) -/

theorem splitRelief_total (r a b : Int) (hr : 0 ≤ r) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    (splitRelief r a b).1 + (splitRelief r a b).2 = min r (a + b) := by
  simp only [splitRelief, pos]
  omega

/-- The order of the claims does not matter. -/
theorem splitRelief_symm (r a b : Int) (hr : 0 ≤ r) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    (splitRelief r a b).1 + (splitRelief r a b).2 = (splitRelief r b a).1 + (splitRelief r b a).2 := by
  rw [splitRelief_total r a b hr ha hb, splitRelief_total r b a hr hb ha, Int.add_comm]

/-- The 2025 relief is 30 times the codified amount for every number of children (ЗДБРБ 2025 ПЗР § 3 against
ЗДДФЛ чл. 22в, ал. 1). -/
theorem childRelief_30x (n : Nat) : childRelief n = 30 * childReliefCodified n := by
  match n with
  | 0 => decide
  | 1 => decide
  | 2 => decide
  | _ + 3 => simp [childRelief, childReliefCodified, LEV]

/-! ## The allowance's notches (ЗДБРБ 2025 чл. 64) -/

/-- Family of 4 (two children): the full allowance stops at 760 лв. per member from April: one stotinka of annual
income more costs 22 лв. a month for nine months (198 лв.). -/
theorem allowance_notch_full :
    allowanceYear 2 4 (12 * 4 * 760 * LEV) - allowanceYear 2 4 (12 * 4 * 760 * LEV + 1) = 198 * LEV := by decide

/-- … and at 860 лв. per member the whole remaining allowance goes (88 лв. a month for nine months, plus the
January-March months already lost at 810 лв.): 792 лв. for one stotinka. -/
theorem allowance_notch_part :
    allowanceYear 2 4 (12 * 4 * 860 * LEV) - allowanceYear 2 4 (12 * 4 * 860 * LEV + 1) = 792 * LEV := by decide

end BgTax
