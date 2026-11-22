import TaxCode.Individual.A.AGI

/-!
# Group A tests: worked examples from IRS publications for tax year 2025, and the counterexamples behind FINDINGS.md

Every example below is from the 2025 edition of the IRS publication named (fetched from irs.gov, November 2026);
section names are given because the HTML editions have no page numbers. Where `Household` cannot carry an example's
facts, the core function is tested instead and the reason is given.
-/

namespace TaxCode.Individual.A.Tests
open TaxCode.Individual TaxCode.Individual.A

/-! ## §86 — Pub 915 (2025) -/

/-- Pub 915 (2025), "Worksheet A" example: single, benefits $1,500, pension $17,000, interest $700 → none taxable. -/
def p915_wkA : Household :=
  { filing := .single, head := { age := 66 }, socialSecurity := 1500, pensions := 17000, taxableInterest := 700 }
theorem p915_wkA_taxable : taxableSocialSecurity p915_wkA = 0 := by decide
theorem p915_wkA_agi : agi p915_wkA = 17700 := by decide

/-- Pub 915 (2025) "Examples", Example 1: single; pension $18,600, wages $9,400, interest $990; benefits $5,980.
Worksheet 1 line 19 = $2,990 (benefits capped at one-half: line 13 $6,980 → line 15 $2,990). -/
def p915_ex1 : Household :=
  { filing := .single, head := { age := 66 }, socialSecurity := 5980, pensions := 18600, wages := 9400,
    taxableInterest := 990 }
theorem p915_ex1_taxable : taxableSocialSecurity p915_ex1 = 2990 := by decide
theorem p915_ex1_agi : agi p915_ex1 = 28990 + 2990 := by decide

/-- Pub 915 (2025) Example 2 (Casey and Pat Hopkins): joint; Casey's pension $15,500; Pat's wages $14,000; interest
$250; Pat's deductible IRA payment $1,000 (not covered by a plan); benefits $5,600. Line 8 $31,550 does not exceed
$32,000: none taxable. -/
def p915_ex2 : Household :=
  { filing := .mfj, head := { age := 67 }, spouse := some { age := 60 }, socialSecurity := 5600, pensions := 15500,
    wages := 14000, wagesSpouse := 14000, taxableInterest := 250, iraContributions := 1000 }
theorem p915_ex2_taxable : taxableSocialSecurity p915_ex2 = 0 := by decide
theorem p915_ex2_ira : (agiSteps p915_ex2).ira = 1000 := by decide
theorem p915_ex2_line8 : (agiSteps p915_ex2).base - (agiSteps p915_ex2).ira + 5600 / 2 = 31550 := by decide

/-- Pub 915 (2025) Example 3 (Jamie and Jessie Johnson): joint; tier 1 benefits $10,000; pension $38,000; taxable
interest $2,300; $200 of savings bond interest excluded under §135 (added back by §86(b)(2)(A)). `Household` has no
§135 field; the $200 is entered as `taxExemptInterest`, which §86(b)(2)(B) adds back the same way. Line 19 = $6,275. -/
def p915_ex3 : Household :=
  { filing := .mfj, head := { age := 66 }, spouse := some { age := 66 }, socialSecurity := 10000, pensions := 38000,
    taxableInterest := 2300, taxExemptInterest := 200 }
theorem p915_ex3_taxable : taxableSocialSecurity p915_ex3 = 6275 := by decide

/-- Pub 915 (2025) Example 4 (Kris and Taylor Jones): married filing separately, lived together; Kris's wages
$8,000, benefits $4,000. Line 17 = 85% × $10,000 = $8,500; line 18 = $3,400; taxable $3,400. -/
def p915_ex4 : Household :=
  { filing := .mfs, head := { age := 64 }, socialSecurity := 4000, wages := 8000 }
theorem p915_ex4_taxable : taxableSocialSecurity p915_ex4 = 3400 := by decide
/-- The same facts living apart all year: base $25,000, so nothing is taxable. -/
theorem p915_ex4_apart : taxableSocialSecurity p915_ex4 (livedApart := true) = 0 := by decide

