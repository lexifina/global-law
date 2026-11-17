/-!
# Pub. 525 Worksheets 2 and 2a (recoveries of itemized deductions) against §111(a) and the §164(b)(6) cap

Reported claim (user Q&A page, April 2025): Worksheet 2's steps "don't properly account for" the SALT-cap excess.
Poster's example: paid $15,000 state income tax, deducted $10,000 because of the cap, refund $3,000; the poster says
"only 2/3 of that refund should be taxable" ($2,000) and that the worksheet gives a different result.

Form text: Publication 525 (2024), Worksheet 2a "Computations for Worksheet 2, lines 1a and 1b" (p. 27) and
Worksheet 2 "Recoveries of Itemized Deductions" (p. 28); the 2025 edition (pp. 26–27) has the same lines (footnote
"1a" renumbered "1"). Lines quoted on each definition.

Statute: §111(a) "Gross income does not include income attributable to the recovery during the taxable year of any
amount deducted in any prior taxable year to the extent such amount did not reduce the amount of tax imposed by this
chapter"; §164(b)(6) (aggregate state and local taxes limited to $10,000, $5,000 married filing separately);
§164(b)(5) (sales taxes in lieu of income taxes); §63(b), (d), (e) (the larger of the standard deduction and itemized
deductions). The IRS's reading, Rev. Rul. 2019-11 (Holding): include "the lesser of (1) the difference between the
taxpayer's total itemized deductions taken in the prior year and the amount of itemized deductions the taxpayer
would have taken in the prior year had the taxpayer paid the proper amount of state and local tax or (2) the
difference between the taxpayer's itemized deductions taken in the prior year and the standard deduction".

`statute` below is that counterfactual: the prior year redone as if only the net amounts had been paid (income-tax
or sales-tax election redone, cap reapplied, standard deduction if larger), and the recovery included to the extent
taxable income, floored at zero, rises.

Domain (the worksheet's own: no AMT, no unused credits, no "itemized deductions limited"; Worksheet 2 line 5 = 0,
i.e. no earlier refund for that year): whole dollars; all amounts ≥ 0 except prior taxable income; the taxpayer
deducted income taxes (`salesAlt ≤ incTax`); refunds no larger than the taxes paid; other recoveries no larger than
the other itemized deductions; a dollar of positive taxable income bears tax (no 0% bracket effects).
-/

namespace TaxCode.Forms.Reported.Pub525

structure Inputs where
  cap : Int        -- §164(b)(6): 10,000 (5,000 married filing separately)
  incTax : Int     -- state and local income taxes paid in the prior year (Schedule A line 5a)
  salesAlt : Int   -- general sales taxes the taxpayer could have deducted instead (§164(b)(5))
  propTax : Int    -- real estate and personal property taxes paid (Schedule A lines 5b + 5c)
  otherItem : Int  -- other itemized deductions allowed (Schedule A lines 8–16)
  stdDed : Int     -- prior-year standard deduction (Worksheet 2 line 7; 0 for Form 1040-NR)
  ti : Int         -- prior-year taxable income (Worksheet 2 line 10; may be negative)
  rInc : Int       -- income tax refund (Form 1099-G)
  rProp : Int      -- real estate / personal property tax refund
  rOther : Int     -- other Schedule A recoveries (Worksheet 2 line 2, footnote-limited to the amount deducted)
  deriving Repr, DecidableEq

/-- The domain stated in the header. -/
def Domain (i : Inputs) : Prop :=
  0 < i.cap ∧ 0 ≤ i.salesAlt ∧ i.salesAlt ≤ i.incTax ∧ 0 ≤ i.propTax ∧ 0 ≤ i.otherItem ∧ 0 ≤ i.stdDed ∧
  0 ≤ i.rInc ∧ i.rInc ≤ i.incTax ∧ 0 ≤ i.rProp ∧ i.rProp ≤ i.propTax ∧ 0 ≤ i.rOther ∧ i.rOther ≤ i.otherItem

