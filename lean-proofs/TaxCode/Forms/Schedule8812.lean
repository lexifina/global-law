import TaxCode.Individual.D.ChildTaxCredit

/-!
# Schedule 8812 (Form 1040), tax year 2025, line by line, against §24

Form text: Schedule 8812 (Form 1040) 2025 ("Created 7/30/25", irs.gov/pub/irs-prior/f1040s8--2025.pdf) and the 2025
Instructions for Schedule 8812 (dated Jan 23, 2026: Credit Limit Worksheets A and B, Earned Income Worksheet), with the
Credit Limit Worksheets of Form 8839 (2025 instructions, line 17), Form 8396 and Form 5695 (2025), which tell the filer
sent there by Credit Limit Worksheet B to use "line 14 of Credit Limit Worksheet B instead of ... line 19".

Statute: 26 U.S.C. §24 (OLRC release point 119-138), via `TaxCode.Individual.D.ChildTaxCredit` (amounts for 2025:
$2,200, $500, $1,700, $2,500, 15%, $400,000/$200,000), §26(a) for the aggregate limit, §24(k)(2)(B)(ii) for Puerto Rico.

Every `l…` definition below is one line of the form or worksheet, from its text. Rounding: line 20 and Credit Limit
Worksheet B line 5 ("Multiply ... by 15% (0.15)") are rounded to the nearest dollar (the forms' whole-dollar rule),
as `D.pctRound` does; the statute model uses the same rounding, so the comparison is exact.

Domain (stated on each theorem): counts `kids`, `others` ≥ 0; tax (Form 1040 line 18) ≥ 0; credits ≥ 0.
-/

namespace TaxCode.Forms.Schedule8812
open TaxCode.Individual TaxCode.Individual.D

/-- What the filer brings to Schedule 8812. -/
structure Inputs where
  filing : Filing
  agi : Int                 -- Form 1040 line 11a
  prExcluded : Int := 0     -- line 2a: Puerto Rico income excluded (§933)
  f2555l43 : Int := 0       -- Form 2555 line 43: housing exclusion + foreign earned income exclusion (§911(a))
  f2555l44 : Int := 0       -- Form 2555 line 44: deductions allocable to the excluded income (§911(d)(6))
  f2555l50 : Int := 0       -- Form 2555 line 50: housing deduction (§911(c)(4))
  f4563 : Int := 0          -- line 2c: Form 4563 line 15 (§931, American Samoa)
  kids : Int                -- line 4: qualifying children under 17 with the required SSN
  others : Int              -- line 6: other dependents
  tax : Int                 -- Form 1040 line 18
  earlier : Int := 0        -- credits Credit Limit Worksheet A line 2 lists (Sch. 3 lines 1, 2, 3, 4, 5b, 6d, 6f,
                            --   6l, 6m), before their own limits
  later : Int := 0          -- credits Credit Limit Worksheet B names (Forms 8396, 8839, 5695 Part I, 8859), before
                            --   their own limits
  earned : Int              -- line 18a (Earned Income Worksheet line 7 / chart; includes nontaxable combat pay)
  ssWithheld : Int := 0     -- line 21 (W-2 boxes 4 and 6)
  ssOther : Int := 0        -- line 22 (Sch. 1 line 15; Sch. 2 lines 5, 6, 13)
  eic : Int := 0            -- Form 1040 line 27a
  excessSS : Int := 0       -- Schedule 3 line 11 (excess social security withheld, §6413(c))
  files2555 : Bool := false
  prResident : Bool := false
  deriving Repr

/-! ## The form, line by line -/

section Form
variable (i : Inputs)

/-- Line 1: "Enter the amount from line 11a of your Form 1040". -/
def l1 : Int := i.agi
/-- Line 2b: "Enter the amounts from lines 45 and 50 of your Form 2555"; line 45 is "Subtract line 44 from line 43". -/
def l2b : Int := (i.f2555l43 - i.f2555l44) + i.f2555l50
/-- Line 2d: "Add lines 2a through 2c". -/
def l2d : Int := i.prExcluded + l2b i + i.f4563
/-- Line 3: "Add lines 1 and 2d". -/
def l3 : Int := l1 i + l2d i
/-- Line 5: "Multiply line 4 by $2,200". -/
def l5 : Int := i.kids * 2200
/-- Line 7: "Multiply line 6 by $500". -/
def l7 : Int := i.others * 500
/-- Line 8: "Add lines 5 and 7". -/
def l8 : Int := l5 i + l7 i
/-- Line 9: "Married filing jointly—$400,000; All other filing statuses—$200,000". -/
def l9 : Int := if i.filing = .mfj then 400000 else 200000
/-- Line 10: "Subtract line 9 from line 3. If zero or less, enter -0-. If more than zero and not a multiple of $1,000,
enter the next multiple of $1,000." -/
def l10 : Int := let d := l3 i - l9 i; if d ≤ 0 then 0 else (d + 999) / 1000 * 1000
/-- Line 11: "Multiply line 10 by 5% (0.05)". -/
def l11 : Int := l10 i * 5 / 100
/-- Line 12: "Is the amount on line 8 more than the amount on line 11? No. Stop here ... Yes. Subtract line 11 from
line 8." ("Stop here" leaves every later line at zero.) -/
def l12 : Int := if l8 i > l11 i then l8 i - l11 i else 0

/-- Credit Limit Worksheet A line 2: the Schedule 3 credits listed there. Each is limited by its own form's credit
limit worksheet, chained in Schedule 3 order, so together they use `min (tax, their sum)`
(`D.useAll_eq` proves the chaining identity). -/
def a2 : Int := min (pos i.tax) (pos i.earlier)
/-- CLW A line 3: "Subtract line 2 from line 1" (line 1 = Form 1040 line 18). -/
def a3 : Int := i.tax - a2 i

/-- When Credit Limit Worksheet B is completed: "1. You are claiming one or more of the following credits [8396,
8839, 5695 Part I, 8859]. 2. You are not filing Form 2555. 3. Line 4 of Schedule 8812 is more than zero." -/
def useB : Bool := decide (0 < i.later) && !i.files2555 && decide (0 < i.kids)

