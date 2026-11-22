import AuTax.Household
import AuTax.Schedule1

/-!
# Properties for all inputs (2024-25 parameters), and the named notches

Money in cents; the rates schedule `auSchedule` (kernel `Schedule`) is in whole dollars (ticks = dollars x bp).
-/

namespace AuTax

open TaxKernel in
/-- The ITRA Sch 7 schedule (2024-25 and 2025-26) is progressive in the kernel's sense. -/
theorem au_progressive : (auSchedule p2025).progressive = true := by decide

theorem au_2026_same : auSchedule p2026 = auSchedule p2025 := by decide

open TaxKernel in
/-- Kernel theorems instantiated: tax never falls when income rises, is convex (marginal rates never fall),
never jumps (at most 45 % of an increase), never exceeds 45 % of income, and tax on nil is nil. -/
theorem au_mono : Monotone' (auSchedule p2025).ticks := Schedule.ticks_mono_of_progressive _ au_progressive
open TaxKernel in
theorem au_convex : Convex (auSchedule p2025).ticks := Schedule.ticks_convex _ au_progressive
open TaxKernel in
theorem au_lipschitz {x y : Int} (h : x ≤ y) :
    0 ≤ (auSchedule p2025).ticks y - (auSchedule p2025).ticks x ∧
    (auSchedule p2025).ticks y - (auSchedule p2025).ticks x ≤ 4500 * (y - x) := by
  have := Schedule.ticks_lipschitz_of_progressive _ au_progressive h
  have hm : (auSchedule p2025).maxRate = 4500 := by decide
  rw [hm] at this; exact this
open TaxKernel in
theorem au_le_top {x : Int} (h : 0 ≤ x) : (auSchedule p2025).ticks x ≤ 4500 * x := by
  have := Schedule.ticks_le_maxRate_mul _ au_progressive h
  have hm : (auSchedule p2025).maxRate = 4500 := by decide
  rw [hm] at this; exact this

/-- Nothing below the tax-free threshold, and the ATO's closed forms ($4,288 + 30c over $45,000; $31,288 + 37c over
$135,000; $51,638 + 45c over $190,000), for every whole-dollar income. -/
theorem tax_zero_below_threshold (x : Int) (h : x ≤ 18200) : (auSchedule p2025).ticks x = 0 := by
  simp [auSchedule, p2025, TaxKernel.Schedule.ofList, TaxKernel.Schedule.ticks, TaxKernel.bandsTicks, TaxKernel.pos]; omega
theorem tax_closed_form_30 (x : Int) (h1 : 45000 ≤ x) (h2 : x ≤ 135000) :
    (auSchedule p2025).ticks x = 4288 * 10000 + 3000 * (x - 45000) := by
  simp [auSchedule, p2025, TaxKernel.Schedule.ofList, TaxKernel.Schedule.ticks, TaxKernel.bandsTicks, TaxKernel.pos]; omega
theorem tax_closed_form_37 (x : Int) (h1 : 135000 ≤ x) (h2 : x ≤ 190000) :
    (auSchedule p2025).ticks x = 31288 * 10000 + 3700 * (x - 135000) := by
  simp [auSchedule, p2025, TaxKernel.Schedule.ofList, TaxKernel.Schedule.ticks, TaxKernel.bandsTicks, TaxKernel.pos]; omega
theorem tax_closed_form_45 (x : Int) (h1 : 190000 ≤ x) :
    (auSchedule p2025).ticks x = 51638 * 10000 + 4500 * (x - 190000) := by
  simp [auSchedule, p2025, TaxKernel.Schedule.ofList, TaxKernel.Schedule.ticks, TaxKernel.bandsTicks, TaxKernel.pos]; omega

/-! ## LITO (ITAA 1997 s. 61-115) -/

/-- The offset in ticks before rounding (exact statutory amounts). -/
def litoTicks (ti : Int) : Int :=
  if ti ≤ 3750000 then 700000000
  else if ti ≤ 4500000 then 700000000 - 500 * (ti - 3750000)
  else 325000000 - 150 * (ti - 4500000)

/-- The three items join up: no step at $37,500 or $45,000 ($700 - 5 % x 7,500 = $325). -/
theorem lito_continuous_items : litoTicks 3750000 = 700000000 ∧ litoTicks 4500000 = 325000000 ∧
    700000000 - 500 * (4500000 - 3750000) = 325000000 := by decide

/-- s. 61-110(1)(b)'s ceiling $66,667 is where item 3 reaches nil (within half a cent): no notch at the limit. -/
theorem lito_ceiling_is_zero_crossing :
    litoTicks 6666600 = 10000 ∧ litoTicks 6666700 = -5000 := by decide

/-- The model's rounded LITO is non-increasing in taxable income. -/
theorem lito_antitone {x y : Int} (h : x ≤ y) : litoStatute p2025 y ≤ litoStatute p2025 x := by
  simp only [litoStatute, p2025, aud, pct, ticksToCents, pos]
  by_cases a1 : y ≤ 100 * 37500 <;> by_cases a2 : y ≤ 100 * 45000 <;> by_cases a3 : y ≤ 100 * 66667 <;>
  by_cases b1 : x ≤ 100 * 37500 <;> by_cases b2 : x ≤ 100 * 45000 <;> by_cases b3 : x ≤ 100 * 66667 <;>
  simp only [a1, a2, a3, b1, b2, b3, ite_true, ite_false] <;> omega