/-- Pub 915 (2025) lump-sum election example (Terry Jackson), Worksheet 1 (regular method): single; wages $3,500,
interest $2,500, dividends $1,500, pension $18,000; total benefits $11,000. Line 19 = $3,000. -/
def p915_jackson : Household :=
  { filing := .single, head := { age := 66 }, socialSecurity := 11000, wages := 3500, taxableInterest := 2500,
    ordinaryDividends := 1500, pensions := 18000 }
theorem p915_jackson_taxable : taxableSocialSecurity p915_jackson = 3000 := by decide

/-- Same example, Worksheet 4 lines 1–19 (benefits $9,000, line 3 $25,500): $2,500. And Worksheet 2 for 2024
(benefits $2,000, AGI $23,000): line 8 $24,000 does not exceed $25,000, nothing. The lump-sum election itself
(§86(e)) is not modelled; these test the §86(a) core only. -/
theorem p915_jackson_wk4 : taxableSS40 25000 34000 9000 25500 = 2500 * 40 := by decide
theorem p915_jackson_wk2 : taxableSS40 25000 34000 2000 23000 = 0 := by decide

/-- Every Pub 915 example above, through the literal Worksheet 1 as well (Example 3 line by line: line 10 $13,500,
line 12 $1,500, line 16 $1,275, line 17 $6,275). -/
theorem p915_ex3_worksheet : worksheet1_40 32000 44000 10000 40500 false = 6275 * 40 := by decide
theorem p915_ex4_worksheet : worksheet1_40 0 0 4000 8000 true = 3400 * 40 := by decide

/-! ## §219 — Pub 590-A (2025) -/

/-- Pub 590-A (2025) Worksheet 1-2, Example 2: joint return, the contributor is not covered but the spouse is
((g)(7): range $236,000–$246,000, 70%); MAGI $238,500; line 4 $5,250; compensation $38,500; deduction $5,250. -/
theorem p590a_wk12_ex2 : personLimit 40 .mfj false .spouseOnly 238500 = 5250 := by decide

/-- Pub 590-A (2025) Worksheet 1-2, Example 1: joint return, covered; MAGI $126,500; the IRS shows line 4 =
$19,500 × 35% = $6,825 and a $6,825 deduction. Under §219(g)(2)(C) the reduction ($175) is rounded down to $170,
leaving $6,830 — and the worksheet's own instruction ("round it to the next highest multiple of $10") also gives
$6,830. The statute value is asserted here; see FINDINGS.md. -/
theorem p590a_wk12_ex1_statute : personLimit 40 .mfj false .self 126500 = 6830 := by decide
theorem p590a_wk12_ex1_worksheet_rule : worksheet12 7000 20000 (126500 - 126000) = 6830 := by decide

/-- Pub 590-A (2025) Appendix B example: joint; age 65, covered by a 401(k); benefits $12,000; IRA contribution
$8,000. Worksheet 1: line 17 taxable benefits $10,200 (85% cap) with AGI before benefits $118,000; line 19 MAGI
$128,200. Worksheet 2: line 4 = $17,800 × 40% = $7,120; deduction $7,120. Worksheet 3: taxable benefits stay
$10,200. Tested on the core functions: the example's contribution belongs to one spouse, which `Household`'s single
`iraContributions` cannot express. -/
theorem p590a_appB_wk1 : taxableSS40 32000 44000 12000 118000 = 10200 * 40 := by decide
theorem p590a_appB_wk2 : personLimit 65 .mfj false .self (118000 + 10200) = 7120 := by decide
theorem p590a_appB_wk3 : taxableSS40 32000 44000 12000 (118000 - 7120) = 10200 * 40 := by decide

/-! ## §221 — Pub 970 (2025), chapter 4 -/

def p970_joint (interest : Int) : Household :=
  { filing := .mfj, head := { age := 30 }, spouse := some { age := 30 }, studentLoanInterest := interest }

