/-!
# 2026 Form 6251 (draft) Part I against §56(b)(1)(E): the §68 reduction stays in AMTI

Form text (2026 draft Form 6251, created 5/26/26, irs.gov/pub/irs-dft/f6251--dft.pdf, p. 1):
* line 1a "Subtract Schedule 1-A (Form 1040), line 43, from Form 1040, 1040-SR, or 1040-NR, line 14";
* line 1b "Subtract line 1a from Form 1040, 1040-SR, or 1040-NR, line 11b";
* line 2a "If filing Schedule A (Form 1040), enter the taxes from Schedule A, line 7";
* line 4 "Alternative minimum taxable income. Combine lines 1b through 3."
Form 1040 (2026 draft) line 14 = "Add lines 12e, 12f, 13a, and 13b"; line 12e = "itemized deductions (from Schedule
A)"; Schedule A (2026 draft, created 5/12/26) line 18: if line 11b minus lines 13a and 13b is more than $384,350,
"See the Itemized Deductions Worksheet" (the new §68 reduction). The draft Instructions for Form 6251 (2026), dated
Nov 6, 2026 (irs.gov/pub/irs-dft/i6251--dft.pdf, pp. 3, 9), describe lines 1a/1b, 2a and the line 3 list without any
§68 item; the text has no occurrence of "section 68".

Statute: §56(b)(1)(E) "Section 68 shall not apply." (in determining AMTI); §56(b)(1)(A)(ii) no deduction for the
§164(a)(1)-(3) taxes; §68(a) (Pub. L. 119-21): itemized deductions "reduced by 2/37 of the lesser of (1) such amount of
itemized deductions, or (2) so much of the taxable income ... (determined without regard to this section and increased
by such amount of itemized deductions) as exceeds the dollar amount at which the 37 percent rate bracket ... begins".
2026 single amounts (Rev. Proc. 2025-32 §4.01; draft instructions p. 7): 37% bracket from $640,600; AMT exemption
$90,100, reduced by 50% of AMTI over $500,000 (zero at $680,200); 26% to $244,500, then 28% less $4,890.

Model domain: no Schedule 1-A senior deduction (line 43 = 0), other below-the-line deductions `oth` (lines 12f, 13a,
13b) kept for the AMT, all other AMT adjustments lumped as `adj` (same in both). AMTI is in units of 1/74 dollar
(so 2/37 is exact); tentative minimum tax in 1/14,800 dollar.
-/

namespace TaxCode.Big.Form6251Sec68

/-- The lesser amount in §68(a): min(ID, TI-without-§68 + ID − bracket start); `agi - oth` is TI + ID. -/
def m68 (agi oth id brk : Int) : Int := min id (max 0 (agi - oth - brk))

/-- §68 reduction in 1/74 dollar: 2/37 × m = 4m/74. -/
def red74 (agi oth id brk : Int) : Int := 4 * m68 agi oth id brk

/-- Form line 4 (×74): line 1b = line 11b − (line 14) with line 12e = ID − §68 reduction; plus line 2a taxes and
the other adjustments. -/
def formAmti74 (agi oth id taxes adj brk : Int) : Int :=
  74 * agi - (74 * (id + oth) - red74 agi oth id brk) + 74 * (taxes + adj)

/-- Statute (×74): §56(b)(1)(A)(ii) takes the taxes out of the deductions, §56(b)(1)(E) leaves §68 out. -/
def statAmti74 (agi oth id taxes adj : Int) : Int :=
  74 * (agi - oth - (id - taxes) + adj)

/-- **The form's AMTI exceeds the statute's by exactly the §68 reduction, for every input.** -/
theorem amti_gap (agi oth id taxes adj brk : Int) :
    formAmti74 agi oth id taxes adj brk - statAmti74 agi oth id taxes adj = red74 agi oth id brk := by
  unfold formAmti74 statAmti74; omega

/-- Exact affected set (AMTI level): the gap is positive iff there are itemized deductions and TI + ID is above
the 37% bracket start. -/
theorem amti_gap_pos_iff (agi oth id taxes adj brk : Int) :
    0 < formAmti74 agi oth id taxes adj brk - statAmti74 agi oth id taxes adj ↔ 0 < id ∧ brk < agi - oth := by
  rw [amti_gap]; unfold red74 m68; omega

/-- Single 2026 exemption ×148 (1/148 dollar): $90,100 less 50% of AMTI over $500,000, not below zero. -/
def ex148 (a74 : Int) : Int := max 0 (148 * 90100 - max 0 (a74 - 74 * 500000))

/-- Single 2026 tentative minimum tax (no gains) in 1/14,800 dollar: line 6 = AMTI − exemption; line 7. -/
def tmt (a74 : Int) : Int :=
  let x := max 0 (2 * a74 - ex148 a74)
  if x ≤ 148 * 244500 then 26 * x else 28 * x - 14800 * 4890

/-- AMT (line 11) given the regular tax (line 10) in the same units. -/
def amt (a74 reg : Int) : Int := max 0 (tmt a74 - reg)

/-- Above the exemption zero point ($680,200) every extra dollar of AMTI costs exactly 28 cents. -/
theorem tmt_gap_top (a r : Int) (ha : 74 * 680200 ≤ a) (hr : 0 ≤ r) :
    tmt (a + r) - tmt a = 28 * 2 * r := by
  unfold tmt ex148; simp only; split <;> split <;> omega

