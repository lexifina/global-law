import AuTax.Household
import AuTax.Schedule1

/-!
# Table vs statute: Schedule 1 scale 2 against the year's liability (single resident, wages only)

`withheldYear x` = 52 x the weekly scale 2 amount (tax-free threshold claimed, no offsets declared, no Medicare
adjustment); `liabilityYear p x` = ITRA Sch 7 tax - LITO + Medicare levy (MLA s. 7) on 52 x weekly earnings.
-/

namespace AuTax

def withheldYear (x : Int) : Int := 52 * aud (withhold scale2 x)

def liabilityYear (p : Params) (x : Int) : Int :=
  let ti := aud (52 * x)
  pos (basicTaxC p ti - litoC p ti) + levyS7C p ti

/-- Never under-withholds a single wage earner on weekly earnings $0-$4,000, in 2024-25 or 2025-26. -/
theorem sched1_never_under :
    (List.range 4001).all (fun w => liabilityYear p2025 w ≤ withheldYear w &&
      liabilityYear p2026 w ≤ withheldYear w) = true := by native_decide

/-- The largest over-withholding: $765.00 at $535 a week ($27,820 a year) in 2024-25 (the liability is $899.00,
the withholding $1,664.00), and $843.90 at $585 a week in 2025-26. -/
theorem sched1_max_over_2025 :
    withheldYear 535 - liabilityYear p2025 535 = 76500 ∧
    (List.range 4001).all (fun w => withheldYear w - liabilityYear p2025 w ≤ 76500) = true := by native_decide

theorem sched1_max_over_2026 :
    withheldYear 585 - liabilityYear p2026 585 = 84390 ∧
    (List.range 4001).all (fun w => withheldYear w - liabilityYear p2026 w ≤ 84390) = true := by native_decide

/-- Where it comes from (2024-25, $500 a week): withholding $1,144 is $104 under the liability without LITO
($1,248) but $596 over the liability with it ($548): the $700 offset is almost entirely left for the return. -/
theorem sched1_lito_left_out :
    withheldYear 500 = 114400 ∧ liabilityYear p2025 500 = 54800 ∧
    pos (basicTaxC p2025 (aud 26000)) + levyS7C p2025 (aud 26000) = 54800 + 70000 := by native_decide

end AuTax
