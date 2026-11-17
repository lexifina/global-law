import TaxCode.Individual.B.Deductions
import TaxCode.Individual.D.Saver
import TaxCode.Individual.D.DependentCare

/-!
# Earlier grid findings (tools/hunt/out/forms/*.md) the model covers, as theorems

1. **Form 2555 lines 45 and 50 as the "amount excluded under section 911"** — Schedule 1-A lines 3/31 (§§224, 225,
   163(h)(4), 151(d)(5)(C)), Form 8962 Worksheets 1-1/1-2 line 3 (§36B), Schedule 8812 line 2b (§24, `Schedule8812`),
   Form 8863 line 2 (§25A, by the form's own "see Pub. 970" redirect not checked here). The statutes say "increased by
   any amount excluded from gross income under section 911"; line 45 = line 43 (the §911(a) exclusions) − line 44
   (deductions disallowed by §911(d)(6)); line 50 is the §911(c)(4) housing DEDUCTION. `magi_gap`: the form's MAGI is
   the statute's plus (line 50 − line 44), for all inputs; the deductions then differ by at most the phase-out rate
   times that gap (`senior_gap`, `tips_gap`, `car_gap`).
2. **Form 8880 line 4, inherited IRAs** (Credits.md item 7): `saver_inherited`.
3. **Form 2441 line 4/5 deemed earned income for an unmarried student or disabled filer** (Credits.md item 6):
   `cdcc_unmarried_student`.

Statute side: `TaxCode.Individual.B` (`seniorPerPerson`, `tipsReduction`, `carReduction`) and `TaxCode.Individual.D`
(`saverPerson`, `cdccExpenses`, `cdcc2025`).
-/

namespace TaxCode.Forms.GridFindings
open TaxCode.Individual TaxCode.Individual.B TaxCode.Individual.D

/-! ## 1. The Form 2555 add-back -/

/-- Form MAGI: AGI + Form 2555 line 45 (= line 43 − line 44) + line 50. Statute MAGI: AGI + the amount excluded
under §911 (line 43). -/
def formMagi (agi l43 l44 l50 : Int) : Int := agi + (l43 - l44) + l50
def statMagi (agi l43 : Int) : Int := agi + l43

theorem magi_gap (agi l43 l44 l50 : Int) : formMagi agi l43 l44 l50 = statMagi agi l43 + (l50 - l44) := by
  unfold formMagi statMagi; omega

/-- **Senior deduction (§151(d)(5)(C), Schedule 1-A line 35)**: a MAGI gap of `d ≥ 0` changes each $6,000 by at
most 6% of `d` (plus a dollar of rounding), never in the other direction. With `d = line 50 − line 44 > 0` the form
gives less; with `d < 0` (line 44 larger) it gives more (apply with the roles swapped). -/
theorem senior_gap (f : Filing) (m d : Int) (hd : 0 ≤ d) :
    seniorPerPerson f (m + d) ≤ seniorPerPerson f m ∧
      100 * (seniorPerPerson f m - seniorPerPerson f (m + d)) ≤ 6 * d + 100 := by
  unfold seniorPerPerson roundDollar; omega

/-- **Tips and overtime (§§224(b)(2), 225(b)(2))**: $100 per whole $1,000 — at most `100 × (d / 1000 + 1)`. -/
theorem tips_gap (f : Filing) (m d : Int) (hd : 0 ≤ d) :
    tipsReduction f m ≤ tipsReduction f (m + d) ∧ tipsReduction f (m + d) - tipsReduction f m ≤ 100 * (d / 1000 + 1) := by
  unfold tipsReduction; omega

/-- **Car loan interest (§163(h)(4)(C)(ii))**: $200 per $1,000 "or portion thereof" — at most `200 × (d/1000 + 1)`. -/
theorem car_gap (f : Filing) (m d : Int) (hd : 0 ≤ d) :
    carReduction f m ≤ carReduction f (m + d) ∧ carReduction f (m + d) - carReduction f m ≤ 200 * (d / 1000 + 1) := by
  unfold carReduction; omega

/-- The grid's examples, now theorems: MFJ, both 66, AGI $20,000, exclusion $130,000, housing deduction $50,000:
statute MAGI $150,000 (each senior $6,000), form $200,000 (each $3,000). Single, $8,000 car-loan interest, AGI
$20,000, exclusion $70,000, housing deduction $50,000: statute $8,000, form $0. -/
theorem examples :
    seniorPerPerson .mfj (statMagi 20000 130000) = 6000 ∧ seniorPerPerson .mfj (formMagi 20000 130000 0 50000) = 3000 ∧
    max 0 (8000 - carReduction .single (statMagi 20000 70000)) = 8000 ∧
    max 0 (8000 - carReduction .single (formMagi 20000 70000 0 50000)) = 0 := by decide

/-! ## 2. Form 8880: distributions from inherited IRAs -/

/-- §25B(d)(2)(A): contributions "reduced by ... distributions received ... from any entity of a type to which
contributions under paragraph (1) may be made" — an inherited IRA is an IRA. Form 8880 line 4 instructions: do not
include "Distributions from an inherited IRA by a nonspousal beneficiary". Form: `inherited` left out. -/
def saverForm (f : Filing) (agi c dOther _inherited : Int) : Int := saverPerson f agi c dOther
def saverStat (f : Filing) (agi c dOther inherited : Int) : Int := saverPerson f agi c (dOther + inherited)

/-- **The form never gives less, and gives more by at most the credit rate × the inherited distribution, at most
$1,000 a person** (`saverPerson` is at most $1,000). -/
theorem saver_inherited (f : Filing) (agi c d i : Int) (hi : 0 ≤ i) :
    saverStat f agi c d i ≤ saverForm f agi c d i ∧ saverForm f agi c d i - saverStat f agi c d i ≤ 1000 ∧
      100 * (saverForm f agi c d i - saverStat f agi c d i) ≤ saverPercent f agi * i + 100 := by
  have hp : 0 ≤ saverPercent f agi ∧ saverPercent f agi ≤ 50 := by
    unfold saverPercent saverTiers saverJoint; cases f <;> simp <;> split <;> (try split) <;> (try split) <;> omega
  have hb1 := saverPerson_bounds f agi c d
  have hb2 := saverPerson_bounds f agi c (d + i)
  unfold saverForm saverStat
  refine ⟨?_, by omega, ?_⟩
  · unfold saverPerson roundDollar pos
    have : min (max 0 (c - (d + i))) 2000 ≤ min (max 0 (c - d)) 2000 := by omega
    have := Int.mul_le_mul_of_nonneg_right this hp.1
    omega
  · unfold saverPerson roundDollar pos
    have hm : min (max 0 (c - d)) 2000 - min (max 0 (c - (d + i))) 2000 ≤ i := by omega
    have hm0 : 0 ≤ min (max 0 (c - d)) 2000 - min (max 0 (c - (d + i))) 2000 := by omega
    have := Int.mul_le_mul_of_nonneg_left hm hp.1
    generalize saverPercent f agi = p at *
    have e : p * (min (max 0 (c - d)) 2000 - min (max 0 (c - (d + i))) 2000) =
        min (max 0 (c - d)) 2000 * p - min (max 0 (c - (d + i))) 2000 * p := by
      rw [Int.mul_sub, Int.mul_comm p, Int.mul_comm p]
    have e2 : p * i = i * p := Int.mul_comm _ _
    omega

/-- The grid's example: joint AGI $15,000, $3,000 contributed, $2,500 from an inherited IRA: per person $1,000 (form)
against $250 (statute) for the contributor at 50%. -/
theorem saver_example : saverForm .mfj 15000 3000 0 2500 = 1000 ∧ saverStat .mfj 15000 3000 0 2500 = 250 := by decide

/-! ## 3. Form 2441: deemed earned income for an unmarried student -/

/-- §21(d)(1)(A)–(B), (d)(2): the expenses taken into account may not exceed earned income (unmarried: the
individual's own; married: the lesser of the two), and only "a spouse who is a student" or incapable is deemed to earn
$250/$500 a month. The model's `cdccExpenses` with no deeming for an unmarried filer. Form 2441 (2025) line 4 and
instructions ("These rules for a spouse who was a student or disabled also apply to you if you were a student or
disabled"): an unmarried full-time student for 12 months enters $3,000 (one person) or $6,000 (two or more) on line 4. -/
def deemed (qualifying : Nat) : Int := if qualifying ≥ 2 then 6000 else 3000

/-- **For an unmarried full-time student with no earnings the form's line 6 is up to $3,000/$6,000; the statute's
is zero** — so the form allows a credit of up to 35% × $3,000/$6,000 before the tax limit, the statute none. -/
theorem cdcc_unmarried_student (n : Nat) (hn : 1 ≤ n) (expenses agi : Int) (he : 0 ≤ expenses) :
    cdccExpenses n expenses 0 0 0 false = 0 ∧
    cdccExpenses n expenses 0 (deemed n) 0 false = min (min expenses (cdccDollarLimit n 0)) (deemed n) := by
  unfold cdccExpenses cdccDollarLimit deemed pos
  constructor <;> (try split) <;> simp <;> omega

end TaxCode.Forms.GridFindings

#print axioms TaxCode.Forms.GridFindings.magi_gap
#print axioms TaxCode.Forms.GridFindings.senior_gap
#print axioms TaxCode.Forms.GridFindings.car_gap
#print axioms TaxCode.Forms.GridFindings.saver_inherited
#print axioms TaxCode.Forms.GridFindings.cdcc_unmarried_student
