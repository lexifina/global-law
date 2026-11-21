import HuTax.Tests

/-!
# Hungary: kernel theorems instantiated, and the properties the statute builds in

* The 15 % rate as a kernel `Schedule` (`Schedule.flat`): progressive, monotone, convex, no jump, marginal rate 15 %.
* The family allowance table is the kernel's `perChildByCount` (§ 29/A (2): every child gets the amount for the
  family's size) and the spill into TB is the kernel's `spillAllowance`.
* `famBurden_closed_form`: for an employee, tax + TB − family contribution allowance is exactly
  `max 0 (33.5 % × wage − 15 % × frame)` (in ticks): the family allowance acts as a non-wastable credit of 15 % of the
  frame against the combined 33.5 % levy, so there is a band of zero burden (`famBurden_zero_band`) and no cliff.
* `youth_no_notch`: the under-25 allowance never makes taxable income jump (0 or 1 more forint per forint).
* Concrete households by `decide`: the age-25 step, the 667 % gross-up (finding F2), and the leads of FINDINGS.md.
-/

namespace HuTax
open TaxKernel

/-! ## The rate schedule -/
def huSched : Schedule := Schedule.flat pitRate
theorem huSched_progressive : huSched.progressive = true := by decide
theorem huSched_mono : Monotone' huSched.ticks := Schedule.ticks_mono_of_progressive _ huSched_progressive
theorem huSched_convex : Convex huSched.ticks := Schedule.ticks_convex _ huSched_progressive
theorem huSched_no_jump {x y : Int} (h : x ≤ y) : huSched.ticks y - huSched.ticks x ≤ huSched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ huSched_progressive h).2
theorem huSched_le_top {x : Int} (h : 0 ≤ x) : huSched.ticks x ≤ 1500 * x := by
  have := Schedule.ticks_le_maxRate_mul _ huSched_progressive h
  have e : huSched.maxRate = 1500 := by decide
  rwa [e] at this
theorem huSched_split_ok (a b : Int) : splitting huSched.ticks a b ≤ separate huSched.ticks a b :=
  splitting_le_separate _ huSched_convex huSched_mono a b
/-- The marginal rate is 15 % on every forint of a non-negative base (kernel `Schedule.ticks_succ`). -/
theorem huSched_marginal {x : Int} (hx : 0 ≤ x) : huSched.ticks (x + 1) - huSched.ticks x = 1500 := by
  rw [Schedule.ticks_succ]
  simp [Schedule.rate, huSched, Schedule.flat, bandsRate, pitRate, hx]

/-- The model's rounding is monotone (kernel `divR_mono`). -/
theorem pct_mono {r a b : Int} (hr : 0 ≤ r) (h : a ≤ b) : pct r a ≤ pct r b := by
  unfold pct
  exact divR_mono .halfUp BP (by decide) (by simp) (Int.mul_le_mul_of_nonneg_left h hr)

/-! ## Family allowance = kernel parts -/
/-- § 29/A (2) is the kernel's "every child gets the amount for the family's size" scale. -/
theorem famMonth_kernel (tbl : List Int) (n : Nat) : famMonth tbl 0 n n 0 = perChildByCount tbl n := by
  unfold famMonth famRate perChildByCount
  rw [Nat.max_self]
  split <;> simp_all [Int.mul_comm]

/-- The single earner's family allowance: taxable income and the 15 % value of the unused part are the kernel's
`spillAllowance` (before the TB cap of Tbj. § 34 (3)). -/
theorem fam_spill_kernel (frame w : Int) (_hf : 0 ≤ frame) (hw : 0 ≤ w) :
    (spillAllowance frame w 1500).1 = w - min w frame ∧
    (spillAllowance frame w 1500).2 = 1500 * (frame - min w frame) / BP := by
  have e1 : pos (w - frame) = w - min w frame := by
    unfold pos; simp only [Int.min_def, Int.max_def]; split <;> (try split) <;> omega
  have e2 : pos (frame - pos w) = frame - min w frame := by
    unfold pos; simp only [Int.min_def, Int.max_def]; split <;> (try split) <;> (try split) <;> omega
  exact ⟨by simp only [spillAllowance, taxableAfter, e1], by simp only [spillAllowance, unusedAllowance, e2]⟩

