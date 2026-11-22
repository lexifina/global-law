import SnTax.Basic

/-! # Senegal: kernel theorems instantiated; the statute's printed tables and two structural findings proved -/

namespace SnTax
open TaxKernel

theorem sched_progressive : sched.progressive = true := by decide
theorem sched_mono : Monotone' sched.ticks := Schedule.ticks_mono_of_progressive _ sched_progressive
theorem sched_convex : Convex sched.ticks := Schedule.ticks_convex _ sched_progressive
theorem sched_no_jump {x y : Int} (h : x ≤ y) : sched.ticks y - sched.ticks x ≤ sched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ sched_progressive h).2
/-- Individual taxation (art. 59) of a convex barème: pooling a couple's income would never be cheaper than taxing
each spouse alone, so separate taxation is the statute's choice, not a loss (kernel `splitting_le_separate`). -/
theorem split_ok (a b : Int) : splitting sched.ticks a b ≤ separate sched.ticks a b :=
  splitting_le_separate _ sched_convex sched_mono a b

/-! ## The part table of art. 174 2., row by row -/
theorem parts_single0 : halfParts false false 0 = 2 := by decide      -- "Célibataire ... sans enfant 1"
theorem parts_married0 : halfParts true false 0 = 3 := by decide      -- "Marié sans enfant à charge 1,5"
theorem parts_single1 : halfParts false false 1 = 3 := by decide      -- "Célibataire ou divorcé ayant 1 enfant 1,5"
theorem parts_married1 : halfParts true false 1 = 4 := by decide      -- "Marié ou veuf ayant 1 enfant 2"
theorem parts_single2 : halfParts false false 2 = 4 := by decide      -- "... 2 enfants 2"
theorem parts_married2 : halfParts true false 2 = 5 := by decide      -- "Marié ou veuf ayant 2 enfants 2,5"
theorem parts_married3 : halfParts true false 3 = 6 := by decide      -- "Marié ou veuf ayant 3 enfants 3"
theorem parts_single4 : halfParts false false 4 = 6 := by decide      -- "Célibataire ou divorcé ayant 4 enfants 3"
theorem parts_cap : halfParts true true 12 = 10 := by decide          -- art. 174 4.: at most 5 parts

/-- The reduction table's maxima are reached exactly at the tax where rate × tax = maximum, and the minima at
rate × tax = minimum: for 1,5 parts the reduction is the minimum 100 000 up to a tax of 1 000 000, then 10 %, then the
maximum 300 000 from a tax of 3 000 000. -/
theorem red15_min : reduction 3 900000 = 100000 := by decide
theorem red15_mid : reduction 3 2000000 = 200000 := by decide
theorem red15_max : reduction 3 5000000 = 300000 := by decide
/-- The minimum reduction wipes out a small tax: a taxpayer with 1,5 parts pays no IR on a tax of up to 100 000. -/
theorem red15_wipes : irTax 3 1100000 = 0 := by decide

/-- Barème check: 1 500 000 of taxable income bears 20 % of 870 000 = 174 000 (art. 173 1.). -/
theorem tax_1500k : grossTax 1500000 = 174000 := by decide
/-- The 30 % deduction reaches its 900 000 cap at a gross wage of 3 000 000 (art. 168 b)). -/
theorem wage_cap : wageNet 3000000 = 2100000 ∧ wageNet 4000000 = 3100000 := by decide

/-- F1 (TRIMF notch, art. 282): one franc of gross pay at 600 000 raises the TRIMF from 900 to 3 600: +2 700 F. -/
theorem trimf_notch_600k : trimf 600000 - trimf 599999 = 2700 := by decide
/-- The largest TRIMF step: 12 000 000 F of gross pay costs 18 000 F more TRIMF than 11 999 999 F. -/
theorem trimf_notch_12m : trimf 12000000 - trimf 11999999 = 18000 := by decide

/-- F2 (43 % cap of art. 174 1.): never binding, since the barème's average rate stays below its 43 % top rate. -/
theorem cap_not_binding : grossTax 100000000 < 100000000 * 4300 / BP := by decide

/-- The CGF minimum (art. 78 3.): any rent up to 360 000 F a year pays 30 000 F. -/
theorem cgf_min : cgf 360000 = 30000 ∧ cgf 120000 = 30000 := by decide
/-- CGF notch at 12 000 000 F of rent: 1/12 becomes 1,5/12 of the whole rent (+500 000 F for one more franc). -/
theorem cgf_notch_12m : cgf 12000001 - cgf 12000000 = 500000 := by decide

end SnTax