/-- CLW B line 1: "Enter the amount from Schedule 8812, line 12". -/
def b1 : Int := l12 i
/-- CLW B line 2: "Number of qualifying children ... × $1,700". -/
def b2 : Int := i.kids * 1700
/-- CLW B lines 3–4: earned income; "Is the amount on line 3 more than $2,500? No. Leave line 4 blank, enter -0- on
line 5 ... Yes. Subtract $2,500". -/
def b4 : Int := if i.earned > 2500 then i.earned - 2500 else 0
/-- CLW B line 5: "Multiply the amount on line 4 by 15% (0.15)". -/
def b5 : Int := pctRound (b4 i) 1500
/-- CLW B line 6, the gate to lines 7–11: "No [line 2 < $5,100]. If you are a bona fide resident of Puerto Rico and
line 5 above is less than line 1 above, go to line 7. Otherwise ... enter -0- on line 11. Yes. If line 5 above is
equal to or more than line 1 above ... enter -0- on line 11. Otherwise, go to line 7." -/
def bGate : Bool := if b2 i ≥ 5100 then decide (b5 i < b1 i) else (i.prResident && decide (b5 i < b1 i))
/-- CLW B lines 7–11: "Add lines 7 and 8" (withheld social security and Medicare taxes; Sch. 1 line 15, Sch. 2 lines
5, 6, 13), less line 10 ("Form 1040 line 27a, and Schedule 3, line 11"); "If the result is zero or less, enter -0-". -/
def b11 : Int := if bGate i then pos ((i.ssWithheld + i.ssOther) - (i.eic + i.excessSS)) else 0
/-- CLW B line 12: "Enter the larger of line 5 or line 11". -/
def b12 : Int := max (b5 i) (b11 i)
/-- CLW B line 13: "Enter the smaller of line 2 or line 12". -/
def b13 : Int := min (b2 i) (b12 i)
/-- CLW B line 14: "Is the amount on line 13 ... more than the amount on line 1? No. Subtract line 13 from line 1.
Yes. Enter -0-." -/
def b14 : Int := if b13 i > b1 i then 0 else b1 i - b13 i
/-- CLW B line 15: the later credits as their own worksheets allow them. Form 8839 Credit Limit Worksheet line 3
(and Forms 8396, 5695): "include the amount from line 14 of Credit Limit Worksheet B instead of ... line 19", plus the
Schedule 3 credits before them; each is the smaller of the credit and the tax left. -/
def b15 : Int := min (pos i.later) (pos (i.tax - a2 i - b14 i))

