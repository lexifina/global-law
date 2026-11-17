import Std

/-!
# The premium tax credit and the self-employed health insurance deduction: a circular rule

Rules, read from the text (`python3 -I tools/hunt/sec.py 36B`, `162 l`, `280C g`):

* §36B(b)(2): premium assistance amount = lesser of (A) the enrollment premium and (B) the benchmark (second lowest
  cost silver plan) premium less the applicable percentage of household income. Annual amounts here (12 equal months).
* §36B(b)(3)(A)(i) as indexed by Rev. Proc. 2025-25 §3.01 (2026): 2.10 / 3.14-4.19 / 4.19-6.60 / 6.60-8.44 /
  8.44-9.96 / 9.96 percent, tiers at 133, 150, 200, 250, 300, 400 percent of the poverty line, linear inside a tier
  (Treas. Reg. §1.36B-3(g)). §36B(b)(3)(A)(iii) (2025): 0 / 0-2 / 2-4 / 4-6 / 6-8.5 / 8.5, tiers 150, 200, 250, 300, 400.
* §36B(c)(1)(A): applicable taxpayer iff household income is at least 100% and not over 400% of the poverty line;
  §36B(c)(1)(E): no 400% cap for 2021-2025.
* §36B(d)(2): household income = modified AGI, so it is computed after the §162(l) deduction.
* §36B(f)(2): from 2026 the whole excess advance payment is repaid (the limitation in former (f)(2)(B) is gone,
  Pub. L. 119-21 §71305). This file models taxpayers without advance payments, the case where it does not matter.
* §162(l)(1): deduction for the amount paid for the insurance; (2)(A) not over earned income (assumed not binding:
  earned income at least the premium).
* §280C(g): no deduction for the portion of the premiums equal to the credit determined under §36B.

