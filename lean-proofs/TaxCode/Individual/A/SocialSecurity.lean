import TaxCode.Individual.Household

/-!
# §86: social security and tier 1 railroad retirement benefits (tax year 2025)

Copied from 26 U.S.C. §86 (OLRC release point 119-138). §86 has no inflation adjustment: the base amounts are the
statutory $25,000 / $32,000 / zero and the adjusted base amounts $34,000 / $44,000 / zero.

**Units.** The statute's amounts are exact fractions (one-half, 85 percent). To keep them exact the core function
`taxableSS40` works in fortieths of a dollar (every quantity is multiplied by 40): one-half of `B` is `20 * B`,
85 percent of an excess `E` is `34 * E`. The household-level amount is rounded to the nearest whole dollar, half up
(`roundDollar _ 40`), as Form 1040 permits; Pub 915 Worksheet 1 rounds line by line instead (see FINDINGS.md).
-/

namespace TaxCode.Individual.A
open TaxCode.Individual

/-- §86(c)(1) "base amount": (A) $25,000; (B) $32,000 "in the case of a joint return"; (C) zero for a taxpayer
married at the close of the year who does not file jointly and "does not live apart from his spouse at all times
during the taxable year". `livedApart` is not a `Household` field; callers pass it. -/
def baseAmount (f : Filing) (livedApart : Bool) : Int :=
  match f with
  | .mfj => 32000
  | .mfs => if livedApart then 25000 else 0
  | _ => 25000

/-- §86(c)(2) "adjusted base amount": $34,000; $44,000 joint; zero for a taxpayer described in (c)(1)(C). -/
def adjustedBaseAmount (f : Filing) (livedApart : Bool) : Int :=
  match f with
  | .mfj => 44000
  | .mfs => if livedApart then 34000 else 0
  | _ => 34000

theorem base_le_adjusted (f : Filing) (la : Bool) :
    0 ≤ baseAmount f la ∧ baseAmount f la ≤ adjustedBaseAmount f la := by
  cases f <;> cases la <;> decide

/-- §86(a)–(b), exact, in fortieths of a dollar. `b` base amount, `a` adjusted base amount, `B` benefits received
(net of repayments, §86(d)(2)(A)), `M` the §86(b)(2) modified adjusted gross income.

* §86(b)(1): the taxpayer is "described" when `M + B/2` exceeds the base amount (`X > 0`).
* §86(a)(1): lesser of one-half of benefits and one-half of that excess (`a1`).
* §86(a)(2): when `M + B/2` exceeds the adjusted base amount (`Y > 0`): lesser of (A) 85% of that excess plus the
  lesser of the (a)(1) amount and one-half of (adjusted base − base), and (B) 85% of benefits. -/
def taxableSS40 (b a B M : Int) : Int :=
  let X := 40 * M + 20 * B - 40 * b
  if X ≤ 0 then 0
  else
    let a1 := min (20 * B) (X / 2)
    let Y := 40 * M + 20 * B - 40 * a
    if Y ≤ 0 then a1
    else min (34 * M + 17 * B - 34 * a + min a1 (20 * (a - b))) (34 * B)

/-- Pub 915 (2025) Worksheet 1, lines 1–19, in fortieths of a dollar (`M` = line 3 + line 4 + line 5 − line 7).
`mfsTogether` is the "married filing separately and lived with your spouse at any time in 2025" path, which skips
lines 9–16 and enters 85% of line 8 on line 17. -/
def worksheet1_40 (b a B M : Int) (mfsTogether : Bool) : Int :=
  let L2 := 20 * B
  let L8 := 40 * M + 20 * B
  let L18 := 34 * B
  if mfsTogether then
    if L8 ≤ 0 then 0 else min (17 * L8 / 20) L18
  else
    let L9 := 40 * b
    if L8 ≤ L9 then 0
    else
      let L10 := L8 - L9
      let L11 := 40 * (a - b)
      let L12 := max 0 (L10 - L11)
      let L13 := min L10 L11
      let L14 := L13 / 2
      let L15 := min L2 L14
      let L16 := 17 * L12 / 20
      min (L15 + L16) L18

/-! ## The statute and Pub 915 Worksheet 1 agree (for all inputs) -/

/-- Worksheet 1 computes exactly the §86 amount whenever benefits are non-negative and `0 ≤ b ≤ a`. -/
theorem worksheet1_eq_statute (b a B M : Int) (hB : 0 ≤ B) (_hb : 0 ≤ b) (hba : b ≤ a) :
    worksheet1_40 b a B M false = taxableSS40 b a B M := by
  unfold worksheet1_40 taxableSS40
  simp only [Bool.false_eq_true, ↓reduceIte]
  repeat' split
  all_goals omega

/-- The "lived with spouse" path of Worksheet 1 is §86 with base and adjusted base amount zero (§86(c)(1)(C),
(c)(2)(C)). -/
theorem worksheet1_mfs_together (B M : Int) (hB : 0 ≤ B) :
    worksheet1_40 0 0 B M true = taxableSS40 0 0 B M := by
  unfold worksheet1_40 taxableSS40
  simp only [↓reduceIte]
  repeat' split
  all_goals omega

/-! ## Properties of §86 for all inputs -/

theorem taxableSS40_nonneg (b a B M : Int) (hB : 0 ≤ B) : 0 ≤ taxableSS40 b a B M := by
  unfold taxableSS40
  dsimp only
  repeat' split
  all_goals omega

/-- Never more than 85 percent of benefits (§86(a)(2)(B)). -/
theorem taxableSS40_le_85 (b a B M : Int) (hB : 0 ≤ B) : taxableSS40 b a B M ≤ 34 * B := by
  unfold taxableSS40
  dsimp only
  repeat' split
  all_goals omega

