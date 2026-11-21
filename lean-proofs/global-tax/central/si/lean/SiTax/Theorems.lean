import SiTax.Basic

/-!
# Slovenia 2025: the kernel's generic theorems instantiated, and checks of FURS's published tables

Every statement is closed by `decide`, `rfl` or a kernel theorem: no unproved steps, no compiled evaluation.
-/

namespace SiTax
open TaxKernel

/-! ## The čl. 122 schedule (kernel `Schedule`) -/

theorem sched_progressive : sched.progressive = true := by decide
theorem sched_mono : Monotone' sched.ticks := Schedule.ticks_mono_of_progressive _ sched_progressive
theorem sched_convex : Convex sched.ticks := Schedule.ticks_convex _ sched_progressive
/-- No jump anywhere in the schedule: one more cent costs at most 50 % of a cent. -/
theorem sched_no_jump {x y : Int} (h : x ≤ y) : sched.ticks y - sched.ticks x ≤ sched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ sched_progressive h).2
theorem sched_maxRate : sched.maxRate = 5000 := by decide
theorem sched_le_top {x : Int} (h : 0 ≤ x) : sched.ticks x ≤ 5000 * x := by
  have := Schedule.ticks_le_maxRate_mul _ sched_progressive h
  rwa [sched_maxRate] at this
/-- Splitting would never cost a couple more than separate assessment (Slovenia has no splitting: spouses are
taxed individually; the inequality measures what equalising a couple's bases would save, see `unit.py`). -/
theorem split_ok (a b : Int) : splitting sched.ticks a b ≤ separate sched.ticks a b :=
  splitting_le_separate _ sched_convex sched_mono a b

/-! ## FURS's printed annual table equals the statute's schedule (Lestvica 2025) -/

/-- Each printed "fixed amount" is the schedule's tax at the row's lower threshold, rounded to the cent:
1.473,64, 6.122,11, 15.061,48 and 24.358,43 (refs/fu_Lestvica_2025.txt). -/
theorem furs_fixed_amounts : furTable.all (fun (lo, fx, _) => taxOn lo == fx) = true := by decide
/-- … and each printed rate is the schedule's marginal rate in that row. -/
theorem furs_rates : furTable.all (fun (lo, _, r) => sched.rate lo == r) = true := by decide

/-- **F2 (convention)**: chaining the printed rows does not reproduce the next row to the cent: the fourth row
(15.061,48 + 39 % above 54.178,00) gives 24.358,4248 € at 78.016,32 € (24.358,42 rounded), the fifth row starts
at 24.358,43 (the exact cumulative tax is 24.358,4288). A taxpayer computing by the table pays at most 1 cent
more just above 78.016,32 than just below. -/
theorem furs_row4_chain : 1506148 * 10000 + 3900 * (7801632 - 5417800) = 24358424800 := by decide
theorem furs_exact_at_top : sched.ticks 7801632 = 24358428800 := by decide

/-- The monthly withholding table (1/12 of the year, čl. 127): thresholds 767,52, 2.257,42, 4.514,83, 6.501,36
are the annual ones divided by 12, rounded to the cent. -/
theorem monthly_thresholds :
    [921026, 2708900, 5417800, 7801632].map (fun t => divR .halfUp t 12) = [76752, 225742, 451483, 650136] := by
  decide

/-- The monthly table's fixed amounts 122,80, 510,18, 1.255,12, 2.029,87 (FURS Lestvica 2025, akontacija) are the
monthly schedule's tax at each threshold. -/
def monthlySched : Schedule :=
  Schedule.ofList [(0, 1600), (76752, 2600), (225742, 3300), (451483, 3900), (650136, 5000)]
theorem monthly_fixed_amounts :
    [76752, 225742, 451483, 650136].map (fun t => monthlySched.tax Rule.unitHalfUp t)
      = [12280, 51018, 125512, 202987] := by decide
/-- FURS's monthly child-allowance column is the annual amount / 12 (236,53, 257,13, 428,87, 600,61, 772,34, and
171,74 for each further child). -/
theorem monthly_child_amounts :
    [283830, 308552, 514639, 720726, 926812, 206087].map (fun a => divR .halfUp a 12)
      = [23653, 25713, 42887, 60061, 77234, 17174] := by decide

/-! ## Indexation (čl. 118, Pravilnik Ur. l. RS 108/24): every 2025 amount is the 2024 amount × 1,052 -/