/-- For every AMTI ≥ 0, extra AMTI r costs between 0 and 42% of r (28% × 1.5 inside the exemption phase-out). -/
theorem tmt_gap_le (a r : Int) (ha : 0 ≤ a) (hr : 0 ≤ r) :
    0 ≤ tmt (a + r) - tmt a ∧ tmt (a + r) - tmt a ≤ 42 * 2 * r := by
  unfold tmt ex148; simp only; split <;> split <;> omega

/-- The AMT itself moves by no more than the tentative minimum tax, and by exactly as much when the statute's
filer already owes AMT. -/
theorem amt_gap (a r reg : Int) (hr : 0 ≤ tmt (a + r) - tmt a) :
    amt (a + r) reg - amt a reg ≤ tmt (a + r) - tmt a ∧
    (reg ≤ tmt a → amt (a + r) reg - amt a reg = tmt (a + r) - tmt a) := by
  unfold amt; omega

/-- **Headline (single, 2026): if the statute's AMTI is at least $680,200 and the filer owes AMT under the statute,
the draft form's AMT is too high by exactly 28% × (2/37) × min(ID, TI + ID − $640,600)** (in 1/14,800 dollar:
224 × m; for any ID ≤ TI + ID − $640,600 that is 1.5135% of the itemized deductions). -/
theorem headline (agi oth id taxes adj reg : Int) (hid : 0 ≤ id)
    (hs : 74 * 680200 ≤ statAmti74 agi oth id taxes adj) (howes : reg ≤ tmt (statAmti74 agi oth id taxes adj)) :
    amt (formAmti74 agi oth id taxes adj 640600) reg - amt (statAmti74 agi oth id taxes adj) reg
      = 224 * m68 agi oth id 640600 := by
  have hg := amti_gap agi oth id taxes adj 640600
  have hm : 0 ≤ m68 agi oth id 640600 := by unfold m68; omega
  have hr4 : red74 agi oth id 640600 = 4 * m68 agi oth id 640600 := rfl
  have hf : formAmti74 agi oth id taxes adj 640600
      = statAmti74 agi oth id taxes adj + red74 agi oth id 640600 := by omega
  rw [hf]
  have ht := tmt_gap_top (statAmti74 agi oth id taxes adj) (red74 agi oth id 640600) hs (by unfold red74; omega)
  have ha := (amt_gap (statAmti74 agi oth id taxes adj) (red74 agi oth id 640600) reg (by omega)).2 howes
  rw [ha, ht]; omega

/-- Upper bound for every single 2026 filer (any AMTI ≥ 0, any regular tax): AMT too high by at most 42% of the §68
reduction, i.e. at most 336/14,800 per unit of m (≈ 2.27% of itemized deductions). -/
theorem bound (agi oth id taxes adj reg : Int) (hid : 0 ≤ id) (hs : 0 ≤ statAmti74 agi oth id taxes adj) :
    amt (formAmti74 agi oth id taxes adj 640600) reg - amt (statAmti74 agi oth id taxes adj) reg
      ≤ 336 * m68 agi oth id 640600 := by
  have hg := amti_gap agi oth id taxes adj 640600
  have hm : 0 ≤ m68 agi oth id 640600 := by unfold m68; omega
  have hr4 : red74 agi oth id 640600 = 4 * m68 agi oth id 640600 := rfl
  have hf : formAmti74 agi oth id taxes adj 640600
      = statAmti74 agi oth id taxes adj + red74 agi oth id 640600 := by omega
  rw [hf]
  have ht := tmt_gap_le (statAmti74 agi oth id taxes adj) (red74 agi oth id 640600) hs (by unfold red74; omega)
  have ha := (amt_gap (statAmti74 agi oth id taxes adj) (red74 agi oth id 640600) reg ht.1).1
  omega

/-! ## Worked examples (single, 2026). AGI $1,400,000; itemized deductions $100,000 of which $10,000 taxes (the SALT
floor at this income); $2,000,000 ISO bargain element (line 2i). Statute AMTI $3,310,000; form $3,315,405.41.
Regular tax on $1,305,405.41 = $438,957.25 (in 1/14,800: 6,496,567,300), so AMT is owed either way. -/

example : statAmti74 1400000 0 100000 10000 2000000 = 74 * 3310000 := by decide
example : red74 1400000 0 100000 640600 = 400000 := by decide          -- $5,405.41 (= 400000/74)
example : amt (formAmti74 1400000 0 100000 10000 2000000 640600) 6496567300
        - amt (statAmti74 1400000 0 100000 10000 2000000) 6496567300 = 22400000 := by decide  -- $1,513.51
/-- $1,000,000 of itemized deductions (e.g. a large gift), same facts otherwise: AMT too high by $15,135.14. -/
example : amt (formAmti74 2300000 0 1000000 10000 2000000 640600) 0
        - amt (statAmti74 2300000 0 1000000 10000 2000000) 0 = 224000000 := by decide

end TaxCode.Big.Form6251Sec68

#print axioms TaxCode.Big.Form6251Sec68.headline
#print axioms TaxCode.Big.Form6251Sec68.bound
#print axioms TaxCode.Big.Form6251Sec68.amti_gap_pos_iff
