import NLTax.Withholding

/-!
# NLTax.Theorems: properties of the 2025 statute, for all incomes (no `sorry`)

Money in cents; "ticks" = cents × bp; "num" = cents × pcm (see `Params.lean`).

1. **The kernel's band schedules** for art. 2.10 / 2.12 are progressive, monotone, continuous and convex (kernel
   theorems instantiated).
2. **The statute's own table is not a band sum.** Art. 2.10 writes kolom III (the tax at the start of a row) as a
   whole-euro amount, rounded down: € 3.140 where the band sum is € 3.140,6297 and € 17.523 where it is
   € 17.523,9545. Hence (a) the statutory tax is below the band sum by up to € 0,9545 (`t210_bands_gap`), and (b) it
   **falls** when income crosses € 38.441: one more cent of income lowers the tax by € 0,63 (`t210_drop`), so the
   statutory tax is neither monotone nor convex (`t210_not_monotone`, `t210_not_convex`). The same holds for box 2
   at € 67.804 (art. 2.12, kolom III € 16.611 against 16 611,98: `box2_drop`).
3. **The kortingen's afbouw.** Inside its band, every extra cent of verzamelinkomen removes exactly 6,337 % of a cent
   of algemene heffingskorting (`ahk_step`), and every extra cent of arbeidsinkomen 6,51 % of arbeidskorting
   (`ak_step`); the arbeidskorting never jumps (`ak_lipschitz`). The AHK is still positive at the start of the top
   bracket (€ 76.817) and ends only at € 76.820,08 (`ahk_alive_at_top`, `ahk_zero_after`): art. 10.6b rounds the
   afbouw percentage to three decimals (3 068 / 48 411 = 6,33740 % → 6,337 %).
4. **The combined marginal rate of an employee** (tax part + premies − kortingen, before the art. 8.8 cap binds):
   50,327 % on € 43.071 - € 76.817, above the 49,50 % top rate (`levy_step_middle`); 56,01 % on € 76.821 - € 129.077
   (`levy_step_top`).
5. **Withholding table vs statute**: for every annual table wage up to Lmax the Belastingdienst's rekenregel for the
   witte tabel withholds at most € 3,05 less, and at most € 0,30 more, than the statutory IB + premie of an employee
   aged under 67 with only that wage (`lb_vs_statute`).
-/

namespace NLTax
open TaxKernel

/-! ## 1. Kernel band schedules -/

theorem t210_bands_progressive : t210.bands.progressive = true := by decide
theorem t210_bands_mono : Monotone' t210.bands.ticks :=
  Schedule.ticks_mono_of_progressive _ t210_bands_progressive
theorem t210_bands_convex : Convex t210.bands.ticks := Schedule.ticks_convex _ t210_bands_progressive
theorem t210_bands_lipschitz {x y : Int} (h : x ≤ y) :
    0 ≤ t210.bands.ticks y - t210.bands.ticks x ∧ t210.bands.ticks y - t210.bands.ticks x ≤ t210.bands.maxRate * (y - x) :=
  Schedule.ticks_lipschitz_of_progressive _ t210_bands_progressive h

def box2Bands : Schedule := Schedule.ofList [(0, box2R1), (box2B1, box2R2)]
theorem box2_bands_progressive : box2Bands.progressive = true := by decide
/-- Box-2 income is a joint item of partners (art. 2.17 lid 5 b): splitting it between them never costs more than
booking it on one (kernel `splitting_le_separate` on the band schedule). -/
theorem box2_split_le (a b : Int) : splitting box2Bands.ticks a b ≤ separate box2Bands.ticks a b :=
  splitting_le_separate _ (Schedule.ticks_convex _ box2_bands_progressive)
    (Schedule.ticks_mono_of_progressive _ box2_bands_progressive) a b

/-! ## 2. The statute's table -/

theorem t210_bands_gap (x : Int) :
    0 ≤ t210.bands.ticks x - t210.ticks x ∧ t210.bands.ticks x - t210.ticks x ≤ 954500 := by
  dsimp only [Table3.bands, Table3.ticks, t210, Schedule.ticks, Schedule.ofList, List.map, bandsTicks, TaxKernel.pos, p0]
  split <;> (try split) <;> omega

