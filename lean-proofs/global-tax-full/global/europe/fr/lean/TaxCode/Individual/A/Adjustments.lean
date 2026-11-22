import TaxCode.Individual.A.SelfEmployment

/-!
# §62 adjustments: educator expenses, §219 IRA deduction, §221 student loan interest, §223 HSA

2025 figures: educator expenses $300 (Rev. Proc. 2024-40); IRA deductible amount $7,000, catch-up $1,000, and the
§219(g) applicable dollar amounts $79,000 / $126,000 / $236,000 (Notice 2024-80, reproduced in Pub 590-A (2025)
Tables 1-2 and 1-3); student loan interest phase-out from $85,000 ($170,000 joint) (Rev. Proc. 2024-40, reproduced
in Pub 970 (2025) "What's New").
-/

namespace TaxCode.Individual.A
open TaxCode.Individual

/-! ## §62(a)(2)(D) educator expenses -/

/-- §62(a)(2)(D): "not in excess of $250", indexed by §62(d)(3) in $50 steps: $300 for 2025 (Rev. Proc. 2024-40). -/
def educatorLimit2025 : Int := 300

/-- The limit is per eligible educator. `Household` has one `educatorExpenses` amount and does not say which spouse is
an educator, so on a joint return the cap is $600 (both spouses educators) — an upper bound. -/
def educatorDeduction (h : Household) : Int :=
  max 0 (min h.educatorExpenses (educatorLimit2025 * (if h.filing == .mfj && h.spouse.isSome then 2 else 1)))

/-! ## §223 HSA (§62(a)(19)) -/

/-- §223(a): contributions are taken as given; the §223(b) monthly limits ($4,300 self-only / $8,550 family for 2025)
and the employer-contribution offset are not modelled. -/
def hsaDeduction (h : Household) : Int := max 0 h.hsaContributions

/-! ## §219 IRA deduction (§62(a)(7)) -/

/-- §219(b)(5)(A) deductible amount ($7,000 for 2025 after (b)(5)(C)) plus the (b)(5)(B) catch-up ($1,000 for 2025
after (b)(5)(C)(iii)) for an individual who has attained age 50 before the close of the year. -/
def iraDollarLimit (age : Nat) : Int := if 50 ≤ age then 8000 else 7000

/-- Who is an active participant (§219(g)(1), (5)). -/
inductive Coverage where
  | none        -- neither the individual nor the spouse
  | self        -- the individual is an active participant
  | spouseOnly  -- (g)(7): "solely because their spouse is an active participant"
  deriving DecidableEq, Repr

/-- §219(g)(3)(B) applicable dollar amount (2025, after the (g)(8) inflation adjustment), or `none` when (g) does not
apply. MFS living apart all year are "not treated as married individuals" ((g)(4)). A qualifying surviving spouse does
not file "a joint return", so the statute gives the (ii) amount; Pub 590-A Table 1-2 gives the joint amount
(see `iraApplicableAmountIRS`). -/
def iraApplicableAmount (f : Filing) (livedApart : Bool) : Coverage → Option Int
  | .none => none
  | .self =>
    match f with
    | .mfj => some 126000                                  -- (3)(B)(i), $80,000 indexed
    | .mfs => if livedApart then some 79000 else some 0   -- (4) / (3)(B)(iii)
    | _ => some 79000                                      -- (3)(B)(ii), $50,000 indexed
  | .spouseOnly =>
    match f with
    | .mfj => some 236000                                  -- (7)(A), $150,000 indexed
    | .mfs => if livedApart then none else some 0          -- (4): not married; else (3)(B)(iii)
    | _ => none                                            -- no spouse for (g)(1) purposes

/-- §219(g)(2)(A)(ii): $10,000, or $20,000 on a joint return — except $10,000 where (g)(7) applies. -/
def iraRange (f : Filing) (c : Coverage) : Int :=
  match f, c with
  | .mfj, .self => 20000
  | _, _ => 10000

