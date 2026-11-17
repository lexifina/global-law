import TaxCode.Individual.Form1040

/-!
# Form 1040 (2025) lines 11a–24 and the §63(e) choice, against the assembly in `Form1040.lean`

Form text: Form 1040 (2025) page 2: 11b "Amount from line 11a (adjusted gross income)"; 12e "Standard deduction or
itemized deductions (from Schedule A)"; 13a "Qualified business income deduction from Form 8995 or Form 8995-A"; 13b
"Additional deductions from Schedule 1-A, line 38"; 14 "Add lines 12e, 13a, and 13b"; 15 "Subtract line 14 from line
11b. If zero or less, enter -0-. This is your taxable income"; 16 tax; 17 Schedule 2 line 3; 18 "Add lines 16 and
17"; 19 Schedule 8812; 20 Schedule 3 line 8; 21 "Add lines 19 and 20"; 22 "Subtract line 21 from line 18. If zero or
less, enter -0-"; 23 Schedule 2 line 21; 24 "Add lines 22 and 23. This is your total tax".

Statute: §63(a), (b), (d), (e) and §26(a), via `B.taxableIncome`, `B.deduction`, `D.applyCredits`
(`D.nonrefundable_eq_min`). The model's §199A deduction is figured on taxable income before it (§199A(e)(1)), which
Form 8995 line 11 defines as line 11b − 12e − 13b: the form's order (13a computed from 12e and 13b, then added on 14)
is the statute's.
-/

namespace TaxCode.Forms.Form1040Lines
open TaxCode.Individual

/-- Lines 14–15. -/
def l15 (l11b l12e l13a l13b : Int) : Int := max 0 (l11b - (l12e + l13a + l13b))

/-- **Line 15 is §63 taxable income for every household, AGI and election**, with 12e = the deduction taken under
§63(e), 13b = the §63(b) deductions every filer takes (Schedule 1-A), 13a = §199A on line 11b − 12e − 13b. -/
theorem l15_eq (h : Household) (agi : Int) (f : B.Facts) :
    l15 agi (B.deduction h agi f) (B.qbiDeduction h (B.taxableBeforeQbi h agi f) (B.netCapitalGain h) f)
      (B.belowTheLine h agi f) = B.taxableIncome h agi f := by
  unfold l15 B.taxableIncome B.taxableBeforeQbi B.nonItemizerCharity; simp only; omega

/-- Lines 18–22: with the nonrefundable credits used as §26(a) allows (`D.nonrefundable_eq_min`: the lesser of the
tax and the credits), line 22's floor never binds and line 22 = line 18 − line 21, as `Form1040.lean` computes it. -/
theorem l22_eq (tax : Int) (c : D.CreditInputs) (ht : 0 ≤ tax) :
    max 0 (tax - (D.applyCredits tax c).1) = tax - (D.applyCredits tax c).1 := by
  have := D.nonrefundable_eq_min tax c
  have h0 : 0 ≤ D.pos c.foreignTax + D.pos c.cdcc + D.pos c.educationNonref + D.pos c.saver + D.pos c.ctc := by
    unfold D.pos; omega
  unfold D.pos at *; omega

/-- **§63(e)**: for a fixed rest of the return, taxable income is smallest when line 12e is the larger of the two
deductions (`B.deduction` with no election) — the form's default ("Itemize if larger") minimises line 15; electing the
smaller one (allowed by §63(e), and sometimes cheaper because of the AMT) never lowers line 15. -/
theorem default_minimises_l15 (agi std itm q b : Int) :
    l15 agi (max std itm) q b ≤ l15 agi std q b ∧ l15 agi (max std itm) q b ≤ l15 agi itm q b := by
  unfold l15; omega

end TaxCode.Forms.Form1040Lines

#print axioms TaxCode.Forms.Form1040Lines.l15_eq
#print axioms TaxCode.Forms.Form1040Lines.l22_eq
