import TaxCode.Individual.D.Basic
import TaxCode.Individual.D.EICTableData

/-!
# §32 Earned income credit, tax year 2025

Source: 26 U.S.C. §32 (OLRC 119-138; the 2025 Act did not amend §32's amounts). Percentages are statutory
(§32(b)(1)); the dollar amounts of §32(b)(2) and §32(i)(1) are indexed under §32(j) and taken from Rev. Proc.
2024-40 §3.06 (2025):

| children | credit % | phase-out % | earned income amount | threshold (other / MFJ) | max credit | completed (other / MFJ) |
|---|---|---|---|---|---|---|
| 0 | 7.65 | 7.65 | 8,490 | 10,620 / 17,730 | 649 | 19,104 / 26,214 |
| 1 | 34 | 15.98 | 12,730 | 23,350 / 30,470 | 4,328 | 50,434 / 57,554 |
| 2 | 40 | 21.06 | 17,880 | 23,350 / 30,470 | 7,152 | 57,310 / 64,430 |
| 3+ | 45 | 21.06 | 17,880 | 23,350 / 30,470 | 8,046 | 61,555 / 68,675 |

Investment-income limit (§32(i)(1) as indexed): $11,950 (Rev. Proc. 2024-40 §3.06(2)).

Three versions are modelled:
* `eicScaled` — the statute exactly, in units of 1/10000 dollar: §32(a)(1) "credit percentage of so much of the
  taxpayer's earned income ... as does not exceed the earned income amount", limited by §32(a)(2): "the excess (if
  any) of (A) the credit percentage of the earned income amount, over (B) the phaseout percentage of so much of the
  adjusted gross income (or, if greater, the earned income) ... as exceeds the phaseout amount";
* `eicTab` — the IRS EIC Table of Pub. 596 (§32(f): "determined under tables prescribed by the Secretary" with
  "income brackets of not greater than $50"), reverse-engineered and checked against all 1,374 rows × 8 columns;
* `eicWorksheet` — EIC Worksheet A: look up earned income, and AGI when AGI is at or above the threshold, and take
  the smaller.
-/

namespace TaxCode.Individual.D
open TaxCode.Individual

structure EicParams where
  cp : Int          -- credit percentage, basis points (§32(b)(1))
  pp : Int          -- phaseout percentage, basis points (§32(b)(1))
  eia : Int         -- earned income amount (§32(b)(2)(A), indexed)
  thrSingle : Int   -- phaseout amount (§32(b)(2)(A), indexed)
  thrJoint : Int    -- phaseout amount + §32(b)(2)(B) joint increase, indexed
  maxCredit : Int   -- Rev. Proc. 2024-40 "Maximum Amount of Credit"
  coSingle : Int    -- Rev. Proc. 2024-40 "Completed Phaseout Amount"
  coJoint : Int
  deriving Repr

/-- §32(b) and Rev. Proc. 2024-40 §3.06(1), by number of qualifying children (3 means "3 or more"). -/
def eicParams : Nat → EicParams
  | 0 => ⟨765, 765, 8490, 10620, 17730, 649, 19104, 26214⟩
  | 1 => ⟨3400, 1598, 12730, 23350, 30470, 4328, 50434, 57554⟩
  | 2 => ⟨4000, 2106, 17880, 23350, 30470, 7152, 57310, 64430⟩
  | _ => ⟨4500, 2106, 17880, 23350, 30470, 8046, 61555, 68675⟩

def EicParams.thr (p : EicParams) (joint : Bool) : Int := if joint then p.thrJoint else p.thrSingle
def EicParams.co (p : EicParams) (joint : Bool) : Int := if joint then p.coJoint else p.coSingle

/-- §32(i)(1) as indexed: $11,950 for 2025. -/
def eicInvestmentLimit : Int := 11950

/-- §32(a)(1)–(2), exactly, in 1/10000 dollars. -/
def eicScaled (cp pp eia thr earned agi : Int) : Int :=
  pos (min (cp * min earned eia) (cp * eia - pp * pos (max agi earned - thr)))