/-- The IRS reading in Pub 590-A (2025) Table 1-2: a qualifying surviving spouse uses the joint-return amounts. -/
def iraApplicableAmountIRS (f : Filing) (livedApart : Bool) (c : Coverage) : Option Int :=
  if f == .qss && c == .self then some 126000 else iraApplicableAmount f livedApart c

def iraRangeIRS (f : Filing) (c : Coverage) : Int :=
  if f == .qss && c == .self then 20000 else iraRange f c

/-- §219(g)(2)(A),(C): the reduction is the limitation times excess/range, "rounded to the next lowest $10".
`excess` is MAGI minus the applicable dollar amount. -/
def phaseReduction (L excess R : Int) : Int :=
  if excess ≤ 0 then 0 else L * excess / R / 10 * 10

/-- §219(g)(1)–(2)(B): the dollar limitation reduced "but not below zero", and not below $200 "unless ... reduced to
zero". -/
def reducedLimit (L excess R : Int) : Int :=
  let v := L - phaseReduction L excess R
  if v ≤ 0 then 0 else if v < 200 then 200 else v

/-- The individual's §219(b)(1)(A)/(c)(1)(A) dollar limitation after (g). -/
def personLimit (age : Nat) (f : Filing) (livedApart : Bool) (c : Coverage) (magi : Int) : Int :=
  match iraApplicableAmount f livedApart c with
  | none => iraDollarLimit age
  | some s => reducedLimit (iraDollarLimit age) (magi - s) (iraRange f c)

/-- `Household.activeParticipant` is a single flag; it is read as "the individual(s) contributing are active
participants" (`Coverage.self`). The (g)(7) spouse-only case is reachable only through `personLimit`. -/
def iraCoverage (h : Household) : Coverage := if h.activeParticipant then .self else .none

/-- §219(f)(1) compensation of the head: wages plus earned income (§401(c)(2): net self-employment earnings after the
§164(f) deduction). A self-employment loss does not reduce wages (Pub 590-A, "Self-employment loss"). -/
def headCompensation (h : Household) : Int := max 0 (headWages h) + max 0 (h.seIncome - halfSeTax h)

def spouseCompensation (h : Household) : Int := max 0 h.wagesSpouse

/-- §219 deduction for the household, given the §219(g)(3)(A) MAGI. `iraContributions` is the couple's total; its
split between spouses is not in `Household`, so the most favourable split is assumed: on a joint return the total is
capped by the sum of the two dollar limitations and, by §219(c) (spousal IRA), by the couple's combined
compensation. Otherwise §219(b)(1): lesser of the dollar limitation and compensation. -/
def iraDeduction (h : Household) (magi : Int) (livedApart : Bool := false) : Int :=
  let c := iraCoverage h
  let lh := personLimit h.head.age h.filing livedApart c magi
  let contrib := max 0 h.iraContributions
  match h.filing, h.spouse with
  | .mfj, some sp =>
    min contrib (min (lh + personLimit sp.age h.filing livedApart c magi)
      (headCompensation h + spouseCompensation h))
  | _, _ => min contrib (min lh (headCompensation h))

/-! ### Properties of the §219(g) phase-out -/

