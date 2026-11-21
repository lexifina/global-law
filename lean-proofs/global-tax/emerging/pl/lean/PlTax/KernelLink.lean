import TaxKernel
import PlTax.Theorems

/-!
# Link to the shared kernel (`~/cmp20/kernel`, TaxKernel API v1.0)

The model was written before the kernel existed (its generic parts are in `PlTax/Kernel.lean`). Here the Polish scale
is stated as kernel schedules, the kernel's generic theorems are instantiated for it, and a bridge theorem proves the
model's `scaleTax` equals the kernel schedule on every whole-złoty base, so every kernel theorem applies to the model.
-/

namespace PlTax.KernelLink

/-- art. 27 ust. 1 as kernel bands on whole złoty, before the kwota zmniejszająca (which the OECD books as a credit). -/
def sched : TaxKernel.Schedule := TaxKernel.Schedule.ofList [(0, 1200), (120000, 3200)]

/-- The same scale with the kwota zmniejszająca 3600 zł written as a 30 000 zł zero band. -/
def schedZero : TaxKernel.Schedule := TaxKernel.Schedule.ofList [(0, 0), (30000, 1200), (120000, 3200)]

theorem sched_progressive : sched.progressive = true := by decide
theorem schedZero_progressive : schedZero.progressive = true := by decide

theorem sched_mono : TaxKernel.Monotone' sched.ticks :=
  TaxKernel.Schedule.ticks_mono_of_progressive _ sched_progressive
theorem schedZero_mono : TaxKernel.Monotone' schedZero.ticks :=
  TaxKernel.Schedule.ticks_mono_of_progressive _ schedZero_progressive
theorem schedZero_convex : TaxKernel.Convex schedZero.ticks :=
  TaxKernel.Schedule.ticks_convex _ schedZero_progressive

/-- Kernel `splitting_le_separate` for the Polish scale (art. 6 ust. 2): splitting never costs more. -/
theorem split_ok (a b : Int) : TaxKernel.splitting schedZero.ticks a b ≤ TaxKernel.separate schedZero.ticks a b :=
  TaxKernel.splitting_le_separate _ schedZero_convex schedZero_mono a b

/-- Kernel `ticks_le_maxRate_mul`: at most 32 % of the base. -/
theorem le_top {x : Int} (h : 0 ≤ x) : schedZero.ticks x ≤ 3200 * x := by
  have := TaxKernel.Schedule.ticks_le_maxRate_mul _ schedZero_progressive h
  have e : schedZero.maxRate = 3200 := by decide
  rwa [e] at this

/-- **Bridge**: on every whole-złoty base the model's art. 27 tax (grosze) is the kernel zero-band schedule's ticks
divided by 100 (ticks are złoty × basis points; 12 % of a whole złoty is a whole number of grosze, so no rounding). -/
theorem bridge (b : Int) (h : 0 ≤ b) : scaleTax (100 * b) = schedZero.ticks b / 100 := by
  rw [scaleTax_eq_statute _ (by omega)]
  simp only [scaleStatute, TaxKernel.Schedule.ticks, schedZero, TaxKernel.Schedule.ofList, List.map,
    TaxKernel.bandsTicks, TaxKernel.pos, PlTax.pos, rhu]
  split <;> omega

end PlTax.KernelLink