/-- Tax + TB − family contribution allowance of an employee with wage `w` and family frame `K`, in ticks (before
rounding): 15 % of the base left after the frame, plus 18.5 % TB, less the contribution allowance (15 % of the unused
frame, at most the TB). -/
def famBurden (K w : Int) : Int := 1500 * pos (w - K) + 1850 * w - min (1850 * w) (1500 * pos (K - w))

/-- The closed form: `max 0 (3350 w − 1500 K)`. The frame is a credit of 15 % × K against a 33.5 % levy; nothing of
it is lost while the wage is at least 1500 K / 3350, and the marginal rate is either 0 or 33.5 %. -/
theorem famBurden_closed_form {K w : Int} (hK : 0 ≤ K) (hw : 0 ≤ w) :
    famBurden K w = max 0 (3350 * w - 1500 * K) := by
  unfold famBurden pos
  simp only [Int.min_def, Int.max_def]
  split <;> (try split) <;> (try split) <;> (try split) <;> omega

theorem famBurden_zero_band {K w : Int} (hK : 0 ≤ K) (hw : 0 ≤ w) (h : 3350 * w ≤ 1500 * K) :
    famBurden K w = 0 := by
  rw [famBurden_closed_form hK hw]; omega

/-- No cliff: one more forint of wage never raises the burden by more than 33.5 % of it. -/
theorem famBurden_lipschitz {K w : Int} (hK : 0 ≤ K) (hw : 0 ≤ w) :
    0 ≤ famBurden K (w + 1) - famBurden K w ∧ famBurden K (w + 1) - famBurden K w ≤ 3350 := by
  rw [famBurden_closed_form hK hw, famBurden_closed_form hK (by omega)]
  omega

/-! ## Under 25 -/
/-- § 29/F: the base left after the under-25 allowance rises by 0 or 1 per forint: a kink, never a notch. -/
theorem youth_no_notch (months : Nat) {q : Int} (hq : 0 ≤ q) :
    0 ≤ (q + 1 - youthAllowance months (q + 1)) - (q - youthAllowance months q) ∧
    (q + 1 - youthAllowance months (q + 1)) - (q - youthAllowance months q) ≤ 1 := by
  unfold youthAllowance pos
  have hm : (0 : Int) ≤ (months : Int) * youthCapMonthly := by unfold youthCapMonthly; omega
  simp only [Int.min_def, Int.max_def]
  split <;> (try split) <;> (try split) <;> (try split) <;> omega

/-- The age step: the same 7 million forint wage, all accounted to months before the 25th birthday (December
birthday) or after it (aged 26): 1 050 000 forint of tax. -/
theorem age25_step :
    pct pitRate (stage1 { age := 25, birthMonth := 12, wages := 7000000 }).rest = 0 ∧
    pct pitRate (stage1 { age := 26, wages := 7000000 }).rest = 1050000 := by decide

/-! ## Finding F2: the 667 % gross-up of Szja tv. § 29/B (6) -/
/-- 667 % is not 1/15 %: 0.15 × 6.67 = 1.0005, so every forint of contribution allowance taken during the year
costs 1.0005 forint of tax in the return. -/
theorem grossUp_excess (J : Int) : 1500 * (66700 * J) - BP * (BP * J) = 50000 * J := by
  unfold BP; omega
/-- The Kedves family of NAV 73: the frame left is 7 016 050 (667 %), not 7 016 667 (exact 1/15 %): 617 forint of
frame, 93 forint of tax. -/
theorem kedves_667_cost :
    frameAfterInYearCredit 8250000 185000 = 7016050 ∧
    8250000 - divR .halfUp (185000 * BP) 1500 = 7016667 ∧ pct pitRate 617 = 93 := by decide

end HuTax