/-- € 38.441,00 → € 38.441,01: the statutory tax falls by € 0,63 (62,6 cents). -/
theorem t210_drop : t210.ticks 3844101 < t210.ticks 3844100 := by decide
/-- In whole euros (box 1 is computed on a whole-euro income in practice): € 38.441 → € 38.442 lowers the tax part
from € 3.140,63 to € 3.140,37, and the premie stops at € 38.441 (Wfsv art. 8 lid 3), so IB + premie fall too. -/
theorem t210_drop_euro : t210.ticks 3844200 < t210.ticks 3844100 := by decide
theorem levy_drop_euro :
    t210.ticks 3844200 + 2765 * min 3844200 3844100 < t210.ticks 3844100 + 2765 * min 3844100 3844100 := by decide
theorem t210_drop_top : t210.ticks 7681701 < t210.ticks 7681700 := by decide

theorem t210_not_monotone : ¬ Monotone' t210.ticks := fun h => by
  have := h 3844100 3844101 (by decide); have := t210_drop; omega
theorem t210_not_convex : ¬ Convex t210.ticks := fun h => by
  have h1 := h 3844099
  have : t210.ticks (3844099 + 1) - t210.ticks 3844099 = 817 := by decide
  have : t210.ticks (3844099 + 2) - t210.ticks (3844099 + 1) < 0 := by decide
  omega

theorem box2_drop : box2Ticks 6780401 < box2Ticks 6780400 := by decide

/-! ## 3. Kortingen -/

theorem ahk_step (x : Int) (h1 : ahkStart ≤ x) (h2 : x + 1 ≤ 7682000) : ahkNum x - ahkNum (x + 1) = ahkRate := by
  dsimp only [ahkNum, y2025, ahkMax, ahkRate, ahkStart, eur, p0] at *; omega

theorem ahk_alive_at_top : 0 < ahkNum t210.b2 := by decide
theorem ahk_zero_after (x : Int) (h : 7682008 ≤ x) : ahkNum x = 0 := by
  dsimp only [ahkNum, y2025, ahkMax, ahkRate, ahkStart, eur, p0]; omega

theorem ak_step (x : Int) (h1 : 4307300 ≤ x) (h2 : x + 1 ≤ 12907700) : akNum x - akNum (x + 1) = akRateD := by
  dsimp only [akNum, y2025, akRateA, akCapA, akRateB, akStartB, akCapB, akRateC, akStartC, akCapC, akRateD, akStartD, eur,
    p0] at *
  omega

theorem ak_lipschitz (x : Int) : -akRateD ≤ akNum (x + 1) - akNum x ∧ akNum (x + 1) - akNum x ≤ akRateA + akRateB + akRateC := by
  dsimp only [akNum, y2025, akRateA, akCapA, akRateB, akStartB, akCapB, akRateC, akStartC, akCapC, akRateD, akStartD, eur, p0]
  omega

/-! ## 4. Combined marginal rate of an employee (pcm per cent of wage) -/

/-- IB tax part + premies volksverzekeringen − AHK − AK, exact, in cents × pcm, for an employee under 67 whose wage
`x` is both box-1 income and arbeidsinkomen, before the art. 8.8 cap (which does not bind here). -/
def levyNum (x : Int) : Int :=
  10 * t210.ticks x + 10 * ((pAOW + pAnw + pWlz) * min (p0 x) t210.b1) - ahkNum x - akNum x

theorem levy_step_middle (x : Int) (h1 : 4307300 ≤ x) (h2 : x + 1 ≤ t210.b2) :
    levyNum (x + 1) - levyNum x = 37480 + ahkRate + akRateD := by
  dsimp only [levyNum, y2025, Table3.ticks, t210, pAOW, pAnw, pWlz, ahkNum, akNum, ahkMax, ahkRate, ahkStart, akRateA, akCapA,
    akRateB, akStartB, akCapB, akRateC, akStartC, akCapC, akRateD, akStartD, eur, p0] at *
  split <;> split <;> (try split) <;> (try split) <;> omega

/-- 50,327 % > 49,50 %: the middle band's combined rate exceeds the top rate. -/
theorem middle_exceeds_top : 37480 + ahkRate + akRateD > 10 * t210.r3 := by decide