/-- Pub 970 (2025) ch. 4, "Figuring the Deduction", phaseout example: joint, MAGI $185,000, interest $800:
reduction $800 × $15,000 / $30,000 = $400; deduction $400. -/
theorem p970_phaseout_800 : studentLoanDeduction (p970_joint 800) 185000 = 400 := by decide
/-- Same with $2,750 of interest: capped at $2,500, reduction $1,250, deduction $1,250. -/
theorem p970_phaseout_2750 : studentLoanDeduction (p970_joint 2750) 185000 = 1250 := by decide
/-- Pub 970 (2025) ch. 4, "Claimed as dependent" example: $1,100 of interest, claimed by parents: no deduction. -/
def p970_dep : Household :=
  { filing := .single, head := { age := 22 }, canBeClaimedAsDependent := true, studentLoanInterest := 1100 }
theorem p970_dependent : studentLoanDeduction p970_dep 30000 = 0 := by decide

/-! ## Additional Medicare tax — Form 8959 instructions (2025), examples -/

/-- Ann: single, $130,000 self-employment income, no wages: $0. -/
theorem i8959_ann : additionalMedicareCore .single 0 (130000 * 10000) = 0 := by decide
/-- Bob: single, $220,000 self-employment income: 0.9% × $20,000 = $180. -/
theorem i8959_bob : additionalMedicareCore .single 0 (220000 * 10000) = 180 := by decide
/-- Carl: single, $145,000 self-employment income, $130,000 wages: threshold reduced to $70,000; $675. -/
theorem i8959_carl : additionalMedicareCore .single 130000 (145000 * 10000) = 675 := by decide
/-- Don: married filing separately, $150,000 self-employment income, $200,000 wages: $675 + $1,350 = $2,025. -/
theorem i8959_don : additionalMedicareCore .mfs 200000 (150000 * 10000) = 2025 := by decide
/-- Erin and Frank: joint, wages $150,000 + $175,000: $675. -/
theorem i8959_erin_frank : additionalMedicareCore .mfj 325000 0 = 675 := by decide
/-- Kathleen and Liam: joint, Kathleen's wages $130,000, Liam's self-employment income $140,000: $180. -/
theorem i8959_kathleen_liam : additionalMedicareCore .mfj 130000 (140000 * 10000) = 180 := by decide
-- George/Helen and Ishmael/Judy turn on RRTA compensation, which `Household` does not carry.

/-! ## Counterexamples and contrasts recorded in FINDINGS.md -/

/-- A single covered worker, under 50, with $50,000 of social security benefits and wages `w`. -/
def torpedoWorker (w : Int) : Household :=
  { filing := .single, head := { age := 40 }, wages := w, socialSecurity := 50000, iraContributions := 7000,
    activeParticipant := true }

/-- Under the simultaneous reading of §219(g)(3)(A)(i), the IRA deduction is not uniquely determined: both $0 and
$200 are fixed points (the $200 floor of §219(g)(2)(B) lifts the deduction, the deduction lowers taxable benefits by
$170, and that lowered MAGI is inside the phase-out). The IRS sequence gives $0. -/
theorem ira_two_fixed_points :
    iraMap (torpedoWorker 49850) false 0 = 0 ∧ iraMap (torpedoWorker 49850) false 200 = 200 ∧
    (agiSteps (torpedoWorker 49850)).ira = 0 := by decide

/-- The IRS sequence's IRA deduction is not a fixed point of the simultaneous reading: with $45,000 of wages it
gives $6,230, but recomputing §219 MAGI with the resulting §86 amount gives $7,000 (itself a fixed point). -/
theorem worksheet_not_fixed_point :
    (agiSteps (torpedoWorker 45000)).ira = 6230 ∧ iraMap (torpedoWorker 45000) false 6230 = 7000 ∧
    iraMap (torpedoWorker 45000) false 7000 = 7000 := by decide

/-- Qualifying surviving spouse, covered, MAGI $100,000: the statute ((g)(3)(B)(ii), not a joint return) phases the
deduction out completely; Pub 590-A Table 1-2 (joint-return range) allows all $7,000. -/
theorem qss_ira_statute_vs_irs :
    personLimit 40 .qss false .self 100000 = 0 ∧
    reducedLimit 7000 (100000 - 126000) (iraRangeIRS .qss .self) = 7000 ∧
    iraApplicableAmountIRS .qss false .self = some 126000 := by decide

/-- The torpedo on a household: $100 more wages raises AGI by $185 (single filer in the 85% zone, no IRA); a single
extra dollar raises it by $2 after rounding taxable benefits to whole dollars. -/
def retiree (w : Int) : Household :=
  { filing := .single, head := { age := 67 }, wages := w, socialSecurity := 40000 }