/-- The statute rounded to the nearest dollar. -/
def eicStatute (k : Nat) (joint : Bool) (earned agi : Int) : Int :=
  let p := eicParams k
  roundDollar (eicScaled p.cp p.pp p.eia (p.thr joint) earned agi) 10000

/-- The IRS EIC Table (Pub. 596, 2025) for one amount `x`: zero at or past the completed phase-out; otherwise the
credit at the midpoint of the $50 band `[a, b)` (the last band ends at the completed phase-out amount), rounded to the
nearest dollar, with the published (rounded) maximum credit — except that a band with a kink of the formula strictly
inside it (the earned income amount, or the threshold) shows the maximum credit. This rule reproduces every cell. -/
def eicTab (cp pp eia thr mx co : Int) (x : Int) : Int :=
  if x ≤ 0 ∨ co ≤ x then 0 else
  let a := x / 50 * 50
  let b := min (a + 50) co
  if (a < eia ∧ eia < b) ∨ (a < thr ∧ thr < b) then mx else
  let m := a + b   -- twice the midpoint
  let v := max 0 (min (cp * m) (20000 * mx - pp * max 0 (m - 2 * thr)))
  (v + 10000) / 20000

def eicTable (k : Nat) (joint : Bool) (x : Int) : Int :=
  let p := eicParams k
  eicTab p.cp p.pp p.eia (p.thr joint) p.maxCredit (p.co joint) x

/-- EIC Worksheet A (Pub. 596 / Form 1040 instructions): line 2 looks up earned income; if AGI differs and is at or
above the threshold, AGI is looked up too and the smaller amount is the credit. -/
def eicWorksheet (k : Nat) (joint : Bool) (earned agi : Int) : Int :=
  if agi < (eicParams k).thr joint then eicTable k joint earned
  else min (eicTable k joint earned) (eicTable k joint agi)

/-! ## From a household -/

/-- §32(c)(3): a §152(c) qualifying child (under 19, a full-time student under 24, or disabled; living with the
taxpayer more than half the year), counted only with an SSN valid for employment (§32(c)(3)(D), (m)). -/
def isEicChild (d : Dependent) : Bool :=
  (d.age < 19 || (d.student && d.age < 24) || d.disabled) && d.monthsWithTaxpayer > 6 && d.ssn

def eicChildren (h : Household) : Nat := min 3 (h.dependents.filter isEicChild).length

/-- §32(i)(2) disqualified income, from what `Household` records: taxable and tax-exempt interest, dividends, and
capital gain net income (§1222(9): gains over losses, if positive). Rents, royalties and passive income are not in
`Household`. -/
def disqualifiedIncome (h : Household) : Int :=
  h.taxableInterest + h.taxExemptInterest + h.ordinaryDividends + pos (h.shortTermGains + h.longTermGains)

/-- §32(c)(1)(A)(ii)(II): with no qualifying child, the individual (or, if married, either spouse) is 25 to 64. -/
def ageOk (p : Person) : Bool := 25 ≤ p.age && p.age < 65

/-- §32(c)(1) eligibility and §32(d)(1) (married must file jointly; the separated-spouse exception of §32(d)(2)(B)
is not modelled). -/
def eicEligible (h : Household) : Bool :=
  h.filing != .mfs && !h.canBeClaimedAsDependent &&
    (0 < eicChildren h || ageOk h.head || (match h.spouse with | some s => ageOk s | none => false))

/-- The credit as allowed: table amounts (§32(f)(1)), worksheet A, and the §32(i) investment-income denial. -/
def eic2025 (h : Household) (earned agi : Int) : Int :=
  if !eicEligible h ∨ eicInvestmentLimit < disqualifiedIncome h then 0
  else eicWorksheet (eicChildren h) (h.filing == .mfj) earned agi

/-! ## Tests -/