section Prior
variable (i : Inputs)
/-- Schedule A line 5d: income taxes + real estate + personal property taxes. -/
def s5d : Int := i.incTax + i.propTax
/-- Schedule A line 5e: "Enter the smaller of line 5d or $10,000 ($5,000 if married filing separately)". -/
def s5e : Int := min (s5d i) i.cap
/-- Schedule A line 17: total itemized deductions. -/
def s17 : Int := s5e i + i.otherItem
end Prior

/-! ## The statute (§111(a) with §164(b)(5), (6) and §63, as Rev. Rul. 2019-11 applies them) -/

section Statute
variable (i : Inputs)
/-- The state and local tax deduction had only the net taxes been paid: the larger of net income taxes and sales
taxes (§164(b)(5) election redone), plus net property taxes, capped (§164(b)(6)). -/
def saltCf : Int := min i.cap (max (i.incTax - i.rInc) i.salesAlt + (i.propTax - i.rProp))
/-- Itemized deductions had only the net amounts been paid. -/
def itemCf : Int := saltCf i + i.otherItem - i.rOther
/-- §63: the deduction the taxpayer would then have taken (standard deduction if larger). -/
def dedCf : Int := max i.stdDed (itemCf i)
/-- Prior-year taxable income had only the net amounts been paid. -/
def tiCf : Int := i.ti + s17 i - dedCf i
/-- **§111(a)**: the recovery is income only to the extent the deduction reduced tax, i.e. to the extent it lowered
taxable income above zero. -/
def statute : Int := max 0 (max 0 (tiCf i) - max 0 i.ti)
end Statute

/-! ## Worksheet 2a, line by line -/

