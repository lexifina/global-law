import TaxCode.Individual.A.SocialSecurity
import TaxCode.Individual.A.Adjustments

/-!
# §61 gross income, §62 adjusted gross income, and §1411 net investment income tax

## The §86 / §219 / §221 circularity, and how it is resolved here

Three provisions each read a "modified adjusted gross income" that depends on the others:

* §86(b)(2): AGI "determined without regard to this section and sections ... 221 ..." — so *with* the §219 IRA
  deduction.
* §219(g)(3)(A): AGI "after application of sections 86 and 469" and "without regard to ... 221 ... or the deduction
  allowable under this section".
* §221(b)(2)(C): AGI "without regard to this section" and "after application of sections 86, 135, 137, 219, and 469".

§221 is downstream of both others and causes no loop. §86 and §219 read each other. Pub 590-A (2025) Appendix B
(Worksheets 1–3) and Pub 915 (2025) resolve it in sequence, which is what `agiSteps` does:

1. `ss0`: taxable benefits figured with *no* IRA deduction (Pub 590-A Appendix B Worksheet 1, lines 1–17).
2. `ira`: the IRA deduction with `magi219 = base + ss0` (Worksheet 1 line 19 → Worksheet 2).
3. `ss`: taxable benefits again, now with the IRA deduction subtracted (Worksheet 3) — this is the §86 amount.
4. `sli`: student loan interest with `magi221 = base + ss − ira` (Pub 970 Worksheet 4-1).
5. `agi = base + ss − ira − sli`.

This is the reading in which "without regard to the deduction allowable under this section" in §219(g)(3)(A)(ii) also
governs the §86 computation that (i) applies. Under the other reading — §219's MAGI uses the *final* §86 amount, so the
IRA deduction is a fixed point of `iraMap` — the fixed point need not be unique (`ira_two_fixed_points`), the IRS
sequence's answer need not be one (`worksheet_not_fixed_point`), but every fixed point is at least the IRS answer
(`worksheet_ira_le_every_fixed_point`). See FINDINGS.md.
-/

namespace TaxCode.Individual.A
open TaxCode.Individual

/-! ## §61 gross income and §62(a)(3) capital losses -/

/-- Net capital gain or loss line (Form 1040 line 7): a net loss is allowed only up to $3,000 ($1,500 married filing
separately) by §1211(b). -/
def capitalGainLine (h : Household) : Int :=
  let n := h.shortTermGains + h.longTermGains
  if 0 ≤ n then n else max n (if h.filing == .mfs then -1500 else -3000)