/-- Rev. Proc. 2024-40's "Maximum Amount of Credit" is the credit percentage times the earned income amount,
rounded to the nearest dollar ($649.485 becomes $649 for no children). -/
theorem maxCredit_is_rounded :
    ∀ k ∈ [0, 1, 2, 3], roundDollar ((eicParams k).cp * (eicParams k).eia) 10000 = (eicParams k).maxCredit := by
  decide

/-- Rev. Proc. 2024-40's "Completed Phaseout Amount" is the threshold plus (rounded maximum credit ÷ phase-out
percentage), rounded to the nearest dollar. (So for 3+ children 2.7 cents of formula credit remain at $61,555.) -/
theorem completed_phaseout_consistent : ∀ k ∈ [0, 1, 2, 3], ∀ j ∈ [false, true],
    roundDollar ((eicParams k).thr j * (eicParams k).pp + 10000 * (eicParams k).maxCredit) (eicParams k).pp
      = (eicParams k).co j := by
  decide

/-- Every cell of the Pub. 596 (2025) EIC Table, checked at both ends of its band. -/
def tableCheck : Bool :=
  eicTable2025.all fun (a, vs) =>
    (List.range 8).all fun i =>
      let v := vs.getD i (-1)
      v < 0 || (eicTable (i % 4) (decide (4 ≤ i)) a == v && eicTable (i % 4) (decide (4 ≤ i)) (max a 1 + 48) == v)

#guard eicTable2025.length = 1374
#guard tableCheck
-- Pub. 596 (2025) footnotes to the starred cells (pp. 32, 38):
-- "at least $19,100 but less than $19,104, and you have no qualifying children ... your credit is $0"
#guard eicTable 0 false 19100 = 0 ∧ eicTable 0 false 19103 = 0 ∧ eicTable 0 false 19104 = 0
-- "at least $57,300 but less than $57,310, and you have two qualifying children ... your credit is $1"
#guard eicTable 2 false 57300 = 1 ∧ eicTable 2 false 57309 = 1 ∧ eicTable 2 false 57310 = 0
-- "at least $57,550 but less than $57,554, and you have one qualifying child ... your credit is $0" (MFJ column)
#guard eicTable 1 true 57550 = 0 ∧ eicTable 1 true 57553 = 0
-- "at least $61,550 but less than $61,555, and you have three qualifying children ... your credit is $1"
#guard eicTable 3 false 61550 = 1 ∧ eicTable 3 false 61554 = 1 ∧ eicTable 3 false 61555 = 0
-- (Review) Pub. 596 (2025): "at least $26,200 but less than $26,214" (MFJ, no qualifying child): "your credit is $1".
#guard eicTable 0 true 26200 = 1 ∧ eicTable 0 true 26213 = 1 ∧ eicTable 0 true 26214 = 0
-- Pub. 596 (2025) p. 29, Example: "single, you have one qualifying child, and the amount ... is $2,455, you would
-- enter $842."
#guard eicTable 1 false 2455 = 842
-- Pub. 596 (2025) Rule 6: "You can't claim the EIC unless your investment income is $11,950 or less."
#guard eicInvestmentLimit = 11950

/-! ## Properties -/

/-- The statute's credit is never negative and never above the credit percentage of the earned income amount. -/
theorem eicScaled_bounds (cp pp eia thr e a : Int) : 0 ≤ eicScaled cp pp eia thr e a := by
  unfold eicScaled pos; omega

theorem eicScaled_le_max (k : Nat) (j : Bool) (e a : Int) :
    let p := eicParams k
    eicScaled p.cp p.pp p.eia (p.thr j) e a ≤ p.cp * p.eia := by
  match k with
  | 0 | 1 | 2 | _ + 3 => cases j <;> simp [eicParams, EicParams.thr, eicScaled, pos] <;> omega