/-- Worksheet 2a line 5 has three outcomes: blank (line 4 "No ... go to line 6"), STOP ("No. [STOP] None of the
refunds on line 1 or 2 are taxable"), or an amount ("Yes. Subtract line 4 from line 3"). -/
inductive L5 where
  | blank | stop | amt (v : Int)
  deriving Repr, DecidableEq

section W2a
variable (i : Inputs)
/-- Line 1: "Enter the income tax refund from Form(s) 1099-G (or similar statement)". -/
def a1 : Int := i.rInc
/-- Line 2: "Enter the refunds received for state and local real estate taxes and state and local personal property
taxes". -/
def a2 : Int := i.rProp
/-- Line 3: "Total state and local refunds. Add lines 1 and 2. But don't enter more than the amount of your state and
local taxes shown on your 2023 Schedule A, line 5d". -/
def a3 : Int := min (a1 i + a2 i) (s5d i)
/-- Line 4: "Is the amount of state and local income taxes (or general sales taxes), real estate taxes, and personal
property taxes paid in 2023 (generally, this is the amount reported on your 2023 Schedule A, line 5d) more than the
amount on your 2023 Schedule A, line 5e? No. Enter the amount from line 3 on line 4 and go to line 6. Yes. Subtract
the amount on your 2023 Schedule A, line 5e, from [line 5d]". -/
def a4 : Int := if s5e i < s5d i then s5d i - s5e i else a3 i
/-- Line 5: "Is the amount on line 3 more than the amount on line 4? No. [STOP] None of the refunds on line 1 or 2
are taxable. Yes. Subtract line 4 from line 3". Blank when line 4 sent the filer to line 6. -/
def a5 : L5 := if s5e i < s5d i then (if a4 i < a3 i then .amt (a3 i - a4 i) else .stop) else .blank
/-- Line 6: "Add lines 1 and 2". -/
def a6 : Int := a1 i + a2 i
/-- Line 7 × line 6. Line 7: "If line 5 is blank, enter the amount from line 1. If there is an amount on line 5,
divide line 1 by line 6. Then multiply by the amount on line 5". (After STOP nothing is entered: 0.) Kept scaled by
line 6 so the fraction is exact. -/
def a7x6 : Int := match a5 i with | .blank => a1 i * a6 i | .stop => 0 | .amt v => a1 i * v
/-- Line 8 × line 6: the same with line 2. -/
def a8x6 : Int := match a5 i with | .blank => a2 i * a6 i | .stop => 0 | .amt v => a2 i * v
/-- Lines 7 + 8 (= Worksheet 2 lines 1a + 1b), a whole number: line 6 if line 5 is blank, 0 after STOP, line 5
otherwise. -/
def a78 : Int := match a5 i with | .blank => a6 i | .stop => 0 | .amt v => v

/-- The two scaled lines add up to line 6 × `a78`: lines 7 and 8 split `a78` in proportion to the two refunds. -/
theorem lines78 : a7x6 i + a8x6 i = a6 i * a78 i := by
  unfold a7x6 a8x6 a78 a6; cases a5 i <;> simp [Int.add_mul]
end W2a

/-! ## Worksheet 2, line by line, given lines 1a + 1b -/

section W2
variable (i : Inputs) (l1ab : Int)
/-- Line 3: "Add lines 1a, 1b, and 2" (line 2: other Schedule A recoveries). -/
def b3 : Int := l1ab + i.rOther
/-- Lines 4–6: itemized deductions (Schedule A line 17) less line 5 "any amount previously refunded" (0 here). -/
def b6 : Int := s17 i - 0
/-- Line 8: "Subtract line 7 from line 6. If the result is zero or less, stop here. The amounts on lines 1a, 1b, and
2 aren't taxable" (line 7: standard deduction). `none` = stopped. -/
def b8 : Option Int := if b6 i - i.stdDed ≤ 0 then none else some (b6 i - i.stdDed)
/-- Line 9: "Enter the smaller of line 3 or line 8". -/
def b9 : Option Int := (b8 i).map (min (b3 i l1ab))
/-- Line 11: "If line 10 is zero or more, enter the amount from line 9. If line 10 is a negative amount, add lines 9
and 10 and enter the result (but not less than zero)" (line 10: prior-year taxable income). 0 after a stop. -/
def b11 : Int := match b9 i l1ab with
  | none => 0
  | some v => if 0 ≤ i.ti then v else max 0 (v + i.ti)
end W2

/-- The worksheets as the filer completes them, lines 1a + 1b from Worksheet 2a (footnote 1a not binding). -/
def worksheet (i : Inputs) : Int := b11 i (a78 i)

/-! ## Worksheet = statute -/

/-- Lines 7 + 8 in closed form: line 6 on the "No" branch of line 4, else line 3 − line 4 floored at zero (STOP). -/
theorem a78_val (i : Inputs) : a78 i = if s5e i < s5d i then max 0 (a3 i - a4 i) else a6 i := by
  unfold a78 a5
  by_cases h1 : s5e i < s5d i <;> by_cases h2 : a4 i < a3 i <;> simp only [h1, h2, ↓reduceIte] <;> omega

/-- Worksheet 2a's lines 1a + 1b are exactly the drop in the capped SALT deduction when the income-tax election
stays the larger one after the refund. -/
theorem a78_eq (i : Inputs) (h : Domain i) (hs : i.salesAlt ≤ i.incTax - i.rInc) :
    a78 i = s5e i - saltCf i := by
  unfold Domain at h
  rw [a78_val]; unfold a4 saltCf
  by_cases h1 : s5e i < s5d i
  · rw [if_pos h1, if_pos h1]; unfold a3 a2 a1 s5e s5d at *; omega
  · rw [if_neg h1]; unfold a6 a2 a1 s5e s5d at *; omega

/-- Worksheet 2 line 11 in closed form. -/
theorem b11_val (i : Inputs) (x : Int) : b11 i x =
    if s17 i - i.stdDed ≤ 0 then 0
    else if 0 ≤ i.ti then min (x + i.rOther) (s17 i - i.stdDed)
    else max 0 (min (x + i.rOther) (s17 i - i.stdDed) + i.ti) := by
  unfold b11 b9 b8 b6 b3
  by_cases h : s17 i - 0 - i.stdDed ≤ 0
  · have h' : s17 i - i.stdDed ≤ 0 := by omega
    simp only [h, h', if_true, Option.map_none]
  · have h' : ¬ s17 i - i.stdDed ≤ 0 := by omega
    simp only [h', if_false, Option.map_some, Int.sub_zero]

/-- Worksheet 2 line 11 is the §111(a) amount for any lines 1a + 1b equal to the drop in the SALT deduction. -/
theorem b11_eq (i : Inputs) (h : Domain i) (x : Int) (hx : x = s5e i - saltCf i) : b11 i x = statute i := by
  unfold Domain at h
  have h0 : 0 ≤ s5e i - saltCf i := by unfold s5e saltCf s5d; omega
  have h17 : s17 i = s5e i + i.otherItem := rfl
  rw [b11_val]; unfold statute tiCf dedCf itemCf
  rw [h17]; subst hx
  generalize s5e i = E at *; generalize saltCf i = C at *
  by_cases p1 : E + i.otherItem - i.stdDed ≤ 0
  · rw [if_pos p1]; omega
  · rw [if_neg p1]
    by_cases p2 : 0 ≤ i.ti
    · rw [if_pos p2]; omega
    · rw [if_neg p2]; omega

/-- **Worksheets 2a and 2 give exactly the §111(a) amount (Rev. Rul. 2019-11) for all inputs in the domain**, when
the income-tax election stays the larger one after the refund (net income tax ≥ sales-tax alternative). -/
theorem worksheet_eq_statute (i : Inputs) (h : Domain i) (hs : i.salesAlt ≤ i.incTax - i.rInc) :
    worksheet i = statute i :=
  b11_eq i h _ (a78_eq i h hs)

/-! ## The poster's example and Rev. Rul. 2019-11 Situations 1–4 -/

/-- Poster: $15,000 state income tax paid, $10,000 deducted (cap), $3,000 refund. Other itemized deductions $10,000
(mortgage interest, assumed), 2023 single standard deduction $13,850, taxable income $60,000 (assumed; any positive
amount gives the same result). -/
def poster : Inputs := ⟨10000, 15000, 0, 0, 10000, 13850, 60000, 3000, 0, 0⟩

/-- The poster's "2/3 taxable" rule: refund × deducted / paid. -/
def posterRule (refund deducted paid : Int) : Int := refund * deducted / paid

/-- **Worksheet 2a stops at line 5 ("None of the refunds ... are taxable"): $0, and so does the statute; the poster's
pro-rata rule gives $2,000.** Worksheet 2a: line 3 = $3,000, line 4 = $15,000 − $10,000 = $5,000, line 5 "No". -/
theorem poster_example :
    a3 poster = 3000 ∧ a4 poster = 5000 ∧ a5 poster = .stop ∧ worksheet poster = 0 ∧ statute poster = 0 ∧
    posterRule 3000 10000 15000 = 2000 := by decide

/-- Rev. Rul. 2019-11 facts (single, 2018 standard deduction $12,000; other itemized deductions = total itemized −
SALT deduction; taxable income not stated, taken as $50,000; no sales-tax alternative). -/
def sit1 : Inputs := ⟨10000, 5000, 0, 4000, 5000, 12000, 50000, 1500, 0, 0⟩
def sit2 : Inputs := ⟨10000, 7000, 0, 5000, 5000, 12000, 50000, 750, 0, 0⟩
def sit3 : Inputs := ⟨10000, 6000, 0, 5000, 5000, 12000, 50000, 1500, 0, 0⟩
def sit4 : Inputs := ⟨10000, 6000, 0, 4250, 2500, 12000, 50000, 1000, 0, 0⟩

/-- **The worksheet and the statute model both give the ruling's answers**: $1,500, $0, $500, $500 (itemized
deductions $14,000 / $15,000 / $15,000 / $12,500 as the ruling states). -/
theorem revRul_2019_11 :
    s17 sit1 = 14000 ∧ s17 sit2 = 15000 ∧ s17 sit3 = 15000 ∧ s17 sit4 = 12500 ∧
    worksheet sit1 = 1500 ∧ statute sit1 = 1500 ∧ worksheet sit2 = 0 ∧ statute sit2 = 0 ∧
    worksheet sit3 = 500 ∧ statute sit3 = 500 ∧ worksheet sit4 = 500 ∧ statute sit4 = 500 := by decide

/-- The poster's pro-rata rule is never below the statute's SALT amount (scaled by the taxes paid `T`): for a refund
`r ≤ T` of capped taxes `T ≥ cap`, `T × max(0, r − (T − cap)) ≤ r × cap`, with equality only when `r = T` or the cap
does not bind. So the "2/3" reading overstates, it does not correct an understatement. -/
theorem posterRule_ge (T r cap : Int) (hr : 0 ≤ r) (hrT : r ≤ T) (hc : 0 < cap) (hT : cap ≤ T) :
    T * max 0 (r - (T - cap)) ≤ r * cap := by
  have e : T * (r - (T - cap)) + (T - r) * (T - cap) = r * cap := by
    simp only [Int.mul_sub, Int.sub_mul, Int.mul_comm r T]; omega
  have n1 : 0 ≤ (T - r) * (T - cap) := Int.mul_nonneg (by omega) (by omega)
  have n2 : 0 ≤ r * cap := Int.mul_nonneg hr (by omega)
  by_cases hp : 0 ≤ r - (T - cap)
  · rw [Int.max_eq_right hp]; omega
  · rw [Int.max_eq_left (by omega)]; simp; omega

/-! ## Footnote 1a and the sales-tax election under the cap

Worksheet 2 footnote 1a: "Don't enter more than the excess of your state and local income tax deduction over your
state and local general sales taxes you could have deducted." When the refund makes the sales-tax alternative the
larger one, this footnote is the only limit. Two readings (no property-tax refund, so line 1a is a whole number):
reading 1 compares the uncapped amounts (income taxes − sales taxes, the pre-2018 meaning); reading 2 compares the
deductions after the cap (line 5e − the capped deduction with sales taxes). -/

/-- Line 1a under reading 1. -/
def l1aReading1 (i : Inputs) : Int := min (a78 i) (i.incTax - i.salesAlt)
/-- Line 1a under reading 2. -/
def l1aReading2 (i : Inputs) : Int := min (a78 i) (s5e i - min i.cap (i.salesAlt + i.propTax))

/-- **Reading 2 is exact for every input in the domain** (no property-tax refund): the worksheet gives the §111(a)
amount whichever election is larger after the refund. -/
theorem reading2_eq_statute (i : Inputs) (h : Domain i) (hp : i.rProp = 0) :
    b11 i (l1aReading2 i) = statute i := by
  apply b11_eq i h
  unfold Domain at h
  unfold l1aReading2 saltCf; rw [a78_val]; unfold a4
  by_cases h1 : s5e i < s5d i
  · rw [if_pos h1, if_pos h1]; unfold a3 a2 a1 s5e s5d at *; rw [hp]; omega
  · rw [if_neg h1]; unfold a6 a2 a1 s5e s5d at *; rw [hp]; omega

/-- **Reading 1 overstates lines 1a + 1b by exactly** `min(a, I − S) − max(0, min(a, cap − S − P))`, where
`a = r − (I + P − cap)` is Worksheet 2a line 5, when the cap binds (`I + P > cap`) and line 5 is positive; it agrees
otherwise. The overstatement is at most the cap ($10,000; $5,000 married filing separately) and at most `I − S`. -/
theorem reading1_excess (i : Inputs) (h : Domain i) (hp : i.rProp = 0) :
    l1aReading1 i - l1aReading2 i =
      (if i.cap < i.incTax + i.propTax ∧ i.incTax + i.propTax - i.cap < i.rInc then
        min (i.rInc - (i.incTax + i.propTax - i.cap)) (i.incTax - i.salesAlt) -
          max 0 (min (i.rInc - (i.incTax + i.propTax - i.cap)) (i.cap - i.salesAlt - i.propTax))
      else 0) ∧
    0 ≤ l1aReading1 i - l1aReading2 i ∧ l1aReading1 i - l1aReading2 i ≤ min i.cap (i.incTax - i.salesAlt) := by
  unfold Domain at h
  unfold l1aReading1 l1aReading2; rw [a78_val]; unfold a4
  by_cases h1 : s5e i < s5d i
  · rw [if_pos h1, if_pos h1]; unfold a3 a2 a1 s5e s5d at *; rw [hp]
    by_cases c : i.cap < i.incTax + i.propTax ∧ i.incTax + i.propTax - i.cap < i.rInc
    · rw [if_pos c]; omega
    · rw [if_neg c]; omega
  · rw [if_neg h1]; unfold a6 a2 a1 s5e s5d at *; rw [hp]
    have c : ¬ (i.cap < i.incTax + i.propTax ∧ i.incTax + i.propTax - i.cap < i.rInc) := by omega
    rw [if_neg c]; omega

/-- The sales-tax case in dollars: income tax $50,000, sales tax alternative $45,000 (e.g. a year with a large
purchase), cap $10,000, refund $48,000. Net income tax $2,000 < sales tax, so the deduction would still have been
$10,000: nothing is taxable. Worksheet 2a line 5 = $8,000; reading 1 enters $5,000 on line 1a; reading 2 enters $0. -/
def salesCase : Inputs := ⟨10000, 50000, 45000, 0, 20000, 14600, 100000, 48000, 0, 0⟩

theorem sales_case :
    statute salesCase = 0 ∧ a78 salesCase = 8000 ∧ b11 salesCase (l1aReading1 salesCase) = 5000 ∧
    b11 salesCase (l1aReading2 salesCase) = 0 := by decide

/-! ## A-2: the 2020–2023 editions of Worksheet 2a (Reddit r/tax claim, April 2024)

Publication 525 for 2020, 2021, 2022 and 2023 (irs-prior p525--2020.pdf ... p525--2023.pdf), Worksheet 2a line 4:
"No. Enter the amount from line 3 on line 4 and go to line 5." Line 5: "Is the amount on line 3 more than the amount
on line 4? No. [STOP] None of the refunds on line[s] 1 or 2 [is/are] taxable. Yes. Subtract line 4 from line 3".
Lines 7–8 had no "If line 5 is blank" bullet: "Divide line 1 by line 6. Then multiply by the amount on line 5".
The 2024 and 2025 editions say "go to line 6" and add the blank-line-5 bullets (modelled above as `a5`, `a78`). -/

/-- Line 5 of the 2020–2023 editions: reached on both branches of line 4. -/
def a5old (i : Inputs) : L5 := if a4 i < a3 i then .amt (a3 i - a4 i) else .stop
/-- Lines 7 + 8 of the 2020–2023 editions (line 7 + line 8 = line 5, or 0 after STOP). -/
def a78old (i : Inputs) : Int := match a5old i with | .blank => a6 i | .stop => 0 | .amt v => v
/-- Worksheets 2a and 2 as the 2020–2023 editions are completed. -/
def worksheetOld (i : Inputs) : Int := b11 i (a78old i)

/-- On the "No" branch line 4 = line 3, so line 5 is always "No. [STOP]": the 2020–2023 lines 1a + 1b are 0
whenever Schedule A line 5d is not more than line 5e (the cap does not bind). -/
theorem a78old_val (i : Inputs) : a78old i = if s5e i < s5d i then max 0 (a3 i - a4 i) else 0 := by
  unfold a78old a5old
  by_cases h1 : s5e i < s5d i
  · rw [if_pos h1]; by_cases h2 : a4 i < a3 i <;> simp only [h2, ↓reduceIte] <;> omega
  · rw [if_neg h1]
    have : a4 i = a3 i := by unfold a4; rw [if_neg h1]
    have h2 : ¬ a4 i < a3 i := by omega
    simp only [h2, ↓reduceIte]

/-- When the cap binds, the 2020–2023 and 2024–2025 editions agree. -/
theorem old_eq_new_capped (i : Inputs) (h : s5e i < s5d i) : worksheetOld i = worksheet i := by
  unfold worksheetOld worksheet; rw [a78old_val, a78_val, if_pos h, if_pos h]

/-- Worksheet 2 line 11 rises by between 0 and x when lines 1a + 1b rise from 0 to x. -/
theorem b11_lip (i : Inputs) (x : Int) (hx : 0 ≤ x) :
    0 ≤ b11 i x - b11 i 0 ∧ b11 i x - b11 i 0 ≤ x := by
  rw [b11_val, b11_val]
  by_cases p1 : s17 i - i.stdDed ≤ 0
  · rw [if_pos p1, if_pos p1]; omega
  · rw [if_neg p1, if_neg p1]
    by_cases p2 : 0 ≤ i.ti
    · rw [if_pos p2, if_pos p2]; omega
    · rw [if_neg p2, if_neg p2]; omega

/-- **The Reddit claim, proved for every input in the domain with the cap not binding** (Schedule A line 5d ≤ cap):
the 2020–2023 worksheet drops the state and local refunds entirely (line 11 as if lines 1a, 1b were 0), while §111(a)
— and the 2024–2025 worksheet — include them in full, subject only to the standard-deduction and negative-income
limits of Worksheet 2. The understatement is exactly `b11(refunds) − b11(0)`, between 0 and the refunds. -/
theorem old_nocap_gap (i : Inputs) (h : Domain i) (hs : i.salesAlt ≤ i.incTax - i.rInc) (hc : s5d i ≤ i.cap) :
    worksheetOld i = b11 i 0 ∧ worksheet i = b11 i (i.rInc + i.rProp) ∧ statute i = worksheet i ∧
    0 ≤ statute i - worksheetOld i ∧ statute i - worksheetOld i ≤ i.rInc + i.rProp := by
  have hD := h
  unfold Domain at hD
  have hn : ¬ s5e i < s5d i := by unfold s5e; omega
  have e1 : worksheetOld i = b11 i 0 := by unfold worksheetOld; rw [a78old_val, if_neg hn]
  have e2 : worksheet i = b11 i (i.rInc + i.rProp) := by
    unfold worksheet; rw [a78_val, if_neg hn]; rfl
  have e3 := (worksheet_eq_statute i h hs).symm
  have L := b11_lip i (i.rInc + i.rProp) (by omega)
  refine ⟨e1, e2, e3, ?_, ?_⟩ <;> rw [e3, e1, e2] <;> omega

/-- The Reddit-style example: $8,000 state income tax paid (under the $10,000 cap), $10,000 other itemized deductions,
$13,850 standard deduction, $60,000 taxable income, $1,000 refund. §111(a): $1,000; 2024–2025 worksheet: $1,000;
2020–2023 worksheet: line 4 = line 3 = $1,000, line 5 "No. [STOP]", $0. Rev. Rul. 2019-11 Situation 1 ($1,500 refund,
fully includible): 2020–2023 worksheet $0. -/
def redditCase : Inputs := ⟨10000, 8000, 0, 0, 10000, 13850, 60000, 1000, 0, 0⟩

theorem reddit_case :
    a3 redditCase = 1000 ∧ a4 redditCase = 1000 ∧ a5old redditCase = .stop ∧ a5 redditCase = .blank ∧
    worksheetOld redditCase = 0 ∧ worksheet redditCase = 1000 ∧ statute redditCase = 1000 ∧
    worksheetOld sit1 = 0 ∧ worksheet sit1 = 1500 ∧ statute sit1 = 1500 := by decide

/-- With a property-tax refund only (the case the Schedule 1 State and Local Income Tax Refund Worksheet sends to
Pub. 525): $6,000 income tax + $3,000 property tax paid, $500 property-tax refund. Old worksheet $0, statute $500. -/
theorem property_refund_case :
    worksheetOld ⟨10000, 6000, 0, 3000, 10000, 13850, 60000, 0, 500, 0⟩ = 0 ∧
    statute ⟨10000, 6000, 0, 3000, 10000, 13850, 60000, 0, 500, 0⟩ = 500 := by decide

end TaxCode.Forms.Reported.Pub525

#print axioms TaxCode.Forms.Reported.Pub525.worksheet_eq_statute
#print axioms TaxCode.Forms.Reported.Pub525.poster_example
#print axioms TaxCode.Forms.Reported.Pub525.revRul_2019_11
#print axioms TaxCode.Forms.Reported.Pub525.posterRule_ge
#print axioms TaxCode.Forms.Reported.Pub525.reading2_eq_statute
#print axioms TaxCode.Forms.Reported.Pub525.reading1_excess
#print axioms TaxCode.Forms.Reported.Pub525.old_nocap_gap
#print axioms TaxCode.Forms.Reported.Pub525.old_eq_new_capped
#print axioms TaxCode.Forms.Reported.Pub525.reddit_case
#print axioms TaxCode.Forms.Reported.Pub525.property_refund_case
