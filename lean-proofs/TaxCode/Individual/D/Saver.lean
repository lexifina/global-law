import TaxCode.Individual.D.Basic

/-!
# §25B Saver's credit (elective deferrals and IRA contributions), tax year 2025

Source: 26 U.S.C. §25B (OLRC 119-138). §25B(a): "the applicable percentage of so much of the qualified retirement
savings contributions of the eligible individual ... as do not exceed $2,000". The 2025 Act's "$2,100" (§70116(b))
applies to taxable years beginning after December 31, 2026, so 2025 uses $2,000.

§25B(b)(1) joint-return tiers (50% / 20% / 10% / 0%), indexed by §25B(b)(3) "rounded to the nearest multiple of
$500"; Notice 2024-80 (2025): "$47,500", "$51,000", "$79,000". §25B(b)(2): a head of household uses "75 percent" and
everyone else "50 percent" of each (indexed) joint amount. AGI here is §25B(e) AGI (determined without §§911, 931,
933). Each spouse is a separate eligible individual with a separate $2,000.
-/

namespace TaxCode.Individual.D
open TaxCode.Individual

/-- Notice 2024-80: the three indexed joint-return amounts for 2025. -/
def saverJoint : Int × Int × Int := (47500, 51000, 79000)

/-- §25B(b)(2): the amounts for each filing status, derived from the joint amounts as the statute directs. -/
def saverTiers : Filing → Int × Int × Int
  | .mfj => saverJoint
  | .hoh => (saverJoint.1 * 75 / 100, saverJoint.2.1 * 75 / 100, saverJoint.2.2 * 75 / 100)
  | _ => (saverJoint.1 / 2, saverJoint.2.1 / 2, saverJoint.2.2 / 2)

/-- §25B(b)(1): "not over" the first amount 50 percent; "over ... but not over" the second 20 percent; then 10
percent; "over" the third, zero. -/
def saverPercent (f : Filing) (agi : Int) : Int :=
  let (a, b, c) := saverTiers f
  if agi ≤ a then 50 else if agi ≤ b then 20 else if agi ≤ c then 10 else 0

/-- §25B(c): eligible if 18 or older, not claimed as a dependent, not a full-time student. -/
def saverEligible (age : Nat) (dependent student : Bool) : Bool := 18 ≤ age && !dependent && !student

/-- One eligible individual: contributions less distributions in the testing period (§25B(d)(2)), capped at $2,000,
times the percentage, rounded to the nearest dollar (Form 8880 line 10 × line 9 decimal). -/
def saverPerson (f : Filing) (agi contributions distributions : Int) : Int :=
  roundDollar (min (pos (contributions - distributions)) 2000 * saverPercent f agi) 100

/-- The credit for the return: one entry per eligible individual (the taxpayer, and the spouse on a joint return). -/
def saverCredit (f : Filing) (agi : Int) (people : List (Int × Int)) : Int :=
  (people.map fun (c, d) => saverPerson f agi c d).sum

/-! ## Tests -/

-- Notice 2024-80 (2025 amounts): heads of household "$35,625", "$38,250", "$59,250"; all other filers "$23,750",
-- "$25,500", "$39,500". The statute's 75% / 50% rule reproduces them exactly.
#guard saverTiers .hoh = (35625, 38250, 59250)
#guard saverTiers .single = (23750, 25500, 39500) ∧ saverTiers .mfs = (23750, 25500, 39500)
#guard saverTiers .qss = (23750, 25500, 39500)
#guard saverPercent .mfj 47500 = 50 ∧ saverPercent .mfj 47501 = 20 ∧ saverPercent .mfj 51001 = 10 ∧
  saverPercent .mfj 79000 = 10 ∧ saverPercent .mfj 79001 = 0
-- §25B(a): $2,000 at 50% gives $1,000 per person.
#guard saverCredit .mfj 40000 [(2000, 0), (2000, 0)] = 2000

/-! ## Properties -/

theorem saverPercent_antitone (f : Filing) (agi : Int) : saverPercent f (agi + 1) ≤ saverPercent f agi := by
  cases f <;> simp only [saverPercent, saverTiers, saverJoint] <;> repeat' split
  all_goals omega

theorem saverPerson_bounds (f : Filing) (agi c d : Int) : 0 ≤ saverPerson f agi c d ∧ saverPerson f agi c d ≤ 1000 := by
  have hp : 0 ≤ saverPercent f agi ∧ saverPercent f agi ≤ 50 := by
    cases f <;> simp only [saverPercent, saverTiers, saverJoint] <;> repeat' split
    all_goals omega
  unfold saverPerson
  generalize hb : min (pos (c - d)) 2000 = b
  have hb0 : 0 ≤ b := by rw [← hb]; unfold pos; omega
  have hb1 : b ≤ 2000 := by rw [← hb]; omega
  have : b * saverPercent f agi ≤ 2000 * 50 := Int.mul_le_mul hb1 hp.2 hp.1 (by omega)
  have : 0 ≤ b * saverPercent f agi := Int.mul_nonneg hb0 hp.1
  unfold roundDollar; omega

/-- Monotone: more AGI never raises one person's credit. -/
theorem saverPerson_antitone (f : Filing) (agi c d : Int) : saverPerson f (agi + 1) c d ≤ saverPerson f agi c d := by
  have hp := saverPercent_antitone f agi
  unfold saverPerson
  generalize hb : min (pos (c - d)) 2000 = b
  have hb0 : 0 ≤ b := by rw [← hb]; unfold pos; omega
  have : b * saverPercent f (agi + 1) ≤ b * saverPercent f agi := Int.mul_le_mul_of_nonneg_left hp hb0
  unfold roundDollar; exact Int.ediv_le_ediv (by omega) (by omega)

/-- **Cliffs.** The tiers are cliffs, not phase-outs. A married couple each contributing $2,000: AGI $47,500 gives
$2,000; $47,501 gives $800 ($1,200 lost for $1); $51,001 gives $400; $79,001 gives nothing. -/
theorem saver_cliffs :
    saverCredit .mfj 47500 [(2000, 0), (2000, 0)] = 2000 ∧ saverCredit .mfj 47501 [(2000, 0), (2000, 0)] = 800 ∧
    saverCredit .mfj 51000 [(2000, 0), (2000, 0)] = 800 ∧ saverCredit .mfj 51001 [(2000, 0), (2000, 0)] = 400 ∧
    saverCredit .mfj 79000 [(2000, 0), (2000, 0)] = 400 ∧ saverCredit .mfj 79001 [(2000, 0), (2000, 0)] = 0 := by
  decide

/-- The largest one-dollar loss per person is 30% of contributions ($600): from 50% to 20%. -/
theorem saverPerson_step_le_600 (f : Filing) (agi c d : Int) :
    saverPerson f agi c d - saverPerson f (agi + 1) c d ≤ 600 := by
  have hstep : saverPercent f agi - saverPercent f (agi + 1) ≤ 30 ∧ saverPercent f (agi + 1) ≤ saverPercent f agi := by
    cases f <;> simp only [saverPercent, saverTiers, saverJoint] <;> repeat' split
    all_goals omega
  unfold saverPerson
  generalize hb : min (pos (c - d)) 2000 = b
  have hb0 : 0 ≤ b := by rw [← hb]; unfold pos; omega
  have hb1 : b ≤ 2000 := by rw [← hb]; omega
  have : b * saverPercent f agi - b * saverPercent f (agi + 1) ≤ 2000 * 30 := by
    rw [← Int.mul_sub]; exact Int.mul_le_mul hb1 hstep.1 (by omega) (by omega)
  unfold roundDollar; omega

end TaxCode.Individual.D