/-- The phase-out is monotone: more AGI never raises the credit. -/
theorem eicScaled_antitone_agi (k : Nat) (j : Bool) (e a : Int) :
    let p := eicParams k
    eicScaled p.cp p.pp p.eia (p.thr j) e (a + 1) ≤ eicScaled p.cp p.pp p.eia (p.thr j) e a := by
  match k with
  | 0 | 1 | 2 | _ + 3 => cases j <;> simp [eicParams, EicParams.thr, eicScaled, pos] <;> omega

/-- The statute has no notch: one more dollar of income (earned income = AGI) changes the credit by at most the
credit percentage going up and at most the phase-out percentage going down. -/
theorem eicScaled_step (k : Nat) (j : Bool) (x : Int) :
    let p := eicParams k
    eicScaled p.cp p.pp p.eia (p.thr j) (x + 1) (x + 1) - eicScaled p.cp p.pp p.eia (p.thr j) x x ≤ p.cp ∧
    eicScaled p.cp p.pp p.eia (p.thr j) x x - eicScaled p.cp p.pp p.eia (p.thr j) (x + 1) (x + 1) ≤ p.pp := by
  match k with
  | 0 | 1 | 2 | _ + 3 => cases j <;> simp [eicParams, EicParams.thr, eicScaled, pos] <;> omega

/-- **Worksheet = statute.** Looking up earned income and (when at or over the threshold) AGI and taking the smaller
gives exactly the statute's "AGI (or, if greater, the earned income)" rule, for every number of children. -/
theorem worksheet_rule_exact (k : Nat) (j : Bool) (e a : Int) :
    let p := eicParams k
    eicScaled p.cp p.pp p.eia (p.thr j) e a =
      if a < p.thr j then eicScaled p.cp p.pp p.eia (p.thr j) e e
      else min (eicScaled p.cp p.pp p.eia (p.thr j) e e) (eicScaled p.cp p.pp p.eia (p.thr j) a a) := by
  match k with
  | 0 | 1 | 2 | _ + 3 => cases j <;> simp [eicParams, EicParams.thr, eicScaled, pos] <;> split <;> omega

/-! ### Table versus statute: a proved bound

`10000 * table - statute` (in 1/10000 dollar) lies in `[lo, hi]` for every earned income `x ≥ 0` (with AGI = earned
income). The bounds are attained, so they are tight. The table can pay up to $13.50 more than the formula (3+
children, at $17,850: formula $8,032.50, table $8,046) and up to $11.05 less. -/

set_option maxHeartbeats 1000000

theorem table_vs_statute_0 (j : Bool) (x : Int) (hx : 0 ≤ x) :
    let p := eicParams 0
    10000 * eicTable 0 j x - eicScaled p.cp p.pp p.eia (p.thr j) x x ≥ -28900 ∧
    10000 * eicTable 0 j x - eicScaled p.cp p.pp p.eia (p.thr j) x x ≤ 25750 := by
  cases j <;> simp only [eicTable, eicParams, EicParams.thr, EicParams.co, eicScaled, eicTab, pos] <;>
    simp only [Bool.false_eq_true, ↓reduceIte] <;> repeat' split
  all_goals omega

theorem table_vs_statute_1 (j : Bool) (x : Int) (hx : 0 ≤ x) :
    let p := eicParams 1
    10000 * eicTable 1 j x - eicScaled p.cp p.pp p.eia (p.thr j) x x ≥ -76600 ∧
    10000 * eicTable 1 j x - eicScaled p.cp p.pp p.eia (p.thr j) x x ≤ 100000 := by
  cases j <;> simp only [eicTable, eicParams, EicParams.thr, EicParams.co, eicScaled, eicTab, pos] <;>
    simp only [Bool.false_eq_true, ↓reduceIte] <;> repeat' split
  all_goals omega

theorem table_vs_statute_2 (j : Bool) (x : Int) (hx : 0 ≤ x) :
    let p := eicParams 2
    10000 * eicTable 2 j x - eicScaled p.cp p.pp p.eia (p.thr j) x x ≥ -96000 ∧
    10000 * eicTable 2 j x - eicScaled p.cp p.pp p.eia (p.thr j) x x ≤ 120000 := by
  cases j <;> simp only [eicTable, eicParams, EicParams.thr, EicParams.co, eicScaled, eicTab, pos] <;>
    simp only [Bool.false_eq_true, ↓reduceIte] <;> repeat' split
  all_goals omega

