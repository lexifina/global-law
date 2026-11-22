import TaxKernel
import CzTax.Theorems

/-!
# The § 16 ZDP schedule as a shared-kernel `Schedule` (TaxKernel v1.0)

`czSched` is the kernel form of § 16 odst. 1 (15 % up to 36 × average wage, 23 % above). `czSched_eq` proves it
equals the local `tax16Cents` for every non-negative base (kernel ticks = units × bp = 100 × hundredths), so every
generic kernel theorem below carries over to the Czech tax.
-/

namespace CzTax

def czSched : TaxKernel.Schedule := TaxKernel.Schedule.ofList [(0, rateLow), (threshold23, rateHigh)]

theorem czSched_progressive : czSched.progressive = true := by decide

theorem czSched_eq (b : Int) : czSched.ticks b = 100 * tax16Cents b := by
  simp only [czSched, TaxKernel.Schedule.ofList, TaxKernel.Schedule.ticks, List.map, TaxKernel.bandsTicks,
    tax16Cents, threshold23, avgWage, rateLow, rateHigh, TaxKernel.pos, CzTax.pos]
  omega

theorem cz_mono : TaxKernel.Monotone' czSched.ticks :=
  TaxKernel.Schedule.ticks_mono_of_progressive _ czSched_progressive

theorem cz_convex : TaxKernel.Convex czSched.ticks := TaxKernel.Schedule.ticks_convex _ czSched_progressive

theorem cz_no_jump {x y : Int} (h : x ≤ y) : czSched.ticks y - czSched.ticks x ≤ czSched.maxRate * (y - x) :=
  (TaxKernel.Schedule.ticks_lipschitz_of_progressive _ czSched_progressive h).2

theorem cz_maxRate : czSched.maxRate = 2300 := by decide

end CzTax
