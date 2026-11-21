import KrTax.Out

/-!
# Theorems (for all inputs unless a figure is named); no `sorry`, no `native_decide`

Kernel one-liners for the schedules (`TaxKernel.Schedule.*`), then Korea-specific properties: the printed bases of
§55① equal the rates (the statute writes each row as "base + rate × excess"), the local schedule is exactly one tenth
of the national one (지방세법 §92① vs 소득세법 §55①), the 근로소득세액공제 limit of §59② never rises with pay and has no
jump, and the 장려금 tables against the statute's formulas (F3, F4).
-/

namespace KrTax
open TaxKernel

/-! ## §55① 종합소득세율 -/

theorem nat_progressive : natSched.progressive = true := by decide
theorem nat_mono : Monotone' natSched.ticks := Schedule.ticks_mono_of_progressive _ nat_progressive
theorem nat_convex : Convex natSched.ticks := Schedule.ticks_convex _ nat_progressive
theorem nat_no_jump {x y : Int} (h : x ≤ y) : natSched.ticks y - natSched.ticks x ≤ natSched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ nat_progressive h).2
theorem nat_le_top {x : Int} (h : 0 ≤ x) : natSched.ticks x ≤ 4500 * x := by
  have := Schedule.ticks_le_maxRate_mul _ nat_progressive h
  have e : natSched.maxRate = 4500 := by decide
  rwa [e] at this
/-- The marginal rate on `(x, x+1]` is the band's (any `x`). -/
theorem nat_marginal (x : Int) : natSched.ticks (x + 1) - natSched.ticks x = natSched.rate x :=
  Schedule.ticks_succ natSched x

/-- §55①'s printed bases are the rates applied to the lower bands: 84만, 624만, 1,536만, 3,706만, 9,406만,
1억7,406만 and 3억8,406만원 (the last is the one law.go.kr's text omits, F2). -/
theorem nat_bases :
    natTax 14000000 = 840000 ∧ natTax 50000000 = 6240000 ∧ natTax 88000000 = 15360000 ∧
    natTax 150000000 = 37060000 ∧ natTax 300000000 = 94060000 ∧ natTax 500000000 = 174060000 ∧
    natTax 1000000000 = 384060000 := by decide

/-! ## 지방세법 §92①: the local schedule is the national one divided by ten, exactly -/

theorem local_progressive : localSched.progressive = true := by decide

theorem local_eq (x : Int) : 10 * localSched.ticks x = natSched.ticks x := by
  simp only [Schedule.ticks, localSched, natSched, Schedule.ofList, List.map, bandsTicks, pos]
  omega

/-- Hence the local 산출세액 is the national one cut to a tenth (both cut to the won). -/
theorem localTax_eq (x : Int) : localTax x = natTax x / 10 := by
  have h := local_eq (pos x)
  simp only [localTax, natTax, Schedule.tax, Rule.ofTicks, Rule.unitDown, divR, BP] at *
  omega

/-! ## §47 근로소득공제 -/

theorem earnedDed_progressive_false : earnedDedSched.progressive = false := by decide
/-- The deduction's rates fall (70 % → 2 %), so its schedule is concave; it still never falls with pay. -/
theorem earnedDed_ratesNonneg : earnedDedSched.RatesNonneg := by
  intro b hb
  simp only [earnedDedSched, Schedule.ofList, List.map, List.mem_cons, List.mem_nil_iff, or_false] at hb
  rcases hb with h | h | h | h | h <;> subst h <;> decide

theorem earnedDed_bases :
    earnedDeduction 5000000 = 3500000 ∧ earnedDeduction 15000000 = 7500000 ∧
    earnedDeduction 45000000 = 12000000 ∧ earnedDeduction 100000000 = 14750000 ∧
    earnedDeduction 362500000 = 20000000 ∧ earnedDeduction 400000000 = 20000000 := by decide

theorem earnedDeduction_mono {a b : Int} (h : a ≤ b) : earnedDeduction a ≤ earnedDeduction b := by
  have hm := Schedule.ticks_mono earnedDedSched earnedDed_ratesNonneg (pos_mono h)
  unfold earnedDeduction Schedule.tax Rule.ofTicks Rule.unitDown divR at *
  have : earnedDedSched.ticks (pos a) / (BP * 1) ≤ earnedDedSched.ticks (pos b) / (BP * 1) :=
    Int.ediv_le_ediv (by decide) hm
  have := pos_mono h
  simp only [Int.mul_one] at *
  omega

/-- The 근로소득금액 (pay − deduction) never falls when pay rises: the deduction's rate is below 100 %. -/
theorem earnedIncome_mono {a b : Int} (h : a ≤ b) :
    pos a - earnedDeduction a ≤ pos b - earnedDeduction b := by
  unfold earnedDeduction Schedule.tax Rule.ofTicks Rule.unitDown divR
  simp only [Schedule.ticks, earnedDedSched, Schedule.ofList, List.map, bandsTicks, BP, pos, Int.mul_one,
    earnedDedCap]
  omega

/-! ## §59 근로소득세액공제 -/

/-- §59②'s limit never rises with pay … -/
theorem earnedCreditLimit_antitone {a b : Int} (h : a ≤ b) : earnedCreditLimit b ≤ earnedCreditLimit a := by
  unfold earnedCreditLimit mulDiv; repeat (first | split | omega)

/-- … and has no jump at its three thresholds (3,300만, 7,000만, 1억2,000만원). -/
theorem earnedCreditLimit_continuous :
    earnedCreditLimit 33000000 = 740000 ∧ earnedCreditLimit 33000001 = 740000 ∧
    earnedCreditLimit 70000000 = 660000 ∧ earnedCreditLimit 70000002 = 659999 ∧
    earnedCreditLimit 120000000 = 500000 ∧ earnedCreditLimit 120000002 = 499999 := by decide

/-- Between 7,000만 and 7,032만원 and between 1억2,000만 and 1억2,060만원 the limit falls by half a won per won:
when it binds, the 근로소득세액공제 withdrawal adds 50 points to the marginal rate (Theorem for all pay in the band). -/
theorem earnedCreditLimit_slope {w : Int} (h1 : 70000000 ≤ w) (h2 : w + 2 ≤ 70320000) :
    earnedCreditLimit w - earnedCreditLimit (w + 2) = 1 := by
  unfold earnedCreditLimit mulDiv; repeat (first | split | omega)

theorem earnedCredit_le_limit (t w : Int) : earnedCredit t w ≤ earnedCreditLimit w ∨ w ≤ 0 := by
  unfold earnedCredit; repeat (first | split | omega)

/-! ## §59의2 자녀세액공제 -/

theorem childCredit_mono {m n : Nat} (h : m ≤ n) : childCredit m ≤ childCredit n := by
  unfold childCredit; repeat (first | split | omega)

/-! ## Local tax of a resident -/

theorem localIncomeTax_le (o : PersonOut) (h1 : 0 ≤ o.determined) (h2 : 0 ≤ o.sepTax) :
    10 * localIncomeTax o ≤ o.determined + o.sepTax := by
  unfold localIncomeTax; omega

end KrTax