theorem table_vs_statute_3 (j : Bool) (x : Int) (hx : 0 ≤ x) :
    let p := eicParams 3
    10000 * eicTable 3 j x - eicScaled p.cp p.pp p.eia (p.thr j) x x ≥ -110500 ∧
    10000 * eicTable 3 j x - eicScaled p.cp p.pp p.eia (p.thr j) x x ≤ 135000 := by
  cases j <;> simp only [eicTable, eicParams, EicParams.thr, EicParams.co, eicScaled, eicTab, pos] <;>
    simp only [Bool.false_eq_true, ↓reduceIte] <;> repeat' split
  all_goals omega

/-- The bounds are attained (tight): over by $13.50 at $17,850 (3+ children), under by $11.05 at $17,849. -/
theorem table_vs_statute_tight :
    let p := eicParams 3
    10000 * eicTable 3 false 17850 - eicScaled p.cp p.pp p.eia (p.thr false) 17850 17850 = 135000 ∧
    10000 * eicTable 3 false 17849 - eicScaled p.cp p.pp p.eia (p.thr false) 17849 17849 = -110500 := by
  decide

/-- The table's $50 bands make small notches the statute does not have: one more dollar can cost $12 of credit
(joint return, 3+ children, $30,499 → $30,500: the band holding the $30,470 threshold shows the maximum). -/
theorem table_notch : eicTable 3 true 30499 - eicTable 3 true 30500 = 12 := by decide

theorem table_step_le_12 (j : Bool) (x : Int) : eicTable 3 j x - eicTable 3 j (x + 1) ≤ 12 := by
  cases j <;> simp only [eicTable, eicParams, EicParams.thr, EicParams.co, eicTab] <;>
    simp only [Bool.false_eq_true, ↓reduceIte] <;> repeat' split
  all_goals omega

/-- With no children the statute's maximum is $649.485, not $649: the unrounded statutory credit is still positive
at $19,104–$19,109 (where the table has stopped), though below 50 cents. -/
theorem zero_child_tail :
    let p := eicParams 0
    0 < eicScaled p.cp p.pp p.eia (p.thr false) 19109 19109 ∧ eicTable 0 false 19109 = 0 ∧
    eicStatute 0 false 19109 19109 = 0 ∧ eicScaled p.cp p.pp p.eia (p.thr false) 19110 19110 = 0 := by
  decide

/-! ### The §32(i) cliff -/

/-- A single parent of three children, earned income and AGI $20,000. -/
def cliffFamily (interest : Int) : Household :=
  { filing := .hoh, head := ⟨35, false⟩, dependents := [{ age := 4 }, { age := 6 }, { age := 8 }],
    taxableInterest := interest }

/-- **Cliff.** $1 more of interest (from $11,950 to $11,951) removes the whole credit: $8,046. The cliff is the full
credit at that point, so the largest possible cliff is the largest credit, $8,046. -/
theorem investment_income_cliff :
    eic2025 (cliffFamily 11950) 20000 20000 = 8046 ∧ eic2025 (cliffFamily 11951) 20000 20000 = 0 := by
  decide

/-- The table never exceeds the published maximum credit, so no §32(i) cliff exceeds $8,046 (3+ children). -/
theorem table_le_max (k : Nat) (j : Bool) (x : Int) : eicTable k j x ≤ (eicParams k).maxCredit := by
  match k with
  | 0 | 1 | 2 | _ + 3 =>
    cases j <;> simp only [eicTable, eicParams, EicParams.thr, EicParams.co, eicTab] <;>
      simp only [Bool.false_eq_true, ↓reduceIte] <;> repeat' split
    all_goals omega

end TaxCode.Individual.D
