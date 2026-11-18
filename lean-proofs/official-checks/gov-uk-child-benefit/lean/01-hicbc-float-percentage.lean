/-!
# High Income Child Benefit Charge: the percentage at £65,800, £71,400 and £71,600

ITEPA 2003 s. 681C(2): the appropriate percentage is 100 % or, if less, (ANI − L) / X %, with L = £60,000 and
X = £200 (2024-25 onwards); s. 681C(3)(b): a percentage that is not a whole number is rounded down.

GOV.UK's calculator (alphagov/smart-answers, `lib/smart_answer/calculators/child_benefit_tax_calculator.rb`, line 97)
computes `(((adjusted_net_income - lower_earnings_threshold) / difference_between_thresholds) * 100.0).floor` in
IEEE 754 binary64 (Ruby `Float`). This file models that evaluation exactly with natural numbers (round to nearest,
ties to even) and proves, by kernel computation (`decide`, no `native_decide`, no `sorry`):

* the statute gives exactly k % at ANI = £60,000 + £200 k for every k = 0 … 100;
* the binary64 evaluation gives k % for every such k except 29, 57 and 58, where it gives one less;
* hence at £65,800 with two children (2025-26) the charge is £652 by the statute and £630 as calculated.

Lean 4 core only. Check with: `lean 01-hicbc-float-percentage.lean`.
-/

namespace HicbcFloat

/-- s. 681C(2)(b) and (3)(b) for whole-pound ANI between L and L + 100 X (2024-25 onwards: L = 60,000, X = 200). -/
def statutePct (ani : Nat) : Nat := min 100 ((ani - 60000) / 200)

/-! ## IEEE 754 binary64, positive normal numbers: m · 2^e with 2^52 ≤ m < 2^53 -/

/-- Round num/den to the nearest natural number, ties to even. -/
def rne (num den : Nat) : Nat :=
  let m := num / den
  let r := num % den
  if 2 * r > den then m + 1 else if 2 * r < den then m else m + m % 2

/-- The binary64 significand of the positive rational `num/den` at exponent `e = -s` (s > 0): rne(num·2^s/den). -/
def sig (num den s : Nat) : Nat := rne (num * 2 ^ s) den

def isNormal (m : Nat) : Bool := 2 ^ 52 ≤ m && m < 2 ^ 53

/-- The scale `s` (exponent −s) at which `num/den` (0 < num/den < 2^52) is a normal binary64: the s with
2^52 ≤ num·2^s/den < 2^53, searched over s = 1 … 120. -/
def scale (num den : Nat) : Nat :=
  ((List.range 120).map (· + 1)).find? (fun s => 2 ^ 52 * den ≤ num * 2 ^ s && num * 2 ^ s < 2 ^ 53 * den) |>.getD 0

/-- The calculator's percentage for whole-pound ANI = 60,000 + 200 k, 0 < k < 100, as Ruby evaluates it:
`q = 200k.0 / 20000` (one rounding), `p = q * 100.0` (one rounding), `p.floor`.
`q = m₁ · 2^(-s₁)`; the exact product is `m₁ · 100 · 2^(-s₁)`, rounded at its own scale `s₂`; the floor of
`m₂ · 2^(-s₂)` is `m₂ / 2^s₂`. -/
def govPct (k : Nat) : Nat :=
  if k = 0 then 0 else if k ≥ 100 then 100 else          -- lines 92-95: below L → 0; at or above U → 100
  let s₁ := scale (200 * k) 20000
  let m₁ := sig (200 * k) 20000 s₁                        -- q = m₁ / 2^s₁
  let s₂ := scale (m₁ * 100) (2 ^ s₁)
  let m₂ := sig (m₁ * 100) (2 ^ s₁) s₂                    -- p = m₂ / 2^s₂
  m₂ / 2 ^ s₂                                             -- p.floor

/-- Every rounding above lands on a normal binary64 (so the model is exact for these inputs). -/
def wellFormed (k : Nat) : Bool :=
  k = 0 || k ≥ 100 ||
  (let s₁ := scale (200 * k) 20000
   let m₁ := sig (200 * k) 20000 s₁
   let s₂ := scale (m₁ * 100) (2 ^ s₁)
   isNormal m₁ && isNormal (sig (m₁ * 100) (2 ^ s₁) s₂) && s₁ > 0 && s₂ > 0)

/-- The statute: exactly k % at £60,000 + £200 k, for every k from 0 to 100. -/
theorem statute_whole_steps : ∀ k, k < 101 → statutePct (60000 + 200 * k) = k := by decide

theorem model_well_formed : ∀ k, k < 101 → wellFormed k = true := by decide

/-- The calculator agrees with the statute at every £200 step except three. -/
theorem gov_differs_exactly_at :
    (List.range 101).filter (fun k => govPct k ≠ statutePct (60000 + 200 * k)) = [29, 57, 58] := by decide

/-- £65,800: 0.29 is stored as 0.28999999999999998002…, times 100 rounds to 28.999999999999996447…, floor 28. -/
theorem at_65800 : statutePct 65800 = 29 ∧ govPct 29 = 28 := by decide
theorem at_71400 : statutePct 71400 = 57 ∧ govPct 57 = 56 := by decide
theorem at_71600 : statutePct 71600 = 58 ∧ govPct 58 = 57 := by decide

/-! ## The charge, 2025-26, two children (s. 681C(1), (3)(a))
Child benefit 2025-26: £26.05 (eldest) and £17.25 a week, 52 weeks (the Mondays 7 April 2025 … 30 March 2026):
£2,251.60, rounded down to £2,251 (s. 681C(3)(a)). -/

def cbPence (children : Nat) : Nat := 52 * (2605 + 1725 * (children - 1))

/-- The statutory charge in pounds: ⌊ ⌊total⌋ × pct / 100 ⌋. -/
def charge (children pct : Nat) : Nat := (cbPence children / 100) * pct / 100

theorem charge_65800_two_children : cbPence 2 = 225160 ∧ charge 2 (statutePct 65800) = 652 := by decide

/-- What the calculator shows at £65,800 with 28 %: ⌊ £2,251.60 × 28 % ⌋ = £630 (it does not round the total
first; see issue 02), £22 less than the statute's £652. One to four children: £379/£392, £630/£652, £881/£912,
£1,132/£1,173. -/
theorem shown_65800 :
    (cbPence 1 * 28 / 10000, cbPence 2 * 28 / 10000, cbPence 3 * 28 / 10000, cbPence 4 * 28 / 10000)
      = (379, 630, 881, 1132) ∧
    (charge 1 29, charge 2 29, charge 3 29, charge 4 29) = (392, 652, 912, 1173) := by decide

end HicbcFloat