/-- CLW A line 4: "If you are not completing Credit Limit Worksheet B, enter -0-; otherwise ... line 15". -/
def a4 : Int := if useB i then b15 i else 0
/-- CLW A line 5 = Schedule 8812 line 13: "Subtract line 4 from line 3". -/
def l13 : Int := a3 i - a4 i
/-- Line 14: "Enter the smaller of line 12 or line 13. This is your child tax credit and credit for other
dependents." -/
def l14 : Int := min (l12 i) (l13 i)

/-- Line 16a: "Subtract line 14 from line 12. If zero, stop here". -/
def l16a : Int := l12 i - l14 i
/-- Line 16b: "Number of qualifying children ... × $1,700". -/
def l16b : Int := i.kids * 1700
/-- Line 17: "Enter the smaller of line 16a or line 16b". -/
def l17 : Int := min (l16a i) (l16b i)
/-- Line 19: "Is the amount on line 18a more than $2,500? No. Leave line 19 blank and enter -0- on line 20. Yes.
Subtract $2,500". -/
def l19 : Int := if i.earned > 2500 then i.earned - 2500 else 0
/-- Line 20: "Multiply the amount on line 19 by 15% (0.15)". -/
def l20 : Int := pctRound (l19 i) 1500
/-- Lines 21–25: "Add lines 21 and 22", less line 24 ("Form 1040 line 27a, and Schedule 3, line 11"); "If zero or
less, enter -0-". -/
def l25 : Int := pos ((i.ssWithheld + i.ssOther) - (i.eic + i.excessSS))
/-- Line 26: "Enter the larger of line 20 or line 25". -/
def l26 : Int := max (l20 i) (l25 i)
/-- Line 27 with the routing after line 20: "On line 16b, is the amount $5,100 or more? No. If you are a bona fide
resident of Puerto Rico, go to line 21. Otherwise ... enter the smaller of line 17 or line 20 on line 27. Yes. If
line 20 is equal to or more than line 17 ... enter the amount from line 17 on line 27. Otherwise, go to line 21."
After line 26: "enter the smaller of line 17 or line 26 on line 27". Part II-A caution: "If you file Form 2555, you
cannot claim the additional child tax credit." -/
def l27 : Int :=
  if i.files2555 then 0 else
  if l16b i ≥ 5100 then (if l20 i ≥ l17 i then l17 i else min (l17 i) (l26 i))
  else if i.prResident then min (l17 i) (l26 i) else min (l17 i) (l20 i)

/-- The later credits finally allowed (when CLW B is not used they are figured after the CTC, against "line 19"). -/
def laterAllowed : Int := if useB i then b15 i else min (pos i.later) (pos (i.tax - a2 i - l14 i))

/-- All nonrefundable credits used (Form 1040 line 21 restricted to these credits). -/
def nonrefTotal : Int := a2 i + l14 i + laterAllowed i

end Form

/-! ## The statute -/

section Statute
variable (i : Inputs)

/-- §24(b)(1): "adjusted gross income increased by any amount excluded from gross income under section 911, 931, or
933". The §911 amount excluded is Form 2555 line 43 (the two exclusions of §911(a)). -/
def magi : Int := i.agi + i.prExcluded + i.f2555l43 + i.f4563

def counts : CtcCounts := ⟨i.kids, i.others⟩

/-- §24(a), (b)(1), (h)(2)–(4): the credit after the phase-out. -/
def credit : Int := ctcAfterPhaseout i.filing (magi i) (counts i)