theorem torpedo_household : agi (retiree 30001) - agi (retiree 30000) = 2 ∧
    agi (retiree 30100) - agi (retiree 30000) = 185 := by decide

/-- The §1402(b)(2) notch on a household: $433 vs $434 of self-employment profit. -/
theorem se_notch_household :
    seTax ({ filing := .single, head := { age := 40 }, seIncome := 433 } : Household) = 0 ∧
    seTax ({ filing := .single, head := { age := 40 }, seIncome := 434 } : Household) = 61 := by decide

/-! ## Reviewer additions -/

/-- Self-employment tax, hand-computed on Schedule SE (2025) lines 3–13 (no official worked example was reached):
$100,000 profit → line 4a $92,350; line 10 $11,451.40; line 11 $2,678.15; line 12 $14,129.55 → $14,130; line 13
$7,064.78 → $7,065. -/
theorem se_100k : seTaxCore 100000 0 = 14130 ∧ halfSeTaxCore 100000 0 = 7065 := by decide
/-- Same profit with $150,000 of social security wages: line 9 = $176,100 − $150,000 = $26,100; line 10 $3,236.40;
line 11 $2,678.15; total $5,914.55 → $5,915. -/
theorem se_100k_wages : seTaxCore 100000 150000 = 5915 := by decide
/-- Wages already at the base: only the 2.9% part, $2,678.15 → $2,678. -/
theorem se_100k_over_base : seTaxCore 100000 176100 = 2678 := by decide

/-- IRS "Questions and Answers on the Net Investment Income Tax", Q&A sale-of-residence example 2 (B and C): joint;
recognized gain $100,000 plus $125,000 of other net investment income; MAGI $300,000; NIIT $1,900. Interest stands in
for the other income. -/
def niit_bc : Household :=
  { filing := .mfj, head := { age := 50 }, spouse := some { age := 50 }, longTermGains := 100000,
    taxableInterest := 125000 }
theorem niit_bc_tax : netInvestmentIncome niit_bc = 225000 ∧ niit niit_bc 300000 = 1900 := by decide
/-- Same Q&A: single, wages $180,000 and $15,000 of dividends and capital gains; MAGI $195,000; no NIIT. -/
def niit_19 : Household :=
  { filing := .single, head := { age := 40 }, wages := 180000, ordinaryDividends := 10000, longTermGains := 5000 }
theorem niit_19_tax : agi niit_19 = 195000 ∧ niit niit_19 (agi niit_19) = 0 := by decide
/-- Same Q&A: single, wages $180,000, $90,000 of net investment income (a passive partnership there; dividends stand
in, since `Household` has no passive income); MAGI $270,000; NIIT $2,660. -/
def niit_20 : Household :=
  { filing := .single, head := { age := 40 }, wages := 180000, ordinaryDividends := 90000 }
theorem niit_20_tax : agi niit_20 = 270000 ∧ niit niit_20 (agi niit_20) = 2660 := by decide
/-- Reg. §1.1411-4(d)(2): "The calculation of net gain may not be less than zero" — a $3,000 net capital loss does not
reduce interest in net investment income, though it reduces AGI. -/
def niit_loss : Household :=
  { filing := .single, head := { age := 40 }, wages := 300000, taxableInterest := 20000, shortTermGains := -10000 }
theorem niit_loss_tax : netInvestmentIncome niit_loss = 20000 ∧ agi niit_loss = 317000 ∧
    niit niit_loss (agi niit_loss) = 760 := by decide

/-- §221(b)(2) boundaries for 2025 (joint $170,000–$200,000): full $2,500 at the start, nothing at the end, half
in the middle. -/
theorem sli_boundaries : studentLoanDeduction (p970_joint 2750) 170000 = 2500 ∧
    studentLoanDeduction (p970_joint 2750) 200000 = 0 ∧ studentLoanDeduction (p970_joint 2750) 199999 = 0 ∧
    studentLoanDeduction (p970_joint 2750) 185000 = 1250 := by decide

end TaxCode.Individual.A.Tests