/-- 5.000 → 5.260,00; 16.000 → 16.832,00; 18.761,40 → 19.736,99; 1.500 → 1.578,00; 1.300 → 1.367,60;
2.698 → 2.838,30; second-child step 235 → 247,22; third 2.194 → 2.308,09; fourth 4.153 → 4.368,96;
fifth 6.112 → 6.429,82; sixth and later 1.959 → 2.060,87. -/
theorem indexation_2025 :
    [500000, 1600000, 1876140, 150000, 130000, 269800, 23500, 219400, 415300, 611200, 195900].map
      (fun x => pct x 10520)
      = [526000, 1683200, 1973699, 157800, 136760, 283830, 24722, 230809, 436896, 642982, 206087] := by decide

/-- The child amounts the model uses are the first-child amount plus the indexed steps (čl. 114(2)). -/
theorem child_amounts :
    [childAmount 0, childAmount 1, childAmount 2, childAmount 3, childAmount 4, childAmount 5]
      = [283830, 283830 + 24722, 283830 + 230809, 283830 + 436896, 283830 + 642982,
         283830 + 642982 + 206087] := by decide

/-- **F5 (gov-error, FURS guide)**: "Odmera dohodnine za leto 2025" (refs/fu_Odmera_dohodnine_2025.txt, 8.4)
prints the step for the sixth and later children as "2.060,97 EUR"; 1.959 × 1,052 = 2.060,868, i.e. 2.060,87,
which is what FURS's own Lestvica 2025 and the Pravilnik print. -/
theorem furs_guide_sixth_child : pct 195900 10520 = 206087 ∧ pct 195900 10520 ≠ 206097 := by decide

/-! ## The general allowance (kernel `Taper`), čl. 111 -/

theorem general_wf : generalTaper.WellFormed := by unfold Taper.WellFormed generalTaper; decide
theorem general_antitone {x y : Int} (h : x ≤ y) : generalTaper.amount y ≤ generalTaper.amount x :=
  Taper.amount_antitone _ general_wf h
theorem general_floor (x : Int) : 526000 ≤ generalTaper.amount x := Taper.floor_le_amount generalTaper x
theorem general_at_zero : generalTaper.amount 0 = 2499699 := by decide
/-- Above 16.832,00 € of total income: the plain 5.260,00 €. -/
theorem general_above (x : Int) (h : generalExtraLimit ≤ x) : generalTaper.amount x = 526000 := by
  unfold Taper.amount Taper.reduction generalTaper generalExtraLimit divR pos at *; simp only at *; omega
/-- **The taper band**: 1.000 € more total income (100000 cents) removes exactly 1.172,59 € of allowance while the
allowance is above 5.260 € (kernel `Taper.amount_step`): taxable income rises by 2.172,59 € per 1.000 € of income
before contributions are counted. -/
theorem general_step {inc : Int} (hs : 0 ≤ inc) (hin : 526000 < generalTaper.amount (inc + 100000)) :
    generalTaper.amount (inc + 100000) = generalTaper.amount inc - 117259 :=
  Taper.amount_step generalTaper general_wf hs hin

/-- **F3 (statute-fault, cents)**: the formula of čl. 111(3) is already negative at its own upper limit, in the
statute (18.761,40 − 1,17259 × 16.000 = −0,04) and in 2025 (19.736,99 − 1,17259 × 16.832 = −0,04): read
literally, total income in (16.831,97; 16.832,00] gets up to 4 cents less than 5.260 €. -/
theorem statute_formula_negative :
    1876140 * 100000 < 117259 * 1600000 ∧ 1973699 * 100000 < 117259 * 1683200 := by decide

/-! ## Contributions (kernel `Contribution`) -/

theorem employee_ssc_mono {x y : Int} (h : x ≤ y) : employeeSSC.ticks x ≤ employeeSSC.ticks y :=
  Contribution.ticks_mono employeeSSC
    (by intro b hb; simp [employeeSSC, Schedule.flat, employeeRate] at hb; simp [hb])
    (by intro b hb; simp [employeeSSC, Schedule.flat, employeeRate] at hb; simp [hb]) h
theorem ozp_2025 : ozpYear = 44170 := by decide

/-! ## Child benefit (kernel `Table`) -/

theorem classes_contiguous : classTable.contiguous = true := by decide
theorem classes_increasing : classTable.valuesMono = true := by decide
/-- Within each rank, a higher income class never pays more (primary school). -/
theorem cb_antitone_primary :
    (List.range 3).all (fun r => (List.range 8).all (fun k =>
      decide (childBenefitMonthly ((k : Int) + 2) r false ≤ childBenefitMonthly ((k : Int) + 1) r false))) = true := by
  decide
/-- Above class 8 (1.293,36 € a month per person) there is no child benefit at all: the cliff. -/
theorem cb_cliff : classTable.lookup 129336 0 = 8 ∧ classTable.lookup 129337 0 = 0 := by decide

end SiTax
