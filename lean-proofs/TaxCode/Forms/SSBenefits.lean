import TaxCode.Individual.A.SocialSecurity

/-!
# Social Security Benefits Worksheet—Lines 6a and 6b (2025 Form 1040 instructions) against §86

Form text: 2025 Instructions for Form 1040, "Social Security Benefits Worksheet—Lines 6a and 6b" (lines 1–18) and the
"Exception" under Lines 6a and 6b (use Pub. 590-A if an IRA contribution with plan coverage; repayments over
benefits). Publication 915 (2025), "How To Report Your Benefits" item 2 and Worksheet 1 line 5.

Statute: §86 (OLRC 119-138) via `TaxCode.Individual.A.SocialSecurity` (`taxableSS40`, in fortieths of a dollar).
§86(b)(2): "adjusted gross income (A) determined without regard to this section and sections 85(c), 135, 137, 221,
911, 931, and 933, and (B) increased by" tax-exempt interest.

The worksheet's lines 3–7 build modified AGI from Form 1040 lines 1z, 2b, 3b, 4b, 5b, 7a, 8 and 2a, less Schedule 1
lines 11–20, 23 and 25 (so the §221 deduction, line 21, is not subtracted — the "without regard to section 221").
Nothing on the worksheet adds back the §135 savings-bond exclusion (Form 8815), the §137 adoption-benefit exclusion
(Form 8839), the §911 exclusions and housing deduction (Form 2555 lines 45 and 50) or the §931/§933 exclusions — but
the Exception under Lines 6a and 6b (its last bullet, printed at the top of page 32) sends exactly those filers away:
"You file Form 2555, 4563, or 8815, or you exclude employer-provided adoption benefits or income from sources within
Puerto Rico. Instead, use the worksheet in Pub. 915", whose Worksheet 1 adds them back (line 5 and the Form 8815
note). So within its stated domain (`excluded = 0`) the worksheet is the statute exactly; `worksheet_le_statute` only
measures what a filer who used it outside that domain would get wrong. No finding.
-/

namespace TaxCode.Forms.SSBenefits
open TaxCode.Individual TaxCode.Individual.A

structure Inputs where
  filing : Filing
  livedApart : Bool := false   -- married filing separately and lived apart all year
  benefits : Int               -- line 1 (box 5)
  line3 : Int                  -- Form 1040 lines 1z, 2b, 3b, 4b, 5b, 7a, 8 combined
  taxExempt : Int := 0         -- line 4 (Form 1040 line 2a)
  adjustments : Int := 0       -- line 6 (Schedule 1 lines 11–20, 23, 25)
  excluded : Int := 0          -- §§135, 137, 911, 931, 933 amounts the worksheet does not add back
  deriving Repr

/-- The worksheet's modified AGI before benefits: lines 3 + 4 − 6 (line 5 adds line 2, half the benefits). -/
def mFormOf (i : Inputs) : Int := i.line3 + i.taxExempt - i.adjustments
/-- §86(b)(2) modified AGI: the same, with the excluded amounts restored ("without regard to"). -/
def mStatOf (i : Inputs) : Int := mFormOf i + i.excluded

def mfsTogether (i : Inputs) : Bool := i.filing = .mfs && !i.livedApart

/-- The worksheet, lines 1–18, in fortieths of a dollar: line 2 "Multiply line 1 by 50%", line 5 "Combine lines 2,
3, and 4", line 7 "Subtract line 6 from line 5" (else none taxable), line 8 $32,000 / $25,000 (or, MFS living with
spouse: "skip lines 8 through 15; multiply line 7 by 85% (0.85) and enter the result on line 16"), line 9 "Subtract
line 8 from line 7" (else none taxable), line 10 $12,000 / $9,000, lines 11–13 ("one-half of line 12"), 14
"smaller of line 2 or line 13", 15 "Multiply line 11 by 85%", 16, 17 "Multiply line 1 by 85%", 18 "smaller of
line 16 or line 17". This is `A.worksheet1_40` with M = line 3 + line 4 − line 6. -/
def worksheet40 (i : Inputs) : Int :=
  if mfsTogether i then worksheet1_40 0 0 i.benefits (mFormOf i) true
  else worksheet1_40 (baseAmount i.filing i.livedApart) (adjustedBaseAmount i.filing i.livedApart) i.benefits
    (mFormOf i) false