So a lawful pair (deduction d, credit C) must satisfy `C = credit(I0 - d)` and `d = Q - C`, where `I0` is household
income before the deduction for these premiums and `Q` the premium: the fixed points of `g d = Q - credit (I0 - d)`.
Rev. Proc. 2014-41 §5.01 (iterative) accepts a pair once successive changes are under $1, so `consistent` below
allows $1 either way (whole dollars; the credit's required contribution is rounded down to a dollar).

Poverty line (single person): 2026 coverage $15,650 (2025 HHS guideline, §36B(d)(3)(B)); 2025 coverage $15,060
(Form 8962 instructions 2025, Table 1-1).

Encoding of the applicable percentage: `A26 h` = applicable percentage in basis points x S x P with S = 226,100
(divisible by every tier width in percentage points) and P = 15,650, so that the required contribution is
`h * A26 h / K26` with `K26 = 10,000 x S x P`, exactly the linear scale of Reg. §1.36B-3(g), rounded down.
-/

namespace Legal.USTax.Hunt.Hunt2.Circular

/-! ## Rules: 2026, one person (P = 15,650) -/

/-- applicable percentage x 10,000 x S x P / 10,000 (see header); tiers of Rev. Proc. 2025-25 §3.01 -/
def A26 (h : Int) : Int :=
  if 100 * h < 133 * 15650 then 743077650000
  else if 100 * h < 150 * 15650 then -1795666915000 + 139650000 * h
  else if 100 * h < 200 * 15650 then -1075693360000 + 108980200 * h
  else if 100 * h < 250 * 15650 then -268923340000 + 83204800 * h
  else if 100 * h < 300 * 15650 then 297231060000 + 68734400 * h
  else 3524311140000

def K26 : Int := 35384650000000

/-- required contribution, §36B(b)(2)(B)(ii) (annual), rounded down -/
def contrib26 (h : Int) : Int := h * A26 h / K26

/-- §36B(b)(2), §36B(c)(1)(A) (2026: 100% to 400%) -/
def cr26 (B Q h : Int) : Int :=
  if h < 15650 then 0
  else if 100 * h > 400 * 15650 then 0
  else min Q (max 0 (B - contrib26 h))

/-- deduction the statute leaves when the return claims `d` (§162(l)(1) less §280C(g)) -/
def g26 (B Q I0 d : Int) : Int := Q - cr26 B Q (I0 - d)

/-- a lawful pair to within the $1 of Rev. Proc. 2014-41 §5.01 Step 6 -/
def consistent26 (B Q I0 d : Int) : Prop :=
  0 ≤ d ∧ d ≤ Q ∧ d - g26 B Q I0 d ≤ 1 ∧ g26 B Q I0 d - d ≤ 1

/-! ## Rules: 2025, one person (P = 15,060), §36B(b)(3)(A)(iii), no 400% cap -/

def A25 (h : Int) : Int :=
  if 100 * h < 150 * 15060 then 0
  else if 100 * h < 300 * 15060 then -2710800000 + 120000 * h
  else if 100 * h < 400 * 15060 then -677700000 + 75000 * h
  else 3840300000

def K25 : Int := 45180000000

def contrib25 (h : Int) : Int := h * A25 h / K25

def cr25 (B Q h : Int) : Int :=
  if h < 15060 then 0 else min Q (max 0 (B - contrib25 h))

def g25 (B Q I0 d : Int) : Int := Q - cr25 B Q (I0 - d)

def consistent25 (B Q I0 d : Int) : Prop :=
  0 ≤ d ∧ d ≤ Q ∧ d - g25 B Q I0 d ≤ 1 ∧ g25 B Q I0 d - d ≤ 1

/-! ## Monotonicity of the schedule -/

theorem A26_mono (h1 h2 : Int) (hp : 15650 ≤ h1) (hle : h1 ≤ h2) : A26 h1 ≤ A26 h2 := by
  unfold A26
  repeat' split
  all_goals omega

theorem A26_nonneg (h : Int) (hp : 15650 ≤ h) : 0 ≤ A26 h := by
  unfold A26
  repeat' split
  all_goals omega

theorem contrib26_mono (h1 h2 : Int) (hp : 15650 ≤ h1) (hle : h1 ≤ h2) :
    contrib26 h1 ≤ contrib26 h2 := by
  unfold contrib26
  have hm : h1 * A26 h1 ≤ h2 * A26 h2 :=
    Int.mul_le_mul hle (A26_mono h1 h2 hp hle) (A26_nonneg h1 hp) (by omega)
  exact Int.ediv_le_ediv (by decide) hm

/-- In the credit-bearing region the credit never rises with income (2026). -/
theorem cr26_antitone (B Q h1 h2 : Int) (hq : 0 ≤ Q) (hp : 15650 ≤ h1) (hle : h1 ≤ h2) :
    cr26 B Q h2 ≤ cr26 B Q h1 := by
  have hc := contrib26_mono h1 h2 hp hle
  unfold cr26
  repeat' split
  all_goals omega

theorem A25_mono (h1 h2 : Int) (hp : 15060 ≤ h1) (hle : h1 ≤ h2) : A25 h1 ≤ A25 h2 := by
  unfold A25
  repeat' split
  all_goals omega

theorem A25_nonneg (h : Int) (hp : 15060 ≤ h) : 0 ≤ A25 h := by
  unfold A25
  repeat' split
  all_goals omega

theorem cr25_antitone (B Q h1 h2 : Int) (hq : 0 ≤ Q) (hp : 15060 ≤ h1) (hle : h1 ≤ h2) :
    cr25 B Q h2 ≤ cr25 B Q h1 := by
  have hm : h1 * A25 h1 ≤ h2 * A25 h2 :=
    Int.mul_le_mul hle (A25_mono h1 h2 hp hle) (A25_nonneg h1 hp) (by omega)
  have hc : contrib25 h1 ≤ contrib25 h2 := Int.ediv_le_ediv (by decide) hm
  unfold cr25
  repeat' split
  all_goals omega

/-! ## Uniqueness: at most one credit-bearing answer, and the only other answer is "no credit, full deduction" -/

/-- 2026: two exact fixed points whose household income is at least the poverty line coincide. -/
theorem fp26_unique_above_floor (B Q I0 d1 d2 : Int) (hq : 0 ≤ Q)
    (f1 : d1 = g26 B Q I0 d1) (f2 : d2 = g26 B Q I0 d2)
    (p1 : 15650 ≤ I0 - d1) (p2 : 15650 ≤ I0 - d2) : d1 = d2 := by
  unfold g26 at f1 f2
  rcases Int.le_total d1 d2 with h | h
  · have := cr26_antitone B Q (I0 - d2) (I0 - d1) hq p2 (by omega)
    omega
  · have := cr26_antitone B Q (I0 - d1) (I0 - d2) hq p1 (by omega)
    omega

/-- 2026: a fixed point below the poverty line is the full deduction with no credit. -/
theorem fp26_below_floor (B Q I0 d : Int) (f : d = g26 B Q I0 d) (p : I0 - d < 15650) : d = Q := by
  unfold g26 cr26 at f
  simp only [p, ite_true] at f
  omega

theorem fp25_unique_above_floor (B Q I0 d1 d2 : Int) (hq : 0 ≤ Q)
    (f1 : d1 = g25 B Q I0 d1) (f2 : d2 = g25 B Q I0 d2)
    (p1 : 15060 ≤ I0 - d1) (p2 : 15060 ≤ I0 - d2) : d1 = d2 := by
  unfold g25 at f1 f2
  rcases Int.le_total d1 d2 with h | h
  · have := cr25_antitone B Q (I0 - d2) (I0 - d1) hq p2 (by omega)
    omega
  · have := cr25_antitone B Q (I0 - d1) (I0 - d2) hq p1 (by omega)
    omega

/-! ## Flat tiers in closed form -/

theorem contrib26_low (h : Int) (h1 : 100 * h < 133 * 15650) : contrib26 h = h * 210 / 10000 := by
  unfold contrib26 A26 K26
  simp only [h1, ite_true]
  omega

theorem contrib26_top (h : Int) (h1 : 300 * 15650 ≤ 100 * h) : contrib26 h = h * 996 / 10000 := by
  unfold contrib26 A26 K26
  simp only [show ¬ (100 * h < 133 * 15650) by omega, show ¬ (100 * h < 150 * 15650) by omega,
    show ¬ (100 * h < 200 * 15650) by omega, show ¬ (100 * h < 250 * 15650) by omega,
    show ¬ (100 * h < 300 * 15650) by omega, ite_false]
  omega

theorem contrib25_low (h : Int) (h1 : 100 * h < 150 * 15060) : contrib25 h = 0 := by
  unfold contrib25 A25 K25
  simp only [h1, ite_true]
  omega

/-! ## Result 1 (2026 cliff): a band of income with no lawful answer at all

Hypotheses: premium at least the benchmark (`B ≤ Q`), all candidate household incomes in the 300-400% tier.
For a 2026 single person this is `I0` from 68,840 to `Q + 62,599`: for a $14,000 benchmark plan, $7,760 of income
(440% to 489% of the poverty line) where no deduction/credit pair satisfies §36B, §162(l) and §280C(g) together. -/
theorem cliff26_no_answer (B Q I0 d : Int) (hB0 : 0 ≤ B) (hBQ : B ≤ Q)
    (hlo : 46950 ≤ I0 - Q) (hup : I0 - Q ≤ 62599) (hband : 68840 ≤ I0 - Q + B) :
    ¬ consistent26 B Q I0 d := by
  intro ⟨d0, dq, c1, c2⟩
  unfold g26 cr26 at c1 c2
  by_cases hp : 100 * (I0 - d) > 400 * 15650
  · simp only [show ¬ (I0 - d < 15650) by omega, hp, ite_true, ite_false] at c1 c2
    omega
  · simp only [show ¬ (I0 - d < 15650) by omega, hp, ite_false] at c1 c2
    rw [contrib26_top (I0 - d) (by omega)] at c1 c2
    omega

/-- The same band, numerically: single person, $14,000 benchmark plan. -/
theorem cliff26_no_answer_14000 (I0 d : Int) (h1 : 68840 ≤ I0) (h2 : I0 ≤ 76599) :
    ¬ consistent26 14000 14000 I0 d :=
  cliff26_no_answer 14000 14000 I0 d (by decide) (by decide) (by omega) (by omega) (by omega)

/-- Result 1b: in that band the Rev. Proc. 2014-41 iteration (start from the full premium) is a 2-cycle,
so its Step 6 test (changes under $1) is never met; its alternative method ends at deduction `g Q` with no credit, while deduction
`I0 - 62,601` with no credit is admissible under Pub. 974 (sum at most the premium) and larger. -/
theorem cliff26_two_cycle (B Q I0 : Int) (hB0 : 0 ≤ B) (hBQ : B ≤ Q)
    (hlo : 46950 ≤ I0 - Q) (hup : I0 - Q ≤ 62599) (hband : 68840 ≤ I0 - Q + B) :
    g26 B Q I0 (g26 B Q I0 Q) = Q ∧ g26 B Q I0 Q + 6 ≤ Q ∧
    cr26 B Q (I0 - g26 B Q I0 Q) = 0 ∧ g26 B Q I0 Q + 4 ≤ I0 - 62601 := by
  have e1 : g26 B Q I0 Q = Q - min Q (max 0 (B - (I0 - Q) * 996 / 10000)) := by
    unfold g26 cr26
    simp only [show ¬ (I0 - Q < 15650) by omega, show ¬ (100 * (I0 - Q) > 400 * 15650) by omega, ite_false]
    rw [contrib26_top (I0 - Q) (by omega)]
  have e2 : ∀ x, 100 * (I0 - x) > 400 * 15650 → g26 B Q I0 x = Q := by
    intro x hx
    unfold g26 cr26
    simp only [show ¬ (I0 - x < 15650) by omega, hx, ite_true, ite_false]
    omega
  have hx : 100 * (I0 - g26 B Q I0 Q) > 400 * 15650 := by rw [e1]; omega
  refine ⟨e2 _ hx, by rw [e1]; omega, ?_, by rw [e1]; omega⟩
  unfold cr26
  simp only [show ¬ (I0 - g26 B Q I0 Q < 15650) by omega, hx, ite_true, ite_false]

/-! ## Result 2 (poverty-line floor, 2025 and 2026): two lawful answers

With household income before the deduction between the poverty line and the poverty line plus the premium, both
"full deduction, no credit" (household income then falls below 100%) and "credit, deduction reduced by it" are
lawful. Pub. 974 (2025), Iterative and Simplified methods, Step 2: "If you are not eligible to take the PTC, stop
here" after Step 1 took the full deduction, so it reaches only the first. -/
theorem floor26_two_answers (Q I0 : Int) (hq : 440 ≤ Q) (h1 : 15980 ≤ I0) (h2 : I0 ≤ 20800)
    (hA : I0 - Q < 15650) :
    consistent26 Q Q I0 Q ∧ cr26 Q Q (I0 - Q) = 0 ∧
    consistent26 Q Q I0 (210 * I0 / 10210) ∧ Q - 440 ≤ cr26 Q Q (I0 - 210 * I0 / 10210) := by
  have eA : cr26 Q Q (I0 - Q) = 0 := by
    unfold cr26; simp only [hA, ite_true]
  have eB : cr26 Q Q (I0 - 210 * I0 / 10210) = Q - (I0 - 210 * I0 / 10210) * 210 / 10000 := by
    unfold cr26
    simp only [show ¬ (I0 - 210 * I0 / 10210 < 15650) by omega,
      show ¬ (100 * (I0 - 210 * I0 / 10210) > 400 * 15650) by omega, ite_false]
    rw [contrib26_low _ (by omega)]
    omega
  refine ⟨⟨by omega, Int.le_refl _, ?_, ?_⟩, eA, ⟨by omega, by omega, ?_, ?_⟩, by rw [eB]; omega⟩
  all_goals unfold g26
  · rw [eA]; omega
  · rw [eA]; omega
  · rw [eB]; omega
  · rw [eB]; omega

/-- Same, plan cheaper than the benchmark (e.g. bronze): the credit pays the whole premium and the deduction is 0. -/
theorem floor26_two_answers_cheap (B Q I0 : Int) (hq : 0 ≤ Q) (hQB : Q + 437 ≤ B)
    (h1 : 15650 ≤ I0) (h2 : I0 ≤ 20800) (hA : I0 - Q < 15650) :
    consistent26 B Q I0 Q ∧ cr26 B Q (I0 - Q) = 0 ∧ consistent26 B Q I0 0 ∧ cr26 B Q I0 = Q := by
  have eA : cr26 B Q (I0 - Q) = 0 := by
    unfold cr26; simp only [hA, ite_true]
  have eB : cr26 B Q I0 = Q := by
    unfold cr26
    simp only [show ¬ (I0 < 15650) by omega, show ¬ (100 * I0 > 400 * 15650) by omega, ite_false]
    rw [contrib26_low _ (by omega)]
    omega
  have eB' : cr26 B Q (I0 - 0) = Q := by simpa using eB
  refine ⟨⟨hq, Int.le_refl _, ?_, ?_⟩, eA, ⟨Int.le_refl _, hq, ?_, ?_⟩, eB⟩
  all_goals unfold g26
  · rw [eA]; omega
  · rw [eA]; omega
  · rw [eB']; omega
  · rw [eB']; omega

/-- 2025: below 150% the applicable percentage is 0, so the credit-bearing answer is "credit = premium,
deduction 0" whenever the premium does not exceed the benchmark. -/
theorem floor25_two_answers (B Q I0 : Int) (hq : 0 ≤ Q) (hQB : Q ≤ B)
    (h1 : 15060 ≤ I0) (h2 : 100 * I0 < 150 * 15060) (hA : I0 - Q < 15060) :
    consistent25 B Q I0 Q ∧ cr25 B Q (I0 - Q) = 0 ∧ consistent25 B Q I0 0 ∧ cr25 B Q I0 = Q := by
  have eA : cr25 B Q (I0 - Q) = 0 := by
    unfold cr25; simp only [hA, ite_true]
  have eB : cr25 B Q I0 = Q := by
    unfold cr25
    simp only [show ¬ (I0 < 15060) by omega, ite_false]
    rw [contrib25_low _ h2]
    omega
  have eB' : cr25 B Q (I0 - 0) = Q := by simpa using eB
  refine ⟨⟨hq, Int.le_refl _, ?_, ?_⟩, eA, ⟨Int.le_refl _, hq, ?_, ?_⟩, eB⟩
  all_goals unfold g25
  · rw [eA]; omega
  · rw [eA]; omega
  · rw [eB']; omega
  · rw [eB']; omega

/-! ## Result 3: where the schedule is flat the iteration contracts (factor about 1/10)

In the 300-400% tier, two candidate deductions `d1, d2` lead to deductions differing by at most a tenth of their
gap plus $1 of rounding: the Rev. Proc. iteration converges there unless it crosses the 400% line. -/
theorem contract26_top (B Q I0 d1 d2 : Int) (hBQ : B ≤ Q)
    (a1 : 300 * 15650 ≤ 100 * (I0 - d1)) (a2 : 100 * (I0 - d1) ≤ 400 * 15650)
    (b1 : 300 * 15650 ≤ 100 * (I0 - d2)) (b2 : 100 * (I0 - d2) ≤ 400 * 15650) (hle : d1 ≤ d2) :
    g26 B Q I0 d1 - g26 B Q I0 d2 ≤ (d2 - d1) / 10 + 1 ∧ g26 B Q I0 d2 ≤ g26 B Q I0 d1 := by
  unfold g26 cr26
  simp only [show ¬ (I0 - d1 < 15650) by omega, show ¬ (I0 - d2 < 15650) by omega,
    show ¬ (100 * (I0 - d1) > 400 * 15650) by omega, show ¬ (100 * (I0 - d2) > 400 * 15650) by omega, ite_false]
  rw [contrib26_top _ a1, contrib26_top _ b1]
  omega

/-! ## Red team (RED_BRIEF T2, T5)

T2, closing the gap: add to §36B(c)(1)(A) the words "household income determined as if the deduction under
section 162(l) were not reduced under section 280C(g)" for the 100% test only (what Pub. 974 Step 2 does). Then in
the floor band only the no-credit answer is consistent, and wherever the full deduction already leaves household
income at or above the poverty line nothing changes. -/

def cr26fix (B Q I0 d : Int) : Int := if I0 - Q < 15650 then 0 else cr26 B Q (I0 - d)
def g26fix (B Q I0 d : Int) : Int := Q - cr26fix B Q I0 d
def consistent26fix (B Q I0 d : Int) : Prop :=
  0 ≤ d ∧ d ≤ Q ∧ d - g26fix B Q I0 d ≤ 1 ∧ g26fix B Q I0 d - d ≤ 1

theorem fix_kills (B Q I0 d : Int) (hA : I0 - Q < 15650) (h : consistent26fix B Q I0 d) :
    Q - 1 ≤ d ∧ cr26fix B Q I0 d = 0 := by
  have e : cr26fix B Q I0 d = 0 := by unfold cr26fix; simp only [hA, ite_true]
  obtain ⟨_, _, _, h4⟩ := h
  unfold g26fix at h4
  rw [e] at h4
  exact ⟨by omega, e⟩

theorem fix_keeps_baseline (B Q I0 d : Int) (hA : 15650 ≤ I0 - Q) :
    consistent26fix B Q I0 d ↔ consistent26 B Q I0 d := by
  have e : g26fix B Q I0 d = g26 B Q I0 d := by
    unfold g26fix g26 cr26fix; simp only [show ¬ (I0 - Q < 15650) by omega, ite_false]
  unfold consistent26fix consistent26
  rw [e]

/-- T5, conservation: a consistent pair never covers more than the premium (to the $1 tolerance), and the credit
is never negative. -/
theorem conserve26 (B Q I0 d : Int) (h : consistent26 B Q I0 d) :
    0 ≤ cr26 B Q (I0 - d) ∧ d + cr26 B Q (I0 - d) ≤ Q + 1 := by
  obtain ⟨h1, h2, h3, h4⟩ := h
  unfold g26 at h3 h4
  constructor
  · unfold cr26
    repeat' split
    all_goals omega
  · omega

/-! ## Checks (tests, not proofs) -/

#guard cr26 14000 14000 62600 = 14000 - 6234
#guard cr26 14000 14000 62601 = 0
#guard g26 14000 14000 72000 (g26 14000 14000 72000 14000) = 14000

end Legal.USTax.Hunt.Hunt2.Circular

open Legal.USTax.Hunt.Hunt2.Circular in
#print axioms cliff26_no_answer
open Legal.USTax.Hunt.Hunt2.Circular in
#print axioms cliff26_two_cycle
open Legal.USTax.Hunt.Hunt2.Circular in
#print axioms floor26_two_answers
open Legal.USTax.Hunt.Hunt2.Circular in
#print axioms floor25_two_answers
open Legal.USTax.Hunt.Hunt2.Circular in
#print axioms fp26_unique_above_floor
open Legal.USTax.Hunt.Hunt2.Circular in
#print axioms fp25_unique_above_floor
open Legal.USTax.Hunt.Hunt2.Circular in
#print axioms contract26_top
open Legal.USTax.Hunt.Hunt2.Circular in
#print axioms fix_kills
open Legal.USTax.Hunt.Hunt2.Circular in
#print axioms fix_keeps_baseline
open Legal.USTax.Hunt.Hunt2.Circular in
#print axioms conserve26