/-! ## Medicare levy (MLA ss. 6, 7) -/

/-- The low-income shade-in joins the full levy at the phase-in limit: at $34,027 the 10 % rule gives $680.50
and 2 % gives $680.54, so the cap is still binding; one dollar later the full 2 % applies ($680.56). -/
theorem levy_phase_in_join :
    levyStatute p2025 3402700 = 68050 ∧ levyStatute p2025 3402800 = 68056 := by decide

/-- The kernel's surcharge (min of 2 % and 10 % of the excess) is the statute's s. 7 with its separately written
phase-in limit, for every whole-dollar taxable income: the stated limit $34,027 adds nothing. -/
theorem levy_kernel_eq (d : Int) (h : 0 ≤ d) : levyS7C p2025 (100 * d) = levyStatute p2025 (100 * d) := by
  simp only [levyS7C, levyStatute, mlSurcharge, p2025, TaxKernel.Surcharge.ticks, TaxKernel.pos, aud, pct, ticksToCents]
  by_cases a1 : 100 * d ≤ 100 * 27222 <;> by_cases a2 : 100 * d ≤ 100 * 34027 <;>
  simp only [a1, a2, ite_true, ite_false] <;> omega

/-- LITO as the larger of two kernel credits equals the statute's three items, for every taxable income. -/
theorem lito_kernel_eq (x : Int) (h : 0 ≤ x) : litoC p2025 x = litoStatute p2025 x := by
  simp only [litoC, litoStatute, lito1, lito2, p2025, TaxKernel.Credit.value, TaxKernel.Credit.phaseIn,
    TaxKernel.Credit.taper, TaxKernel.Taper.amount, TaxKernel.Taper.reduction, TaxKernel.divR, TaxKernel.pos,
    aud, pct, ticksToCents, pos]
  by_cases a1 : x ≤ 100 * 37500 <;> by_cases a2 : x ≤ 100 * 45000 <;> by_cases a3 : x ≤ 100 * 66667 <;>
  by_cases a4 : x > 100 * 66667 <;>
  simp only [a1, a2, a3, a4, ite_true, ite_false] <;> omega

/-- The phase-in limit is the threshold x 1.25 rounded down, in every year modelled and in the SAPTO pair
(MLA s. 3: $27,222 / $34,027; $43,020 / $53,775; 2025-26 $28,011 / $35,013; $44,268 / $55,335): the levy has no
step at either end. -/
theorem phase_in_is_five_quarters :
    34027 = 27222 * 5 / 4 ∧ 53775 = 43020 * 5 / 4 ∧ 35013 = 28011 * 5 / 4 ∧ 55335 = 44268 * 5 / 4 ∧
    32500 = 26000 * 5 / 4 ∧ 51361 = 41089 * 5 / 4 := by decide

/-- The levy is non-decreasing and has no jump: the levy rises by at most 10 % of the increase (plus a cent of rounding), on whole-dollar taxable incomes.
(On cents it would step by 4 cents at $34,027.00 -> $34,027.01: the 10 % cap stops half a dollar before the lines meet.) -/
theorem levy_lipschitz {x y : Int} (h : x ≤ y) (h0 : 0 ≤ x) (hx : x % 100 = 0) (hy : y % 100 = 0) :
    0 ≤ levyStatute p2025 y - levyStatute p2025 x ∧ levyStatute p2025 y - levyStatute p2025 x ≤ (y - x) / 10 + 1 := by
  simp only [levyStatute, p2025, aud, pct, ticksToCents]
  by_cases a1 : y ≤ 100 * 27222 <;> by_cases a2 : y ≤ 100 * 34027 <;>
  by_cases b1 : x ≤ 100 * 27222 <;> by_cases b2 : x ≤ 100 * 34027 <;>
  simp only [a1, a2, b1, b2, ite_true, ite_false] <;> omega

/-! ## MLS: the kernel's notch theorem -/

open TaxKernel in
/-- No glide zone: one dollar above the singles tier 1 threshold ($97,000) costs 1 % of $97,001 = $970.01 (ticks
= dollars x bp). The kernel theorem `Surcharge.exempt_notch`, instantiated. -/
theorem mls_notch : (mlsTier1 p2025).ticks 97001 - (mlsTier1 p2025).ticks 97000 = 100 * 97001 := by
  have := Surcharge.exempt_notch (mlsTier1 p2025) (by decide) (by decide)
  simpa [mlsTier1, p2025] using this

open TaxKernel in
/-- The Medicare levy, by contrast, has a glide zone: no notch at the threshold (kernel `glide_no_notch`). -/
theorem levy_no_notch : (mlSurcharge p2025).ticks 27223 - (mlSurcharge p2025).ticks 27222 ≤ 1000 :=
  Surcharge.glide_no_notch _ (by decide) (by decide)

end AuTax