/-- §24(d)(1)(B)(i)–(ii) with §24(h)(6) and §24(k)(2)(B)(ii) (Puerto Rico: (ii) "without regard to the phrase 'in the
case of a taxpayer with 3 or more qualifying children'"). Social security taxes per §24(d)(2): withheld employee
taxes and half the SE tax, less what is refundable under §6413(c) (`excessSS`). -/
def zStat : Int :=
  max (pctRound (pos (i.earned - actcEarnedFloor)) actcRateBp)
    (if 3 ≤ i.kids ∨ i.prResident = true then pos ((i.ssWithheld + i.ssOther - i.excessSS) - i.eic) else 0)

/-- §26(a): the aggregate subpart A credits allowed against a limitation `lim`, out of credits totalling `s`. -/
def aggAllowed (lim s : Int) : Int := min (pos lim) s

/-- All subpart A credits before the §26(a) limit: the earlier ones, the §24 credit, the later ones. -/
def subpartA : Int := pos i.earlier + credit i + pos i.later

/-- §24(d)(1)(B): "the amount by which the aggregate amount of credits allowed by this subpart ... would increase if
the limitation imposed by section 26(a) were increased by" `zStat`. -/
def incr : Int := aggAllowed (i.tax + zStat i) (subpartA i) - aggAllowed i.tax (subpartA i)

/-- §24(d)(1): the lesser of (A) [as limited by §24(h)(5): $1,700 per child, "without regard to paragraph (4)"] and
(B); §24(d)(3): none for a taxpayer who elects §911 (modelled as filing Form 2555, the form's own test). -/
def actc : Int := if i.files2555 then 0 else min (actcCapA i.filing (magi i) (counts i)) (incr i)

/-- §24(d)(1) last sentence: the refundable credit "shall reduce the amount of credit otherwise allowable under
subsection (a)"; §26(a) then limits all subpart A credits together. -/
def nonrefStat : Int := aggAllowed i.tax (pos i.earlier + (credit i - actc i) + pos i.later)

end Statute

/-! ## Part I: the credit -/

/-- Line 10–11 is the §24(b)(1) reduction: "$50 for each $1,000 (or fraction thereof)". -/
theorem l11_eq (i : Inputs) : l11 i = ctcReduction i.filing (l3 i) := by
  unfold l11 l10 ctcReduction ceilDiv pos ctcThreshold l9
  cases i.filing <;> simp <;> split <;> omega

/-- Line 3 is the statute's MAGI plus (Form 2555 line 50 − line 44): the form adds back the housing DEDUCTION, which
§24(b)(1) does not ("amount excluded"), and adds back the exclusion NET of allocable deductions (line 45), while the
statute adds the whole amount excluded. -/
theorem l3_eq (i : Inputs) : l3 i = magi i + (i.f2555l50 - i.f2555l44) := by
  unfold l3 l1 l2d l2b magi; omega

/-- **Line 12 = §24(a)–(b) for all inputs** in which Form 2555 lines 44 and 50 are equal (e.g. no Form 2555). -/
theorem l12_eq_statute (i : Inputs) (h : i.f2555l50 = i.f2555l44) : l12 i = credit i := by
  have h3 := l3_eq i
  have h11 := l11_eq i
  unfold l12 credit ctcAfterPhaseout ctcTentative counts l8 l5 l7 ctcPerChild odcPerDependent at *
  rw [h11, h3, h]; unfold pos; simp only [Int.add_zero, Int.sub_self]; split <;> omega

theorem ctcReduction_le (f : Filing) (m d : Int) :
    ctcReduction f (m + d) - ctcReduction f m ≤ 50 * ceilDiv (pos d) 1000 ∧
    ctcReduction f m - ctcReduction f (m + d) ≤ 50 * ceilDiv (pos (-d)) 1000 := by
  unfold ctcReduction ceilDiv pos; omega

/-- **Form 2555 filers: the credit (line 12) differs from §24(b)(1) by at most $50 per $1,000 (or fraction) of
|line 50 − line 44|**: lower on the form when the housing deduction exceeds the allocable deductions, higher when the
allocable deductions are larger. -/
theorem l12_diff_2555 (i : Inputs) :
    credit i - l12 i ≤ 50 * ceilDiv (pos (i.f2555l50 - i.f2555l44)) 1000 ∧
    l12 i - credit i ≤ 50 * ceilDiv (pos (i.f2555l44 - i.f2555l50)) 1000 := by
  have h3 := l3_eq i
  have h11 := l11_eq i
  have hr := ctcReduction_le i.filing (magi i) (i.f2555l50 - i.f2555l44)
  have e : -(i.f2555l50 - i.f2555l44) = i.f2555l44 - i.f2555l50 := by omega
  rw [e] at hr
  unfold l12 credit ctcAfterPhaseout ctcTentative counts l8 l5 l7 ctcPerChild odcPerDependent at *
  rw [h11, h3]; dsimp only at *; unfold ceilDiv at *
  generalize ctcReduction i.filing (magi i + (i.f2555l50 - i.f2555l44)) = R1 at *
  generalize ctcReduction i.filing (magi i) = R0 at *
  unfold pos at *; split <;> omega

/-- Single, one child, AGI $199,000, a $20,000 housing deduction, no exclusion: the form adds the deduction back. -/
def ex2555a : Inputs :=
  { filing := .single, agi := 199000, f2555l50 := 20000, kids := 1, others := 0, tax := 0, earned := 0 }
/-- Single, two children, AGI $210,000, $50,000 excluded with $30,000 of allocable deductions: the form adds back only
the net $20,000. -/
def ex2555b : Inputs :=
  { filing := .single, agi := 210000, f2555l43 := 50000, f2555l44 := 30000, kids := 2, others := 0, tax := 0,
    earned := 0 }

/-- The 2555 difference is real in both directions. -/
theorem l12_2555_examples :
    l12 ex2555a = 1250 ∧ credit ex2555a = 2200 ∧ l12 ex2555b = 2900 ∧ credit ex2555b = 1400 := by decide

/-! ## Part II: the refundable credit -/

/-- Line 26 routing: line 27 is `min (line 17, Z)` where Z is the larger of line 20 and (3+ children or Puerto Rico)
line 25; the "skip Part II-B if line 20 ≥ line 17" shortcut changes nothing. -/
theorem l27_eq (i : Inputs) (hk : 0 ≤ i.kids) :
    l27 i = if i.files2555 then 0 else min (l17 i) (zStat i) := by
  unfold l27 zStat l26 l25 l20 l19 l16b actcEarnedFloor actcRateBp
  cases i.files2555 <;> cases i.prResident <;> simp only [Bool.false_eq_true, ↓reduceIte, or_true, or_false] <;>
    unfold pos pctRound roundDollar <;> split <;> (try split) <;> (try split) <;> omega

/-- Credit Limit Worksheet B lines 12–14: the gate at line 6 changes nothing either; line 14 is the credit left after
carving out `min (line 2, Z)`. -/
theorem b14_eq (i : Inputs) (hk : 0 ≤ i.kids) : b14 i = pos (b1 i - min (b2 i) (zStat i)) := by
  unfold b14 b13 b12 b11 bGate b5 b4 b2 zStat actcEarnedFloor actcRateBp
  cases i.prResident <;> simp only [Bool.false_eq_true, ↓reduceIte, or_true, or_false, Bool.true_and,
    Bool.false_and] <;> unfold pos pctRound roundDollar <;> (repeat' split) <;> simp_all <;> omega

theorem l12_nonneg (i : Inputs) : 0 ≤ l12 i := by unfold l12; split <;> omega

theorem b14_nonneg (i : Inputs) : 0 ≤ b14 i := by unfold b14; split <;> omega

/-- Line 13 (CLW A line 5) is never negative when the tax is not. -/
theorem l13_nonneg (i : Inputs) (ht : 0 ≤ i.tax) : 0 ≤ l13 i := by
  have := b14_nonneg i
  unfold l13 a4 b15 a3 a2 pos; split <;> omega

theorem l16a_bounds (i : Inputs) (ht : 0 ≤ i.tax) : 0 ≤ l16a i ∧ l16a i ≤ l12 i := by
  have := l13_nonneg i ht; have := l12_nonneg i; unfold l16a l14; omega

/-- **The unused-credit identity.** Whether or not Credit Limit Worksheet B is used, line 16a (the credit left unused)
caps the refundable credit exactly as the statute's aggregate increase does: for any cap `A` with `0 ≤ A ≤ line 12`,
`min A (min Z line16a) = min A (statute's (d)(1)(B))`. -/
theorem unused_identity (i : Inputs) (hk : 0 ≤ i.kids) (ht : 0 ≤ i.tax) (A : Int) (hA0 : 0 ≤ A) (hA : A ≤ l12 i)
    (hA2 : A ≤ 1700 * i.kids) (h12 : l12 i = credit i) (hn : i.files2555 = false) :
    min A (min (zStat i) (l16a i)) = min A (incr i) := by
  have hb14 := b14_eq i hk
  have hz : 0 ≤ zStat i := by unfold zStat pctRound roundDollar pos; omega
  have hc := l12_nonneg i
  have hBc : useB i = false → (i.later ≤ 0 ∨ i.kids ≤ 0) := by
    intro h; unfold useB at h; rw [hn] at h; simp at h; omega
  unfold incr aggAllowed subpartA l16a l14 l13 a4 b15 a3 a2 at *
  rw [← h12]; rw [hb14]
  unfold b1 b2 at *
  have hE := pos_nonneg i.earlier; have hL := pos_nonneg i.later
  generalize zStat i = Z at *
  generalize l12 i = C at *
  cases hB : useB i
  · have h' := hBc hB; simp only [Bool.false_eq_true, ↓reduceIte]; unfold pos at *; omega
  · simp only [↓reduceIte]; unfold pos at *; omega

/-- §24(h)(5) cap as the form writes it versus the statute: the statute's (A) is `min (child credit after the
phase-out, $1,700 × kids)`; the form's line 16b is `$1,700 × kids` alone. -/
def childPart (i : Inputs) : Int := pos (ctcPerChild * i.kids - ctcReduction i.filing (magi i))

/-- **The exact difference (the known "$200 vs $700" excess, for all inputs).** With no Form 2555, the form's
refundable credit exceeds the statute's by exactly `pos (line 27 − child credit after the phase-out)`, and never
falls below it. -/
theorem actc_difference_exact (i : Inputs) (hk : 0 ≤ i.kids) (ho : 0 ≤ i.others) (ht : 0 ≤ i.tax)
    (hn : i.files2555 = false) (h2555 : i.f2555l50 = i.f2555l44) :
    l27 i - actc i = pos (l27 i - childPart i) := by
  have h12 := l12_eq_statute i h2555
  have h27 := l27_eq i hk
  have hc := l12_nonneg i
  have hcp : 0 ≤ childPart i := pos_nonneg _
  have hcpC : childPart i ≤ l12 i := by
    rw [h12]; unfold childPart credit ctcAfterPhaseout ctcTentative counts odcPerDependent pos; dsimp only; omega
  have hcap : 0 ≤ min (childPart i) (actcPerChildCap * i.kids) := by unfold actcPerChildCap; omega
  have hU := unused_identity i hk ht (min (childPart i) (actcPerChildCap * i.kids)) hcap (by omega)
    (by unfold actcPerChildCap; omega) h12 hn
  have h16 := (l16a_bounds i ht).2
  have h16' := (l16a_bounds i ht).1
  unfold actc actcCapA counts at *
  rw [hn] at h27 ⊢; simp only [Bool.false_eq_true, ↓reduceIte] at h27 ⊢
  rw [h27]; unfold childPart at *
  rw [← hU]; unfold l17 l16b actcPerChildCap at *
  generalize zStat i = Z at *; generalize l16a i = U at *
  unfold pos at *; omega

/-- **Equal for all inputs with no other dependent** (line 6 = 0) and no Form 2555: line 27 = §24(d) ACTC. -/
theorem actc_eq_no_others (i : Inputs) (hk : 0 ≤ i.kids) (ht : 0 ≤ i.tax) (h0 : i.others = 0)
    (hn : i.files2555 = false) (h2555 : i.f2555l50 = i.f2555l44) : l27 i = actc i := by
  have hd := actc_difference_exact i hk (by omega) ht hn h2555
  have h12 := l12_eq_statute i h2555
  have h27 := l27_eq i hk
  have hcp : childPart i = l12 i := by
    rw [h12]; unfold childPart credit ctcAfterPhaseout ctcTentative counts odcPerDependent; rw [h0]; simp
  have h16 := (l16a_bounds i ht).2
  rw [hn] at h27; simp only [Bool.false_eq_true, ↓reduceIte] at h27
  have : l27 i ≤ l12 i := by rw [h27]; unfold l17; omega
  unfold pos at hd; omega

/-- **The maximum excess is `min ($500 × other dependents, $1,700 × children)`** — the form never exceeds the statute
by more ... -/
theorem actc_excess_le (i : Inputs) (hk : 0 ≤ i.kids) (ho : 0 ≤ i.others) (ht : 0 ≤ i.tax)
    (hn : i.files2555 = false) (h2555 : i.f2555l50 = i.f2555l44) :
    0 ≤ l27 i - actc i ∧ l27 i - actc i ≤ min (500 * i.others) (1700 * i.kids) := by
  have hd := actc_difference_exact i hk ho ht hn h2555
  have h12 := l12_eq_statute i h2555
  have h27 := l27_eq i hk
  have h16 := (l16a_bounds i ht).2
  rw [hn] at h27; simp only [Bool.false_eq_true, ↓reduceIte] at h27
  rw [h12] at h16
  have hb : l27 i ≤ l16a i ∧ l27 i ≤ 1700 * i.kids := by rw [h27]; unfold l17 l16b; omega
  unfold childPart credit ctcAfterPhaseout ctcTentative counts ctcPerChild odcPerDependent at *
  dsimp only at *
  generalize ctcReduction i.filing (magi i) = R at *
  unfold pos at *; omega

/-- ... and the maximum is attained for every number of children `n` and other dependents `k`: single, MAGI
$200,000 + $44,000·n (the child credit exactly phased out), no tax, earned income $2,500 + $12,000·n. -/
def worst (n k : Int) : Inputs :=
  { filing := .single, agi := 200000 + 44000 * n, kids := n, others := k, tax := 0, earned := 2500 + 12000 * n }

theorem actc_excess_attained (n k : Int) (hn : 0 ≤ n) (hk : 0 ≤ k) :
    l27 (worst n k) - actc (worst n k) = min (500 * k) (1700 * n) ∧ actc (worst n k) = 0 := by
  have hd := actc_difference_exact (worst n k) hn hk (by simp [worst]) rfl rfl
  have hcp : childPart (worst n k) = 0 := by
    unfold childPart ctcReduction magi ctcThreshold ceilDiv ctcPerChild pos worst; simp; omega
  have h27 := l27_eq (worst n k) hn
  rw [show (worst n k).files2555 = false from rfl] at h27
  simp only [Bool.false_eq_true, ↓reduceIte] at h27
  have hl : l27 (worst n k) = min (500 * k) (1700 * n) := by
    rw [h27]
    simp only [worst, l17, l16a, l16b, l14, l13, l12, l11, l10, l9, l8, l7, l5, l3, l2d, l2b, l1, a4, a3, a2, useB,
      zStat, actcEarnedFloor, actcRateBp, pctRound, roundDollar, pos, Bool.not_false,
      Bool.and_true, Int.lt_irrefl, decide_false, Bool.false_and, Bool.false_eq_true, ↓reduceIte,
      reduceCtorEq]
    (repeat' split) <;> omega
  rw [hcp] at hd; unfold pos at hd
  constructor <;> omega

/-- The published example: one child, one other dependent, single, MAGI $240,000, no tax: form $700, statute $200. -/
theorem published_example :
    l27 { filing := .single, agi := 240000, kids := 1, others := 1, tax := 0, earned := 240000 } = 700 ∧
    actc { filing := .single, agi := 240000, kids := 1, others := 1, tax := 0, earned := 240000 } = 200 := by
  decide

/-- **The nonrefundable side agrees too.** With no other dependent and no Form 2555, the credits used against tax
(Credit Limit Worksheet A line 2 + line 14 + the later credits through Credit Limit Worksheet B) equal the §26(a)
aggregate after the §24(d)(1) reduction: Credit Limit Worksheet B implements the statute's order-free rule. -/
theorem nonref_eq (i : Inputs) (hk : 0 ≤ i.kids) (ht : 0 ≤ i.tax) (h0 : i.others = 0)
    (hn : i.files2555 = false) (h2555 : i.f2555l50 = i.f2555l44) : nonrefTotal i = nonrefStat i := by
  have hA := actc_eq_no_others i hk ht h0 hn h2555
  have h12 := l12_eq_statute i h2555
  have h27 := l27_eq i hk
  have hb14 := b14_eq i hk
  have hc := l12_nonneg i
  have hz : 0 ≤ zStat i := by unfold zStat pctRound roundDollar pos actcRateBp; omega
  have hBc : useB i = false → (i.later ≤ 0 ∨ i.kids ≤ 0) := by
    intro h; unfold useB at h; rw [hn] at h; simp at h; omega
  rw [hn] at h27; simp only [Bool.false_eq_true, ↓reduceIte] at h27
  unfold nonrefStat aggAllowed
  rw [← hA, h27, ← h12]
  unfold nonrefTotal laterAllowed l17 l16a l16b l14 l13 a4 b15 a3 a2 at *
  rw [hb14]; unfold b1 b2
  clear hA h27 hb14 h12
  generalize zStat i = Z at *
  generalize l12 i = C at *
  have hE := pos_nonneg i.earlier; have hM := pos_nonneg i.later
  cases hB : useB i
  · have h' := hBc hB
    have hM0 : i.later ≤ 0 → pos i.later = 0 := fun h => by unfold pos; omega
    simp only [Bool.false_eq_true, ↓reduceIte]
    generalize pos i.earlier = E at *
    rcases h' with h' | h'
    · rw [hM0 h']; unfold pos; omega
    · generalize pos i.later = M at *; unfold pos; omega
  · simp only [↓reduceIte]
    generalize pos i.earlier = E at *
    generalize pos i.later = M at *
    unfold pos; omega

/-! ## Spot checks against the instructions' own numbers -/

-- Credit Limit Worksheet B line 6 and Schedule 8812 line 16b: "$5,100 or more" is three children.
#guard l16b { filing := .single, agi := 0, kids := 3, others := 0, tax := 0, earned := 0 } = 5100
-- Line 10 example in the form text: "if the result is $425, enter $1,000; if the result is $1,025, enter $2,000".
#guard l10 { filing := .single, agi := 200425, kids := 0, others := 0, tax := 0, earned := 0 } = 1000
#guard l10 { filing := .single, agi := 201025, kids := 0, others := 0, tax := 0, earned := 0 } = 2000

/-! ## Agreement with the existing statute model -/

/-- The `actc` here (aggregate §26(a) reading) agrees with `D.actcStatute` when there are no other subpart A
credits, outside Puerto Rico. -/
theorem actc_eq_model (i : Inputs) (hk : 0 ≤ i.kids) (ho : 0 ≤ i.others) (ht : 0 ≤ i.tax) (he : i.earlier = 0)
    (hl : i.later = 0) (hp : i.prResident = false) :
    actc i = actcStatute i.filing (magi i) (counts i) i.tax i.earned (i.ssWithheld + i.ssOther - i.excessSS) i.eic
      i.files2555 := by
  have hA : 0 ≤ actcCapA i.filing (magi i) (counts i) ∧
      actcCapA i.filing (magi i) (counts i) ≤ ctcAfterPhaseout i.filing (magi i) (counts i) := by
    unfold actcCapA ctcAfterPhaseout ctcTentative counts actcPerChildCap ctcPerChild odcPerDependent pos
    dsimp only; omega
  have hz : 0 ≤ pctRound (pos (i.earned - actcEarnedFloor)) actcRateBp := by
    unfold pctRound roundDollar pos actcRateBp; omega
  unfold actc actcStatute incr aggAllowed subpartA actcEarnedAmount ctcNonrefundable zStat at *
  rw [he, hl, hp]; unfold credit
  have hcount : (counts i).children = i.kids := rfl
  rw [hcount]
  cases i.files2555 <;> simp only [Bool.false_eq_true, ↓reduceIte, or_false]
  generalize ctcAfterPhaseout i.filing (magi i) (counts i) = C at *
  generalize actcCapA i.filing (magi i) (counts i) = A at *
  generalize pctRound (pos (i.earned - actcEarnedFloor)) actcRateBp = P at *
  unfold pos; (repeat' split) <;> omega

end TaxCode.Forms.Schedule8812

/-! Axioms -/
#print axioms TaxCode.Forms.Schedule8812.l12_eq_statute
#print axioms TaxCode.Forms.Schedule8812.l12_diff_2555
#print axioms TaxCode.Forms.Schedule8812.actc_difference_exact
#print axioms TaxCode.Forms.Schedule8812.actc_eq_no_others
#print axioms TaxCode.Forms.Schedule8812.actc_excess_le
#print axioms TaxCode.Forms.Schedule8812.actc_excess_attained
#print axioms TaxCode.Forms.Schedule8812.nonref_eq
#print axioms TaxCode.Forms.Schedule8812.actc_eq_model