/-- Below the adjusted base amount, never more than one-half of benefits (§86(a)(1)(A)). -/
theorem taxableSS40_le_half (b a B M : Int) (hB : 0 ≤ B) (hY : 40 * M + 20 * B - 40 * a ≤ 0) :
    taxableSS40 b a B M ≤ 20 * B := by
  unfold taxableSS40
  dsimp only
  repeat' split
  all_goals omega

/-- More other income never lowers the taxable amount. -/
theorem taxableSS40_mono (b a B M M' : Int) (hB : 0 ≤ B) (hba : b ≤ a) (hM : M ≤ M') :
    taxableSS40 b a B M ≤ taxableSS40 b a B M' := by
  unfold taxableSS40
  dsimp only
  repeat' split
  all_goals omega

/-- The marginal inclusion rate is between 0 and 85 cents per dollar of other income (34 fortieths). -/
theorem taxableSS40_marginal (b a B M : Int) (hB : 0 ≤ B) (hba : b ≤ a) :
    taxableSS40 b a B M ≤ taxableSS40 b a B (M + 1) ∧
    taxableSS40 b a B (M + 1) ≤ taxableSS40 b a B M + 34 := by
  unfold taxableSS40
  dsimp only
  constructor <;> (repeat' split) <;> omega

/-- The "tax torpedo": past the adjusted base amount, and before the 85%-of-benefits cap binds, each further dollar
of other income makes exactly 85 cents of benefits taxable (so adds $1.85 to gross income). Requires benefits of
at least (adjusted base − base) so that the (a)(2)(A)(ii) term has reached its own cap. -/
theorem taxableSS40_torpedo (b a B M : Int) (hba : b ≤ a) (hB : a - b ≤ B)
    (hY : 0 < 40 * M + 20 * B - 40 * a)
    (hcap : 34 * (M + 1) + 17 * B - 34 * a + 20 * (a - b) ≤ 34 * B) :
    taxableSS40 b a B (M + 1) = taxableSS40 b a B M + 34 := by
  unfold taxableSS40
  dsimp only
  repeat' split
  all_goals omega

/-- Between the base and adjusted base amounts, and while one-half of benefits is not reached, each further dollar
makes exactly 50 cents of benefits taxable (20 fortieths). -/
theorem taxableSS40_half_zone (b a B M : Int) (hX : 0 < 40 * M + 20 * B - 40 * b)
    (hY : 40 * (M + 1) + 20 * B - 40 * a ≤ 0) (hhalf : 40 * (M + 1) + 20 * B - 40 * b ≤ 40 * B) :
    taxableSS40 b a B (M + 1) = taxableSS40 b a B M + 20 := by
  unfold taxableSS40
  dsimp only
  repeat' split
  all_goals omega

/-- Married filing separately and living together: the first dollar of provisional income is taxed at 85 percent
(base amount zero), so there is no 50% zone at all. -/
theorem taxableSS40_mfs_together (B M : Int) (hB : 0 ≤ B) (hpos : 0 < 40 * M + 20 * B) :
    taxableSS40 0 0 B M = min (34 * M + 17 * B) (34 * B) := by
  unfold taxableSS40
  dsimp only
  repeat' split
  all_goals omega

/-! ## Household level -/

/-- §86(b)(2) modified adjusted gross income: AGI "determined without regard to this section and sections 85(c),
135, 137, 221, 911, 931, and 933", "increased by" tax-exempt interest. The caller supplies AGI without §86 and
§221 (but with §219); §§85(c), 135, 137, 911, 931, 933 are not in `Household`. -/
def magi86 (h : Household) (agiWithout86and221 : Int) : Int := agiWithout86and221 + h.taxExemptInterest

/-- Taxable social security for a household, given AGI computed without §86 and §221. Net benefits below zero
(repayments exceeding benefits, §86(d)(2)) count as zero. -/
def taxableSocialSecurityGiven (h : Household) (livedApart : Bool) (agiWithout86and221 : Int) : Int :=
  roundDollar (taxableSS40 (baseAmount h.filing livedApart) (adjustedBaseAmount h.filing livedApart)
    (max 0 h.socialSecurity) (magi86 h agiWithout86and221)) 40

theorem taxableSocialSecurityGiven_mono (h : Household) (la : Bool) (m m' : Int) (hm : m ≤ m') :
    taxableSocialSecurityGiven h la m ≤ taxableSocialSecurityGiven h la m' := by
  unfold taxableSocialSecurityGiven roundDollar magi86
  have hb := base_le_adjusted h.filing la
  have := taxableSS40_mono (baseAmount h.filing la) (adjustedBaseAmount h.filing la) (max 0 h.socialSecurity)
    (m + h.taxExemptInterest) (m' + h.taxExemptInterest) (by omega) hb.2 (by omega)
  omega

theorem taxableSocialSecurityGiven_bounds (h : Household) (la : Bool) (m : Int) :
    0 ≤ taxableSocialSecurityGiven h la m ∧
    40 * taxableSocialSecurityGiven h la m ≤ 34 * max 0 h.socialSecurity + 20 := by
  unfold taxableSocialSecurityGiven roundDollar
  have hb := base_le_adjusted h.filing la
  have h1 := taxableSS40_nonneg (baseAmount h.filing la) (adjustedBaseAmount h.filing la) (max 0 h.socialSecurity)
    (magi86 h m) (by omega)
  have h2 := taxableSS40_le_85 (baseAmount h.filing la) (adjustedBaseAmount h.filing la) (max 0 h.socialSecurity)
    (magi86 h m) (by omega)
  omega

end TaxCode.Individual.A
