/-!
# Pub. 936 (2025) Table 1 against §163(h)(3)(B), (F): pooling the interest of old and new mortgages

Publication text (Pub. 936 (2025), created Oct 28, 2025, p. 13, https://www.irs.gov/pub/irs-pdf/p936.pdf), Table 1
"Worksheet To Figure Your Qualified Loan Limit and Deductible Home Mortgage Interest": line 1 average balance of
grandfathered debt; 2 average balance of home acquisition debt incurred after October 13, 1987, and prior to December
16, 2017; 3 $1,000,000; 4 larger of 1 or 3; 5 = 1 + 2; 6 smaller of 4 or 5 ("If you have no home acquisition debt
incurred after December 15, 2017, or the amount on line 6 is $750,000 ... or more, line 6 is your qualified loan
limit"); 7 average balance of home acquisition debt incurred after December 15, 2017; 8 $750,000; 9 larger of 6 or 8;
10 = 6 + 7; 11 smaller of 9 or 10 ("your qualified loan limit"); 12 total of the average balances of all mortgages;
13 total interest paid on the loans from line 12; 14 "Divide the amount on line 11 by the amount on line 12 ... (rounded
to three places)"; 15 "Multiply the amount on line 13 by the decimal amount on line 14 ... This is your deductible home
mortgage interest."

Statute: §163(h)(3)(B)(ii) "The aggregate amount treated as acquisition indebtedness for any period shall not exceed
$1,000,000"; §163(h)(3)(F)(i)(II) substitutes $750,000; (F)(i)(IV): "Subclause (II) shall not apply to any
indebtedness incurred on or before December 15, 2017, and, in applying such subclause to any indebtedness incurred
after such date, the limitation under such subclause shall be reduced (but not below zero) by the amount of any
indebtedness incurred on or before December 15, 2017, which is treated as acquisition indebtedness". So the old debt
keeps the $1,000,000 limit in full and the whole excess sits in the new debt; qualified residence interest
(§163(h)(3)(A)) is the interest on the acquisition indebtedness, so the old loan's interest is fully deductible and
only part of the new loan's interest is.

Model: no grandfathered debt (line 1 = 0); old (pre-12/16/2017) average balance P with 0 < P ≤ $1,000,000 and interest
IP; new average balance N > 0 with interest IN. Allowed new debt a = min(N, max(0, 750,000 − P)). The line 14 rounding
(three places) is ignored.
-/

namespace TaxCode.Big.Pub936

/-- Table 1 line 11 with line 1 = 0, P ≤ $1,000,000, N > 0. -/
def l11 (P N : Int) : Int :=
  let l6 := min 1000000 P
  if 750000 ≤ l6 then l6 else min (max l6 750000) (l6 + N)

/-- Allowed new debt under (F)(i)(IV). -/
def allowedNew (P N : Int) : Int := min N (max 0 (750000 - P))

theorem l11_eq (P N : Int) (hP : 0 ≤ P) (hP1 : P ≤ 1000000) (hN : 0 ≤ N) : l11 P N = P + allowedNew P N := by
  unfold l11 allowedNew; simp only; split <;> omega

/-- Worksheet line 15 is (IP + IN) × (P + a)/(P + N); the statute is IP + IN × a/N. Cross-multiplied by N(P + N):
the worksheet exceeds the statute by exactly (N − a)(IN·P − IP·N), i.e. (excess new debt) × P/(P+N) × (new rate −
old rate) per dollar. -/
theorem gap_identity (IP IN P N : Int) :
    (IP + IN) * (P + allowedNew P N) * N - (IP * N + IN * allowedNew P N) * (P + N)
      = (N - allowedNew P N) * (IN * P - IP * N) := by
  generalize allowedNew P N = a; grind

/-- Exact affected set and direction: the worksheet gives more iff some new debt is over the limit and the new debt
carries a higher average rate than the old (IN/N > IP/P); the statute gives more iff over the limit and the old debt
is dearer; equal iff no excess or equal rates. -/
theorem gap_sign (IP IN P N : Int) (hP : 0 < P) (hN : 0 < N) :
    let a := allowedNew P N
    let d := (IP + IN) * (P + a) * N - (IP * N + IN * a) * (P + N)
    (0 < d ↔ a < N ∧ IP * N < IN * P) ∧ (d < 0 ↔ a < N ∧ IN * P < IP * N) := by
  intro a d
  have hid : d = (N - a) * (IN * P - IP * N) := gap_identity IP IN P N
  have ha : a ≤ N := by simp only [a, allowedNew]; omega
  rw [hid]
  constructor
  · constructor
    · intro h
      rcases Int.lt_or_le a N with h1 | h1
      · refine ⟨h1, ?_⟩
        rcases Int.lt_or_le (IP * N) (IN * P) with h2 | h2
        · exact h2
        · exfalso
          have : (N - a) * (IN * P - IP * N) ≤ 0 := Int.mul_nonpos_of_nonneg_of_nonpos (by omega) (by omega)
          omega
      · exfalso; have : N - a = 0 := by omega
        rw [this, Int.zero_mul] at h; omega
    · intro ⟨h1, h2⟩; exact Int.mul_pos (by omega) (by omega)
  · constructor
    · intro h
      rcases Int.lt_or_le a N with h1 | h1
      · refine ⟨h1, ?_⟩
        rcases Int.lt_or_le (IN * P) (IP * N) with h2 | h2
        · exact h2
        · exfalso
          have : 0 ≤ (N - a) * (IN * P - IP * N) := Int.mul_nonneg (by omega) (by omega)
          omega
      · exfalso; have : N - a = 0 := by omega
        rw [this, Int.zero_mul] at h; omega
    · intro ⟨h1, h2⟩; exact Int.mul_neg_of_pos_of_neg (by omega) (by omega)

/-- Bound: |worksheet − statute| × N(P+N) = (N − a)·|IN·P − IP·N| ≤ (P + N)·|IN·P − IP·N|, i.e. the gap is below
P × |new rate − old rate| ≤ $1,000,000 × the rate spread. -/
theorem gap_bound (IP IN P N : Int) (hP : 0 < P) (hN : 0 < N) :
    (N - allowedNew P N) * (IN * P - IP * N).natAbs ≤ (P + N) * (IN * P - IP * N).natAbs := by
  have ha : 0 ≤ allowedNew P N := by unfold allowedNew; omega
  exact Int.mul_le_mul_of_nonneg_right (by omega) (by omega)

/-! ## Worked examples (whole dollars). -/

def worksheet (IP IN P N : Int) : Int := (IP + IN) * l11 P N / (P + N)
def statute (IP IN P N : Int) : Int := IP + IN * allowedNew P N / N

/-- Pre-2017 $1,000,000 refinanced at 3% ($30,000), a 2024 second home with $1,000,000 at 7% ($70,000): worksheet
$50,000, statute $30,000 (none of the new loan is acquisition indebtedness): $20,000 too much deduction, $7,400 of tax
at 37%. -/
example : worksheet 30000 70000 1000000 1000000 = 50000 ∧ statute 30000 70000 1000000 1000000 = 30000 := by decide

/-- $600,000 old at 3% ($18,000), $600,000 new at 7% ($42,000): worksheet $37,500, statute $28,500 ($18,000 + 150/600 of
$42,000). -/
example : worksheet 18000 42000 600000 600000 = 37500 ∧ statute 18000 42000 600000 600000 = 28500 := by decide

/-- Reverse: old $600,000 at 7% ($42,000), new $600,000 at 3% ($18,000): worksheet $37,500, statute $46,500. -/
example : worksheet 42000 18000 600000 600000 = 37500 ∧ statute 42000 18000 600000 600000 = 46500 := by decide

end TaxCode.Big.Pub936

#print axioms TaxCode.Big.Pub936.gap_identity
#print axioms TaxCode.Big.Pub936.gap_sign
#print axioms TaxCode.Big.Pub936.gap_bound
