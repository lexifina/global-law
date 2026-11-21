import AlTax.Basic

/-! # Albania: kernel theorems instantiated, and the notches of the personal deduction (neni 22) proved -/

namespace AlTax
open TaxKernel

theorem emp_progressive : empSchedule.progressive = true := by decide
theorem emp_mono : Monotone' empSchedule.ticks := Schedule.ticks_mono_of_progressive _ emp_progressive
theorem emp_convex : Convex empSchedule.ticks := Schedule.ticks_convex _ emp_progressive
theorem bus_progressive : busSchedule.progressive = true := by decide
theorem individual_ok (a b : Int) : splitting empSchedule.ticks a b ≤ separate empSchedule.ticks a b :=
  splitting_le_separate _ emp_convex emp_mono a b

/-- The transitional monthly table of neni 69 (2) (June 2023 - December 2024) prints "22 100 lekë + 23% të shumës mbi
200 000 lekë" for monthly pay above 200 000 with a 30 000 deduction: 13 % of 170 000 = 22 100. The 2025 annual band
(2 040 000 = 12 × 170 000) is the same band. -/
theorem monthly_table_consistent : (Schedule.ofList [(0, 1300), (170000, 2300)]).ticks 170000 = 22100 * BP := by decide
theorem annual_band_is_12_months : 2040000 = 12 * 170000 := by decide

/-- F1: one lek of pay above 600 000 costs 23 400 lekë of tax (the deduction falls from 600 000 to 420 000). -/
theorem notch_600k : empTax 600001 0 - empTax 600000 0 = 23400 := by decide
/-- F1: one lek above 720 000 costs another 7 800 lekë (the deduction falls from 420 000 to 360 000). -/
theorem notch_720k : empTax 720001 0 - empTax 720000 0 = 7800 := by decide
/-- F1: the take-home pay (before contributions) at 600 001 is lower than at 600 000 until pay reaches 627 000. -/
theorem notch_net : (600001 - empTax 600001 0) < 600000 - empTax 600000 0 := by decide

end AlTax