theorem phaseReduction_mono {L R e e' : Int} (hL : 0 ≤ L) (hR : 0 < R) (h : e ≤ e') :
    phaseReduction L e R ≤ phaseReduction L e' R := by
  unfold phaseReduction
  have h1 : L * e / R ≤ L * e' / R := Int.ediv_le_ediv hR (Int.mul_le_mul_of_nonneg_left h hL)
  by_cases he : e ≤ 0
  · by_cases he' : e' ≤ 0
    · simp [he, he']
    · have : 0 ≤ L * e' / R := Int.ediv_nonneg (Int.mul_nonneg hL (by omega)) (by omega)
      simp only [he, he', ↓reduceIte]
      generalize L * e' / R = q at *
      omega
  · simp only [he, show ¬ e' ≤ 0 by omega, ↓reduceIte]
    generalize L * e / R = p at *
    generalize L * e' / R = q at *
    omega

theorem phaseReduction_nonneg {L R e : Int} (hL : 0 ≤ L) (hR : 0 < R) : 0 ≤ phaseReduction L e R := by
  unfold phaseReduction
  split
  · omega
  · have : 0 ≤ L * e / R := Int.ediv_nonneg (Int.mul_nonneg hL (by omega)) (by omega)
    generalize L * e / R = q at *
    omega

/-- The reduced limitation is non-increasing in MAGI (the $200 floor included). -/
theorem reducedLimit_antitone {L R e e' : Int} (hL : 0 ≤ L) (hR : 0 < R) (h : e ≤ e') :
    reducedLimit L e' R ≤ reducedLimit L e R := by
  have := phaseReduction_mono hL hR h
  unfold reducedLimit
  dsimp only
  generalize phaseReduction L e R = p at *
  generalize phaseReduction L e' R = q at *
  repeat' split
  all_goals omega

/-- Never negative, never above the dollar limitation, and never strictly between $0 and $200. -/
theorem reducedLimit_bounds {L R e : Int} (hL : 200 ≤ L) (hR : 0 < R) :
    0 ≤ reducedLimit L e R ∧ reducedLimit L e R ≤ L ∧
    (reducedLimit L e R = 0 ∨ 200 ≤ reducedLimit L e R) := by
  have := phaseReduction_nonneg (L := L) (e := e) (by omega) hR
  unfold reducedLimit
  dsimp only
  generalize phaseReduction L e R = p at *
  repeat' split
  all_goals omega

theorem iraRange_pos (f : Filing) (c : Coverage) : 0 < iraRange f c := by
  cases f <;> cases c <;> decide

theorem personLimit_antitone (age : Nat) (f : Filing) (la : Bool) (c : Coverage) {m m' : Int} (hm : m ≤ m') :
    personLimit age f la c m' ≤ personLimit age f la c m := by
  unfold personLimit
  split
  · omega
  · exact reducedLimit_antitone (by unfold iraDollarLimit; split <;> omega) (iraRange_pos f c) (by omega)

theorem personLimit_nonneg (age : Nat) (f : Filing) (la : Bool) (c : Coverage) (m : Int) :
    0 ≤ personLimit age f la c m := by
  unfold personLimit
  split
  · unfold iraDollarLimit; split <;> omega
  · exact (reducedLimit_bounds (by unfold iraDollarLimit; split <;> omega) (iraRange_pos f c)).1

/-- The household IRA deduction is non-increasing in MAGI. -/
theorem iraDeduction_antitone (h : Household) (la : Bool) {m m' : Int} (hm : m ≤ m') :
    iraDeduction h m' la ≤ iraDeduction h m la := by
  unfold iraDeduction
  dsimp only
  split
  · rename_i sp _ _
    have := personLimit_antitone h.head.age h.filing la (iraCoverage h) hm
    have := personLimit_antitone sp.age h.filing la (iraCoverage h) hm
    omega
  · have := personLimit_antitone h.head.age h.filing la (iraCoverage h) hm
    omega

/-- Never negative and never more than what was contributed. -/
theorem iraDeduction_bounds (h : Household) (la : Bool) (m : Int) :
    0 ≤ iraDeduction h m la ∧ iraDeduction h m la ≤ max 0 h.iraContributions := by
  unfold iraDeduction headCompensation spouseCompensation
  dsimp only
  split
  · rename_i sp _ _
    have := personLimit_nonneg h.head.age h.filing la (iraCoverage h) m
    have := personLimit_nonneg sp.age h.filing la (iraCoverage h) m
    omega
  · have := personLimit_nonneg h.head.age h.filing la (iraCoverage h) m
    omega

/-! ### The statute's "reduce, round the reduction down" equals Pub 590-A Worksheet 1-2's "multiply the distance to
the top of the range by a percentage, round the result up to $10, at least $200" — for every MAGI inside the range and
each 2025 (limit, range) pair. -/

/-- Pub 590-A (2025) Worksheet 1-2: line 3 = top of range − MAGI; line 4 = line 3 × (L/R) (70%, 80%, 35% or 40%),
rounded up to the next $10, and $200 if less than $200. -/
def worksheet12 (L R excess : Int) : Int :=
  let line3 := R - excess
  let line4 := (L * line3 + 10 * R - 1) / (10 * R) * 10
  if line4 < 200 then 200 else line4

theorem worksheet12_eq_7000_10000 (e : Int) (h0 : 0 < e) (h1 : e < 10000) :
    reducedLimit 7000 e 10000 = worksheet12 7000 10000 e := by
  unfold reducedLimit phaseReduction worksheet12; dsimp only
  repeat' split
  all_goals omega

theorem worksheet12_eq_8000_10000 (e : Int) (h0 : 0 < e) (h1 : e < 10000) :
    reducedLimit 8000 e 10000 = worksheet12 8000 10000 e := by
  unfold reducedLimit phaseReduction worksheet12; dsimp only
  repeat' split
  all_goals omega

theorem worksheet12_eq_7000_20000 (e : Int) (h0 : 0 < e) (h1 : e < 20000) :
    reducedLimit 7000 e 20000 = worksheet12 7000 20000 e := by
  unfold reducedLimit phaseReduction worksheet12; dsimp only
  repeat' split
  all_goals omega

theorem worksheet12_eq_8000_20000 (e : Int) (h0 : 0 < e) (h1 : e < 20000) :
    reducedLimit 8000 e 20000 = worksheet12 8000 20000 e := by
  unfold reducedLimit phaseReduction worksheet12; dsimp only
  repeat' split
  all_goals omega

/-- Marginal rate of the phase-out (single, covered, under 50): one more dollar of MAGI removes at most $10 of the
$7,000 limitation — except at the very top of the range, where the $200 floor ends in a $200 cliff. -/
theorem reducedLimit_step_7000 (e : Int) :
    reducedLimit 7000 e 10000 ≤ reducedLimit 7000 (e - 1) 10000 ∧
    (reducedLimit 7000 (e - 1) 10000 ≤ reducedLimit 7000 e 10000 + 10 ∨ e = 10000) := by
  unfold reducedLimit phaseReduction; dsimp only
  constructor
  · repeat' split
    all_goals omega
  · by_cases he : e = 10000
    · exact Or.inr he
    · left
      repeat' split
      all_goals omega

/-- The $200 floor is a cliff: at the top of the range the deductible limitation drops from $200 to $0 for one
dollar of MAGI (single, covered, under 50). -/
theorem ira_200_cliff : reducedLimit 7000 9999 10000 = 200 ∧ reducedLimit 7000 10000 10000 = 0 := by decide

/-! ## §221 student loan interest (§62(a)(17)) -/

/-- §221(b)(1): $2,500. -/
def studentLoanCap : Int := 2500

/-- §221(b)(2)(B) amounts for 2025 after the (f) adjustment: start $85,000, range $15,000; joint $170,000 and
$30,000. Married filing separately: no deduction (§221(e)(2)). -/
def studentLoanPhase : Filing → Option (Int × Int)
  | .mfj => some (170000, 30000)
  | .mfs => none
  | _ => some (85000, 15000)

/-- §221(b)(2): the capped interest reduced by capped × (MAGI − start)/range; the reduction rounded to the nearest
dollar (the statute has no rounding rule; Pub 970 Worksheet 4-1 rounds the ratio to three decimals). -/
def studentLoanCore (interest start R magi : Int) : Int :=
  let x := max 0 (min interest studentLoanCap)
  let e := magi - start
  if e ≤ 0 then x else if R ≤ e then 0 else x - roundDollar (x * e) R

/-- §221 deduction given the §221(b)(2)(C) MAGI. §221(c): none for an individual whom another taxpayer may claim
(`canBeClaimedAsDependent` — the statute says "is allowed"; Pub 970 reads it as "claims"). -/
def studentLoanDeduction (h : Household) (magi : Int) : Int :=
  if h.canBeClaimedAsDependent then 0
  else match studentLoanPhase h.filing with
    | none => 0
    | some (s, R) => studentLoanCore h.studentLoanInterest s R magi

theorem roundDollar_le_of_le_mul {p x R : Int} (hR : 0 < R) (h : p ≤ x * R) : roundDollar p R ≤ x := by
  unfold roundDollar
  rw [Int.ediv_le_iff_le_mul (by omega)]
  have : x * (2 * R) = 2 * (x * R) := by rw [Int.mul_left_comm]
  omega

theorem roundDollar_nonneg' {p R : Int} (hR : 0 < R) (hp : 0 ≤ p) : 0 ≤ roundDollar p R :=
  Int.ediv_nonneg (by omega) (by omega)

theorem roundDollar_mono {p q R : Int} (hR : 0 < R) (h : p ≤ q) : roundDollar p R ≤ roundDollar q R :=
  Int.ediv_le_ediv (by omega) (by omega)

/-- The student loan deduction is non-increasing in MAGI, for every amount of interest and every start/range. -/
theorem studentLoanCore_antitone (i s R : Int) (hR : 0 < R) {m m' : Int} (hm : m ≤ m') :
    studentLoanCore i s R m' ≤ studentLoanCore i s R m := by
  unfold studentLoanCore
  dsimp only
  generalize hx : max 0 (min i studentLoanCap) = x
  have hx0 : 0 ≤ x := by omega
  have mono : roundDollar (x * (m - s)) R ≤ roundDollar (x * (m' - s)) R :=
    roundDollar_mono hR (Int.mul_le_mul_of_nonneg_left (by omega) hx0)
  have le_x : ∀ e, e ≤ R → roundDollar (x * e) R ≤ x := fun e he =>
    roundDollar_le_of_le_mul hR (Int.mul_le_mul_of_nonneg_left he hx0)
  have nn : ∀ e, 0 ≤ e → 0 ≤ roundDollar (x * e) R := fun e he =>
    roundDollar_nonneg' hR (Int.mul_nonneg hx0 he)
  have a1 := le_x (m - s)
  have a2 := nn (m' - s)
  repeat' split
  all_goals omega

/-- Never negative and never above $2,500 or the interest paid. -/
theorem studentLoanCore_bounds (i s R m : Int) (hR : 0 < R) :
    0 ≤ studentLoanCore i s R m ∧ studentLoanCore i s R m ≤ min (max 0 i) studentLoanCap := by
  unfold studentLoanCore
  dsimp only
  generalize hx : max 0 (min i studentLoanCap) = x
  have hx0 : 0 ≤ x := by omega
  have le_x : ∀ e, e ≤ R → roundDollar (x * e) R ≤ x := fun e he =>
    roundDollar_le_of_le_mul hR (Int.mul_le_mul_of_nonneg_left he hx0)
  have nn : ∀ e, 0 ≤ e → 0 ≤ roundDollar (x * e) R := fun e he =>
    roundDollar_nonneg' hR (Int.mul_nonneg hx0 he)
  have a1 := le_x (m - s)
  have a2 := nn (m - s)
  unfold studentLoanCap at *
  repeat' split
  all_goals omega

theorem studentLoanDeduction_antitone (h : Household) {m m' : Int} (hm : m ≤ m') :
    studentLoanDeduction h m' ≤ studentLoanDeduction h m := by
  unfold studentLoanDeduction
  split
  · omega
  · cases hf : h.filing <;> simp only [studentLoanPhase] <;>
      first | exact Int.le_refl _ | exact studentLoanCore_antitone _ _ _ (by decide) hm

theorem studentLoanDeduction_nonneg (h : Household) (m : Int) : 0 ≤ studentLoanDeduction h m := by
  unfold studentLoanDeduction
  split
  · omega
  · cases hf : h.filing <;> simp only [studentLoanPhase] <;>
      first | omega | exact (studentLoanCore_bounds _ _ _ _ (by decide)).1

end TaxCode.Individual.A