/-- §61(a) gross income except social security, from the items `Household` carries: compensation (a)(1) (`wages`),
business income (a)(2) (`seIncome`, already net of the business's own deductions), gains (a)(3), interest (a)(4),
dividends (a)(7), pensions and IRA distributions (a)(8),(10) (taxable amounts), unemployment compensation (§85), and
other income. Tax-exempt interest is excluded (§103). -/
def grossIncomeExceptSS (h : Household) : Int :=
  h.wages + h.seIncome + h.taxableInterest + h.ordinaryDividends + max 0 (capitalGainLine h) +
    h.iraDistributions + h.pensions + h.unemployment + h.otherIncome

/-- §62(a)(3) "losses from sale or exchange of property", as limited by §1211(b). -/
def capitalLossDeduction (h : Household) : Int := max 0 (- capitalGainLine h)

/-- The §62 adjustments that depend on no MAGI: §62(a)(2)(D) educator expenses, §62(a)(1) with §164(f) one-half of
self-employment tax, §62(a)(19) HSA, §62(a)(3) capital loss. -/
def fixedAdjustments (h : Household) : Int :=
  educatorDeduction h + halfSeTax h + hsaDeduction h + capitalLossDeduction h

/-- AGI before social security, the IRA deduction and student loan interest. -/
def agiBase (h : Household) : Int := grossIncomeExceptSS h - fixedAdjustments h

/-- The steps of the AGI computation (see the module docstring). -/
structure AgiSteps where
  base : Int
  ss0 : Int        -- §86 amount ignoring §219
  magi219 : Int    -- §219(g)(3)(A)
  ira : Int
  ss : Int         -- §86 amount
  magi221 : Int    -- §221(b)(2)(C)
  sli : Int
  agi : Int
  deriving Repr

def agiSteps (h : Household) (livedApart : Bool := false) : AgiSteps :=
  let base := agiBase h
  let ss0 := taxableSocialSecurityGiven h livedApart base
  let magi219 := base + ss0
  let ira := iraDeduction h magi219 livedApart
  let ss := taxableSocialSecurityGiven h livedApart (base - ira)
  let magi221 := base + ss - ira
  let sli := studentLoanDeduction h magi221
  { base, ss0, magi219, ira, ss, magi221, sli, agi := magi221 - sli }

/-- §86: the taxable part of social security benefits (Form 1040 line 6b). -/
def taxableSocialSecurity (h : Household) (livedApart : Bool := false) : Int := (agiSteps h livedApart).ss

/-- §62(a): adjusted gross income (Form 1040 line 11). -/
def agi (h : Household) (livedApart : Bool := false) : Int := (agiSteps h livedApart).agi

/-- §61 gross income including the §86 amount. -/
def grossIncome (h : Household) (livedApart : Bool := false) : Int :=
  grossIncomeExceptSS h + taxableSocialSecurity h livedApart

/-- The exposed IRA deduction given §219 MAGI. -/
def iraDeductionOf (h : Household) (magiBeforeIra : Int) : Int := iraDeduction h magiBeforeIra

/-- The exposed student loan deduction given §221 MAGI. -/
def studentLoanDeductionOf (h : Household) (magi : Int) : Int := studentLoanDeduction h magi

/-! ## The circularity -/

/-- The "simultaneous" reading of §219(g)(3)(A)(i): the IRA deduction `x` must equal the deduction computed from a
MAGI that includes the §86 amount figured *with* `x` subtracted. -/
def iraMap (h : Household) (livedApart : Bool) (x : Int) : Int :=
  iraDeduction h (agiBase h + taxableSocialSecurityGiven h livedApart (agiBase h - x)) livedApart

/-- The IRS sequence computes `iraMap` at zero. -/
theorem agiSteps_ira (h : Household) (la : Bool) : (agiSteps h la).ira = iraMap h la 0 := by
  simp [agiSteps, iraMap]

/-- `iraMap` is monotone: a larger IRA deduction lowers §86 MAGI, so lowers taxable benefits, so lowers §219 MAGI,
so raises the IRA deduction. -/
theorem iraMap_mono (h : Household) (la : Bool) {x y : Int} (hxy : x ≤ y) : iraMap h la x ≤ iraMap h la y := by
  unfold iraMap
  apply iraDeduction_antitone
  have := taxableSocialSecurityGiven_mono h la (agiBase h - y) (agiBase h - x) (by omega)
  omega

/-- Every non-negative fixed point of the simultaneous reading is at least the IRS worksheet's IRA deduction: the
worksheets never give *more* than the statute could. -/
theorem worksheet_ira_le_every_fixed_point (h : Household) (la : Bool) (x : Int) (hx : 0 ≤ x)
    (hfix : iraMap h la x = x) : (agiSteps h la).ira ≤ x := by
  rw [agiSteps_ira, ← hfix]
  exact iraMap_mono h la hx

/-- The IRA deduction does not depend on MAGI at all when nobody is an active participant. -/
theorem iraDeduction_const_of_not_covered (h : Household) (la : Bool) (hp : h.activeParticipant = false)
    (m m' : Int) : iraDeduction h m la = iraDeduction h m' la := by
  simp [iraDeduction, iraCoverage, personLimit, iraApplicableAmount, hp]

/-- So without an active participant the circularity is vacuous: the simultaneous reading has exactly one fixed
point, and it is the IRS worksheet's answer. -/
theorem fixed_point_unique_of_not_covered (h : Household) (la : Bool) (hp : h.activeParticipant = false) (x : Int) :
    iraMap h la x = x ↔ x = (agiSteps h la).ira := by
  rw [agiSteps_ira]
  unfold iraMap
  rw [iraDeduction_const_of_not_covered h la hp _ (agiBase h + taxableSocialSecurityGiven h la (agiBase h - 0))]
  constructor <;> intro e <;> omega

/-- The two MAGIs differ: §221 MAGI never exceeds §219 MAGI (the IRA deduction is subtracted, and the §86 amount can
only fall when it is). -/
theorem magi221_le_magi219 (h : Household) (la : Bool) : (agiSteps h la).magi221 ≤ (agiSteps h la).magi219 := by
  simp only [agiSteps]
  have hb := iraDeduction_bounds h la (agiBase h + taxableSocialSecurityGiven h la (agiBase h))
  have := taxableSocialSecurityGiven_mono h la
    (agiBase h - iraDeduction h (agiBase h + taxableSocialSecurityGiven h la (agiBase h)) la) (agiBase h) (by omega)
  omega

/-- Taxable benefits in the final AGI never exceed 85% of benefits (to the nearest dollar). -/
theorem taxableSocialSecurity_le_85 (h : Household) (la : Bool) :
    0 ≤ taxableSocialSecurity h la ∧ 40 * taxableSocialSecurity h la ≤ 34 * max 0 h.socialSecurity + 20 :=
  taxableSocialSecurityGiven_bounds h la _

/-- The IRA deduction counted in AGI never makes the §86 amount larger than it is without the IRA deduction. -/
theorem ss_le_ss0 (h : Household) (la : Bool) : (agiSteps h la).ss ≤ (agiSteps h la).ss0 := by
  simp only [agiSteps]
  have hb := iraDeduction_bounds h la (agiBase h + taxableSocialSecurityGiven h la (agiBase h))
  exact taxableSocialSecurityGiven_mono h la _ _ (by omega)

/-! ## §1411 net investment income tax -/

/-- §1411(b): $250,000 for a joint return "or a surviving spouse (as defined in section 2(a))"; $125,000 married
filing separately; $200,000 otherwise. Not indexed. -/
def niitThreshold : Filing → Int
  | .mfj => 250000
  | .qss => 250000
  | .mfs => 125000
  | _ => 200000

/-- §1411(c)(1): interest, dividends and net gain (a net capital loss is not a "net gain": floored at zero). Excluded:
tax-exempt interest (not gross income), IRA and pension distributions (§1411(c)(5)), social security, wages and
self-employment income (§1411(c)(6)). Rents, royalties, passive income and the (c)(1)(B) allocable deductions are not
in `Household`. -/
def netInvestmentIncome (h : Household) : Int :=
  max 0 (h.taxableInterest + h.ordinaryDividends + max 0 (h.shortTermGains + h.longTermGains))

/-- §1411(a)(1): 3.8% of the lesser of net investment income and MAGI over the threshold. MAGI is AGI (the §1411(d)
§911 add-back is not modelled). Rounded to the nearest dollar. -/
def niit (h : Household) (agi : Int) : Int :=
  roundDollar (38 * min (netInvestmentIncome h) (max 0 (agi - niitThreshold h.filing))) 1000

theorem netInvestmentIncome_nonneg (h : Household) : 0 ≤ netInvestmentIncome h := by
  unfold netInvestmentIncome; omega

theorem niit_nonneg (h : Household) (a : Int) : 0 ≤ niit h a := by
  have := netInvestmentIncome_nonneg h
  unfold niit roundDollar
  omega

/-- NIIT never exceeds 3.8% of net investment income, nor 3.8% of MAGI over the threshold (to the nearest dollar). -/
theorem niit_le (h : Household) (a : Int) :
    1000 * niit h a ≤ 38 * netInvestmentIncome h + 500 ∧
    1000 * niit h a ≤ 38 * max 0 (a - niitThreshold h.filing) + 500 := by
  have := netInvestmentIncome_nonneg h
  unfold niit roundDollar
  omega

theorem niit_mono (h : Household) {a a' : Int} (ha : a ≤ a') : niit h a ≤ niit h a' := by
  have := netInvestmentIncome_nonneg h
  unfold niit roundDollar
  omega

/-- One more dollar of MAGI adds at most 3.8 cents of NIIT (so at most $1 after rounding). -/
theorem niit_marginal (h : Household) (a : Int) : niit h (a + 1) ≤ niit h a + 1 := by
  have := netInvestmentIncome_nonneg h
  unfold niit roundDollar
  omega

theorem niit_zero_below (h : Household) (a : Int) (ha : a ≤ niitThreshold h.filing) : niit h a = 0 := by
  have := netInvestmentIncome_nonneg h
  unfold niit roundDollar
  omega

/-- The qualifying-surviving-spouse asymmetry: §1411(b)(1) names a surviving spouse alongside joint returns
($250,000), while §3101(b)(2)(C) and §1401(b)(2)(A)(iii) put a surviving spouse "in any other case" ($200,000). -/
theorem qss_thresholds_differ : niitThreshold .qss = 250000 ∧ amtThreshold .qss = 200000 := by decide

end TaxCode.Individual.A