theorem levy_step_top (x : Int) (h1 : 7682008 ≤ x) (h2 : x + 1 ≤ 12907700) :
    levyNum (x + 1) - levyNum x = 49500 + akRateD := by
  dsimp only [levyNum, y2025, Table3.ticks, t210, pAOW, pAnw, pWlz, ahkNum, akNum, ahkMax, ahkRate, ahkStart, akRateA, akCapA,
    akRateB, akStartB, akCapB, akRateC, akStartC, akCapC, akRateD, akStartD, eur, p0] at *
  split <;> split <;> (try split) <;> (try split) <;> omega

/-! ## 5. The withholding table against the statute -/

/-- Statutory IB + premie (cents) of an employee under 67 whose only income is the wage `w` (euros, whole), as the
model computes it (`eval` reduces to this when nothing else is present: tax part, premie, AHK and AK each rounded
down to the cent, set off against each other, floored at 0). -/
def statuteEmployee (w : Int) : Int :=
  let x := 100 * w
  max 0 (t210.ticks x / 10000 + (pAOW + pAnw + pWlz) * min (p0 x) t210.b1 / 10000 - ahkNum x / 100000 - akNum x / 100000)

theorem lb_vs_statute (L : Int) (h0 : 0 ≤ L) (h1 : L ≤ lbLmax) :
    statuteEmployee L - 305 ≤ 100 * lbX L ∧ 100 * lbX L ≤ statuteEmployee L + 30 := by
  dsimp only [statuteEmployee, lbX, lbX1, lbAHK, lbARK, lbLmax, Table3.ticks, t210, pAOW, pAnw, pWlz, ahkNum, akNum, y2025,
    ahkMax, ahkRate, ahkStart, akRateA, akCapA, akRateB, akStartB, akCapB, akRateC, akStartC, akCapC, akRateD, akStartD,
    eur, p0] at *
  split <;> split <;> (try split) <;> (try split) <;> (try split) <;> (try split) <;> omega

end NLTax

namespace NLTax
/-- The arbeidskorting never reaches the € 5.599 of art. 8.11 lid 2 c: the 2,258 % build-up from € 26.288 reaches
€ 5.599 only at € 43.072,77, but the 6,51 % afbouw starts at € 43.071, so the maximum is € 5.598,96 (at € 43.071).
The three amounts were indexed and rounded separately (art. 10.1). -/
theorem ak_below_cap (x : Int) : akNum x < akCapC * 100000 := by
  dsimp only [akNum, y2025, akRateA, akCapA, akRateB, akStartB, akCapB, akRateC, akStartC, akCapC, akRateD, akStartD, eur, p0]
  omega
theorem ak_max_value : akNum akStartD = 55989601400 := by decide
end NLTax

namespace NLTax
/-- **A parent with a child under 12 whose arbeidsinkomen is the lower one (or who has no partner) pays no income
tax and no premies volksverzekeringen on a wage up to € 30.000**: the algemene heffingskorting, arbeidskorting and
IACK together are at least the tax part plus premies (35,82 % of the wage), so art. 8.8 caps them at the levy and the
levy is nil. In pcm × cents; the wage is box-1 income, verzamelinkomen and arbeidsinkomen at once. -/
theorem parent_no_levy (x : Int) (h0 : 0 ≤ x) (h1 : x ≤ 3000000) :
    10 * (817 + pAOW + pAnw + pWlz) * x ≤ ahkNum x + akNum x + iackNum x := by
  dsimp only [ahkNum, y2025, akNum, iackNum, ahkMax, ahkRate, ahkStart, akRateA, akCapA, akRateB, akStartB, akCapB, akRateC,
    akStartC, akCapC, akRateD, akStartD, iackRate, iackStart, iackMax, pAOW, pAnw, pWlz, eur, p0]
  omega
/-- Without the IACK the same wage is levied from € 11.049 (the algemene heffingskorting and arbeidskorting
are used up there; 27 767 x = 3 068 × 10⁷): at € 11.100 the levy exceeds them. -/
theorem no_iack_levy_at_11100 : 10 * (817 + pAOW + pAnw + pWlz) * 1110000 > ahkNum 1110000 + akNum 1110000 := by decide
end NLTax