/-- §86 on the statute's modified AGI. -/
def statute40 (i : Inputs) : Int :=
  taxableSS40 (baseAmount i.filing i.livedApart) (adjustedBaseAmount i.filing i.livedApart) i.benefits (mStatOf i)

theorem base_zero_of_together (i : Inputs) (h : mfsTogether i = true) :
    baseAmount i.filing i.livedApart = 0 ∧ adjustedBaseAmount i.filing i.livedApart = 0 := by
  unfold mfsTogether at h
  cases hf : i.filing <;> cases hl : i.livedApart <;> simp_all [baseAmount, adjustedBaseAmount]

/-- The worksheet is §86 applied to the worksheet's own modified AGI. -/
theorem worksheet_eq_core (i : Inputs) (hB : 0 ≤ i.benefits) :
    worksheet40 i = taxableSS40 (baseAmount i.filing i.livedApart) (adjustedBaseAmount i.filing i.livedApart)
      i.benefits (mFormOf i) := by
  unfold worksheet40
  have hb := base_le_adjusted i.filing i.livedApart
  cases ht : mfsTogether i
  · simp only [Bool.false_eq_true, ↓reduceIte]
    exact worksheet1_eq_statute _ _ _ _ hB hb.1 hb.2
  · simp only [↓reduceIte]
    have ⟨e1, e2⟩ := base_zero_of_together i ht
    rw [e1, e2]; exact worksheet1_mfs_together _ _ hB

/-- **Equal for all inputs with nothing excluded under §§135, 137, 911, 931, 933.** -/
theorem worksheet_eq_statute (i : Inputs) (hB : 0 ≤ i.benefits) (h0 : i.excluded = 0) :
    worksheet40 i = statute40 i := by
  rw [worksheet_eq_core i hB]; unfold statute40 mStatOf; rw [h0, Int.add_zero]

/-- §86 rises by at most 85 cents per dollar of modified AGI. -/
theorem taxableSS40_lip (b a B M D : Int) (hB : 0 ≤ B) (hba : b ≤ a) (hD : 0 ≤ D) :
    taxableSS40 b a B M ≤ taxableSS40 b a B (M + D) ∧ taxableSS40 b a B (M + D) ≤ taxableSS40 b a B M + 34 * D := by
  unfold taxableSS40
  dsimp only
  constructor <;> (repeat' split) <;> omega

/-- **With an excluded amount D ≥ 0 the worksheet never taxes more than §86, and taxes less by at most 85% of D
and at most 85% of benefits** (fortieths of a dollar: 34 per dollar). -/
theorem worksheet_le_statute (i : Inputs) (hB : 0 ≤ i.benefits) (hD : 0 ≤ i.excluded) :
    worksheet40 i ≤ statute40 i ∧ statute40 i - worksheet40 i ≤ 34 * i.excluded ∧
      statute40 i - worksheet40 i ≤ 34 * i.benefits := by
  rw [worksheet_eq_core i hB]; unfold statute40 mStatOf
  have hb := base_le_adjusted i.filing i.livedApart
  have hl := taxableSS40_lip (baseAmount i.filing i.livedApart) (adjustedBaseAmount i.filing i.livedApart)
    i.benefits (mFormOf i) i.excluded hB hb.2 hD
  have h85 := taxableSS40_le_85 (baseAmount i.filing i.livedApart) (adjustedBaseAmount i.filing i.livedApart)
    i.benefits (mFormOf i + i.excluded) hB
  have h0 := taxableSS40_nonneg (baseAmount i.filing i.livedApart) (adjustedBaseAmount i.filing i.livedApart)
    i.benefits (mFormOf i) hB
  omega

/-- Example: single, $30,000 of benefits, $30,000 of other income on the return and $20,000 excluded under §911
(foreign earned income). Worksheet: provisional income $45,000, taxable $13,850. §86: $65,000, taxable $25,500
(the 85% cap). -/
theorem example_911 :
    worksheet40 { filing := .single, benefits := 30000, line3 := 30000, excluded := 20000 } = 40 * 13850 ∧
    statute40 { filing := .single, benefits := 30000, line3 := 30000, excluded := 20000 } = 40 * 25500 := by
  decide

end TaxCode.Forms.SSBenefits

#print axioms TaxCode.Forms.SSBenefits.worksheet_eq_statute
#print axioms TaxCode.Forms.SSBenefits.worksheet_le_statute
