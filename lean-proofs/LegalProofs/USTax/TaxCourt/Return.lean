import LegalProofs.USTax.TaxCourt.CTC
import LegalProofs.USTax.TaxCourt.Income
import LegalProofs.USTax.TaxCourt.EarlyDistribution
import LegalProofs.USTax.TaxCourt.Penalties
import LegalProofs.USTax.TaxCourt.Education
import LegalProofs.USTax.TaxCourt.Retirement

/-!
# A simple individual return, 2012–2024, and the deficiency

`computeReturn p r` runs Form 1040 for one year from the facts in `ReturnFacts`: income (wages, self-employment,
interest, dividends, capital gain, retirement distributions, social security, unemployment, other) → adjustments →
AGI → standard deduction or itemized deductions → personal exemptions (2012–2017) → taxable income → the regular tax
(Tax Table / schedule / capital-gain worksheet) → nonrefundable credits (other, then CTC/ODC) → SE tax, §72(t),
other taxes → refundable credits (EIC, ACTC / 2021 refundable CTC, other).

`deficiency` (§6211(a)): the tax as recomputed less the tax shown, with refundable credits counted as negative tax
(§6211(b)(4)). Withholding and estimated payments are not "tax shown" (§6211(b)(1)) and do not enter it.

Items given as amounts the court found (not computed here): the adjustments to income other than one-half of SE
tax, itemized deductions (after §68 in 2013–2017), the §199A deduction, other credits and other taxes (NIIT,
additional Medicare tax, §5000A payment, household employment taxes, recapture).

Not modelled: AMT (give it in `otherTaxes`), kiddie tax, foreign income, Schedule D worksheet (28% / §1250 gain),
§1(g); MFS spouses' allocation rules; the 2018 §63(c)(5) earned-income rule for dependents' unearned income
details beyond §63(c)(5).
-/

namespace Legal.USTax.TaxCourt
open TaxCode.Individual

/-- The facts of one year's return, as the court finds them (or as filed). -/
structure ReturnFacts where
  filing : Filing := .single
  /-- Ages at the close of the year; `spouseAge` is read on joint returns (and for §63(f) on separate returns when
  `spouseExemption`). -/
  taxpayerAge : Nat := 40
  taxpayerBlind : Bool := false
  spouseAge : Nat := 40
  spouseBlind : Bool := false
  /-- Separate return, spouse with no gross income and not another's dependent (§151(b), §63(f)(1)(B)). -/
  spouseExemption : Bool := false
  /-- Someone else can claim the taxpayer as a dependent (§63(c)(5), §151(d)(2), §152(b)(1)). -/
  canBeClaimedAsDependent : Bool := false
  dependents : List PersonFacts := []
  -- income
  wages : Int := 0
  wagesSpouse : Int := 0
  /-- Net profit from self-employment (Schedules C, F, partnership SE income), taxpayer and spouse. -/
  seProfit : Int := 0
  seProfitSpouse : Int := 0
  taxableInterest : Int := 0
  taxExemptInterest : Int := 0
  ordinaryDividends : Int := 0
  qualifiedDividends : Int := 0
  /-- Schedule D line 16: net capital gain or loss, before the §1211(b) $3,000 limit. -/
  capitalGain : Int := 0
  /-- Schedule D line 15: net long-term gain or loss. -/
  longTermGain : Int := 0
  /-- Taxable IRA distributions and taxable pensions and annuities (Form 1040 lines 4b, 5b). -/
  iraDistributions : Int := 0
  pensions : Int := 0
  socialSecurity : Int := 0
  /-- Married filing separately: lived apart from the spouse all year (§86(c)(1)(C)). -/
  livedApartAllYear : Bool := false
  unemployment : Int := 0
  unemploymentSpouse : Int := 0
  otherIncome : Int := 0
  -- adjustments and deductions
  /-- Adjustments other than one-half of SE tax, as allowed (IRA, student loan interest, HSA, alimony, ...). -/
  adjustments : Int := 0
  /-- Cash charity of a non-itemizer: 2020 §62(a)(22) (up to $300 per return); 2021 §170(p) ($300; $600 joint). -/
  charityNonItemizer : Int := 0
  itemizedDeductions : Int := 0
  /-- `some true`: itemize; `some false`: standard deduction; `none`: the larger. -/
  itemize : Option Bool := none
  /-- Married filing separately and the spouse itemizes (§63(c)(6)(A)): no standard deduction. -/
  spouseItemizes : Bool := false
  qbiDeduction : Int := 0
  -- credits and other taxes
  otherNonrefundableCredits : Int := 0
  otherRefundableCredits : Int := 0
  otherTaxes : Int := 0
  earlyDistributions : List EarlyDistFacts := []
  /-- Whether the EIC and the child tax credit are claimed (a court that disallows them for a reason not modelled
  can set these to false). -/
  claimEIC : Bool := true
  claimCTC : Bool := true
  -- facts read by the EIC and CTC
  taxpayerSSN : Bool := true
  taxpayerTIN : Bool := true
  taxpayerQualifyingChildOfAnother : Bool := false
  abodeInUS : Bool := true
  specifiedStudent : Bool := false
  fosterOrHomelessYouth : Bool := false
  separatedSpouse : Bool := false
  disallowed32k : Bool := false
  /-- Net rents, royalties and passive income (§32(i)(2)(C)–(E)). -/
  otherDisqualifiedIncome : Int := 0
  /-- 2020 / 2021: earned income of 2019 if the taxpayer elects to use it (Pub. L. 116-260 div. EE §211; ARPA
  §9626). -/
  priorYearEarnedIncome : Option Int := none
  advanceCtc : Int := 0
  advanceCtcChildren : Nat := 0
  -- payments
  withholding : Int := 0
  estimatedPayments : Int := 0
  -- items added Nov 2026 (all optional)
  /-- §25A: each student for whom an education credit is claimed. -/
  students : List StudentFacts := []
  /-- §25A(i)(5): the taxpayer is a child to whom §1(g) applies (no refundable AOTC). -/
  educationKiddieRule : Bool := false
  /-- §219: traditional IRA contributions and active-participant status, taxpayer and spouse. -/
  ira : IraFacts := {}
  iraSpouse : IraFacts := {}
  /-- §408(d)(3): distributions claimed to have been rolled over (only the includible part enters income). -/
  rollovers : List RolloverFacts := []
  /-- §223(f): HSA distributions, the qualified medical expenses they paid, and whether a (f)(4)(B)–(C) exception
  (death, disability, 65) applies (the taxpayer's age 65 counts automatically). -/
  hsaDistributions : Int := 0
  hsaQualifiedExpenses : Int := 0
  hsaException : Bool := false
  /-- §165(d): wagering gains (in gross income) and losses (itemized, up to the gains); expenses count 2018–2025. -/
  gamblingWinnings : Int := 0
  gamblingLosses : Int := 0
  gamblingExpenses : Int := 0
  /-- §86(e): parts of `socialSecurity` attributable to earlier years (the election is made if it lowers the tax). -/
  ssLumpSums : List LumpSumFacts := []
  /-- When the opinion gives only totals: AGI as found (replaces the computed AGI) and earned income as found. -/
  agiOverride : Option Int := none
  earnedIncomeOverride : Option Int := none
  deriving Repr, Inhabited

/-- Form 1040, line by line. -/
structure ReturnResult where
  filing : Filing
  totalIncome : Int
  taxableSocialSecurity : Int
  unemploymentExcluded : Int
  halfSeTax : Int
  /-- Total adjustments to income (Form 1040 "adjustments"): one-half of SE tax, the given adjustments, the 2020
  §62(a)(22) charity deduction. -/
  adjustments : Int
  agi : Int
  standardDeduction : Int
  deduction : Int
  exemptions : Int
  taxableIncome : Int
  regularTax : Int
  ctcNonrefundable : Int
  nonrefundableCredits : Int
  seTax : Int
  earlyDistributionTax : Int
  excessAdvanceCtc : Int
  totalTax : Int
  earnedIncome : Int
  eic : Int
  eicReasons : List String
  refundableCtc : Int
  refundableCredits : Int
  /-- Total tax less refundable credits: "tax" for §6211 (`netTax` > 0 owed before payments; < 0 refund). -/
  netTax : Int
  payments : Int
  dependentsCounted : Nat
  iraDeduction : Int := 0
  rolloverIncludible : Int := 0
  hsaIncludible : Int := 0
  hsaAdditionalTax : Int := 0
  gamblingLossDeduction : Int := 0
  /-- §25A: AOTC + LLC allowed against tax, and the refundable AOTC. -/
  educationNonrefundable : Int := 0
  aotcRefundable : Int := 0
  lumpSumElection : Bool := false
  deriving Repr, Inhabited

/-- §63(c)–(f): the standard deduction. -/
def standardDeduction (p : Params) (r : ReturnFacts) (f : Filing) (earned : Int) : Int :=
  if f == .mfs && r.spouseItemizes then 0 else
  let basic0 := p.basicStd f
  let basic := if r.canBeClaimedAsDependent then min basic0 (max p.depMin (earned + p.depAddon)) else basic0
  let married := f == .mfj || f == .mfs || f == .qss
  let per := if married then p.addlMarried else p.addlUnmarried
  let spouseCounts := f == .mfj || (f == .mfs && r.spouseExemption)
  let boxes : Nat := (if r.taxpayerAge ≥ 65 then 1 else 0) + (if r.taxpayerBlind then 1 else 0) +
    (if spouseCounts then (if r.spouseAge ≥ 65 then 1 else 0) + (if r.spouseBlind then 1 else 0) else 0)
  basic + per * boxes

/-- §151 (2012–2017): exemptions for the taxpayer, spouse and dependents, reduced by the §151(d)(3) phase-out (2013–2017;
none in 2012):
2 percentage points for each $2,500 ($1,250 separate) or fraction of AGI over the threshold. Zero from 2018. -/
def exemptions (p : Params) (f : Filing) (agi : Int) (count : Nat) : Int :=
  if p.exemption = 0 then 0 else
  if p.pepThreshold f = 0 then p.exemption * count else
  let total := p.exemption * count
  let step := if f == .mfs then 1250 else 2500
  let pct := min 100 (2 * ceilDiv (pos (agi - p.pepThreshold f)) step)
  total - total * pct / 100

/-- **The return.** -/
def computeReturn (p : Params) (r : ReturnFacts) : ReturnResult :=
  let f := r.filing
  -- self-employment tax, per individual
  let seT := seTaxP p r.seProfit r.wages
  let seS := seTaxP p r.seProfitSpouse r.wagesSpouse
  let halfSe := halfSeTaxP p r.seProfit r.wages + halfSeTaxP p r.seProfitSpouse r.wagesSpouse
  -- capital loss limit §1211(b)
  let capInc := if r.capitalGain < 0 then max r.capitalGain (if f == .mfs then -1500 else -3000) else r.capitalGain
  let uc := r.unemployment + r.unemploymentSpouse
  let rollInc := r.rollovers.foldl (fun t x => t + rolloverIncludible x) 0
  -- §213(f) (2013–2016): "the taxpayer or the taxpayer's spouse", whatever the filing status
  let someone65 := r.taxpayerAge ≥ 65 || ((f == .mfj || f == .mfs) && r.spouseAge ≥ 65)
  let hsa := hsaDistribution p.year r.hsaDistributions r.hsaQualifiedExpenses (r.hsaException || r.taxpayerAge ≥ 65)
  let income0 := r.wages + r.wagesSpouse + r.seProfit + r.seProfitSpouse + r.taxableInterest + r.ordinaryDividends +
    capInc + r.iraDistributions + r.pensions + uc + r.otherIncome + rollInc + hsa.1 + pos r.gamblingWinnings
  -- earned income (§32(c)(2)), also §63(c)(5)
  let earnedT := r.wages + (r.seProfit - halfSeTaxP p r.seProfit r.wages)
  let earnedS := r.wagesSpouse + (r.seProfitSpouse - halfSeTaxP p r.seProfitSpouse r.wagesSpouse)
  let earned := r.earnedIncomeOverride.getD (earnedT + earnedS)
  let std := standardDeduction p r f earned
  -- 2020 §62(a)(22) and 2021 §170(p): only for a taxpayer who does not itemize; the choice compares totals
  let charity := if p.year == 2020 then min (pos r.charityNonItemizer) 300
    else if p.year == 2021 then min (pos r.charityNonItemizer) (if f == .mfj then 600 else 300) else 0
  let gambling := gamblingLossDeduction p.year r.gamblingWinnings r.gamblingLosses r.gamblingExpenses
  let itemized := r.itemizedDeductions + gambling
  let usesStd := match r.itemize with
    | some b => !b
    | none => std + charity ≥ itemized
  let ded := if usesStd then std else itemized
  let charity2020 := if p.year == 2020 && usesStd then charity else 0
  let charity2021 := if p.year == 2021 && usesStd then charity else 0
  let adj0 := halfSe + r.adjustments + charity2020
  -- §86: MAGI = AGI without §86 (and, here, with the given adjustments) plus tax-exempt interest; §86(b)(2)(A)
  -- disregards §85(c), so 2020 unemployment counts in full here (the exclusion is applied afterwards)
  let tssOf (adj : Int) : Int × Bool :=
    let m := income0 - adj + r.taxExemptInterest
    let plain := taxableSocialSecurity f r.livedApartAllYear r.socialSecurity m
    if r.ssLumpSums.isEmpty then (plain, false) else
    let el := lumpSumElectionTaxable f r.livedApartAllYear r.socialSecurity m r.ssLumpSums
    if el < plain then (el, true) else (plain, false)
  -- §219(g)(3)(A): MAGI is AGI without the IRA deduction (taxable social security refigured without it)
  let agiNoIra0 := income0 + (tssOf adj0).1 - adj0
  let agiNoIra := agiNoIra0 - unemploymentExclusion p.year r.unemployment r.unemploymentSpouse agiNoIra0
  let iraD := iraDeduction p f r.livedApartAllYear r.taxpayerAge r.spouseAge earnedT earnedS agiNoIra r.ira
    r.iraSpouse
  let adj := adj0 + iraD.1 + iraD.2
  let tssR := tssOf adj
  let tss := tssR.1
  let agi0 := income0 + tss - adj
  let ucx := unemploymentExclusion p.year r.unemployment r.unemploymentSpouse agi0
  let agi := r.agiOverride.getD (agi0 - ucx)
  -- exemptions (2016–2017)
  let deps := r.dependents.filter (isDependent p r.canBeClaimedAsDependent)
  let selfCount : Nat := (if r.canBeClaimedAsDependent then 0 else 1) +
    (if f == .mfj || (f == .mfs && r.spouseExemption) then 1 else 0)
  let ex := exemptions p f agi (selfCount + deps.length)
  let ti := pos (agi - ded - ex - r.qbiDeduction - charity2021)
  -- the regular tax
  let cgPref := if r.capitalGain > 0 && r.longTermGain > 0 then min r.capitalGain r.longTermGain else 0
  let tax := regularTax p f ti (pos r.qualifiedDividends + cgPref)
  -- credits: the other nonrefundable credits, then §25A, then §24 (Form 1040 order)
  let edu := educationCredits p f agi r.students r.educationKiddieRule
  let otherNonref0 := min (pos r.otherNonrefundableCredits) tax
  let eduNonref := min edu.nonrefundable (tax - otherNonref0)
  let otherNonref := otherNonref0 + eduNonref
  let edTax := r.earlyDistributions.foldl (fun s d => s + earlyDistAmount p agi someone65 d) 0
  let kids := eicChildCounts p r.dependents
  let earnedEic := match r.priorYearEarnedIncome with
    | some e => if (p.year == 2020 || p.year == 2021) && e > earned then e else earned
    | none => earned
  let disq := r.taxableInterest + r.taxExemptInterest + r.ordinaryDividends + pos r.capitalGain +
    r.otherDisqualifiedIncome
  let eicR := if r.claimEIC then
      eicAmount p
        { filing := f, earnedIncome := earnedEic, agi := agi, disqualifiedIncome := disq,
          taxpayerAge := r.taxpayerAge, spouseAge := if f == .mfj then some r.spouseAge else none,
          taxpayerSSN := r.taxpayerSSN, qualifyingChildOfAnother := r.taxpayerQualifyingChildOfAnother,
          canBeClaimedAsDependent := r.canBeClaimedAsDependent, abodeInUS := r.abodeInUS,
          specifiedStudent := r.specifiedStudent, fosterOrHomelessYouth := r.fosterOrHomelessYouth,
          separatedSpouse := r.separatedSpouse, disallowed32k := r.disallowed32k } kids
    else (0, ["EIC not claimed"])
  let counts := ctcCounts p r.taxpayerTIN r.canBeClaimedAsDependent r.dependents
  let earnedCtc := match r.priorYearEarnedIncome with
    | some e => if p.year == 2020 && e > earned then e else earned
    | none => earned
  let ssTaxes := employeeFicaP p r.wages + employeeFicaP p r.wagesSpouse + halfSe
  let ctcR : CtcResult := if r.claimCTC then
      ctcFor p counts
        { filing := f, magi := agi, taxLeft := tax - otherNonref, earnedIncome := earnedCtc,
          ssTaxes := ssTaxes, eic := eicR.1, usAbode := r.abodeInUS, advancePayments := r.advanceCtc,
          advanceChildren := r.advanceCtcChildren }
    else {}
  let nonref := otherNonref + ctcR.nonrefundable
  let totalTax := pos (tax - nonref) + seT + seS + edTax + r.otherTaxes + ctcR.excessAdvance + hsa.2
  let refundable := eicR.1 + ctcR.refundable + r.otherRefundableCredits + edu.aotcRefundable
  { filing := f, totalIncome := income0 + tss - ucx, taxableSocialSecurity := tss, unemploymentExcluded := ucx,
    halfSeTax := halfSe, adjustments := adj, agi := agi, standardDeduction := std, deduction := ded, exemptions := ex,
    taxableIncome := ti, regularTax := tax, ctcNonrefundable := ctcR.nonrefundable, nonrefundableCredits := nonref,
    seTax := seT + seS, earlyDistributionTax := edTax, excessAdvanceCtc := ctcR.excessAdvance,
    totalTax := totalTax, earnedIncome := earned, eic := eicR.1, eicReasons := eicR.2,
    refundableCtc := ctcR.refundable, refundableCredits := refundable, netTax := totalTax - refundable,
    payments := r.withholding + r.estimatedPayments, dependentsCounted := deps.length,
    iraDeduction := iraD.1 + iraD.2, rolloverIncludible := rollInc, hsaIncludible := hsa.1, hsaAdditionalTax := hsa.2,
    gamblingLossDeduction := if usesStd then 0 else gambling, educationNonrefundable := eduNonref,
    aotcRefundable := edu.aotcRefundable, lumpSumElection := tssR.2 }

/-- §6211(a), (b)(4): the deficiency — tax as recomputed less tax shown, refundable credits as negative tax. Negative
means the return overstated the tax. -/
def deficiencyOf (corrected : ReturnResult) (shownNetTax : Int) : Int := corrected.netTax - shownNetTax

/-! ## Tests: worked returns -/

section
private def py (y : Nat) : Params := (params? y).getD default

-- 2016 single, wages $40,000: standard deduction $6,300 + exemption $4,050: taxable $29,650; Tax Table
-- 29,650–29,700 single: $3,988 (2016 Form 1040 instructions).
#guard (computeReturn (py 2016) { wages := 40000 }).taxableIncome = 29650
#guard (computeReturn (py 2016) { wages := 40000 }).regularTax = 3988
-- 2024 single, wages $40,000: $14,600 standard deduction: taxable $25,400; Table 25,400–25,450 single: $2,819.
#guard (computeReturn (py 2024) { wages := 40000 }).regularTax = 2819
-- 2016 personal-exemption phase-out: joint AGI $361,300 is $50,000 over $311,300: 20 steps of $2,500 = 40% lost.
#guard exemptions (py 2016) .mfj 361300 4 = 16200 - 6480
-- 2018 joint, both 66: $24,000 + 2 × $1,300 = $26,600.
#guard (computeReturn (py 2018) { filing := .mfj, taxpayerAge := 66, spouseAge := 66 }).standardDeduction = 26600
-- 2023 single 70 and blind: $13,850 + 2 × $1,850 = $17,550.
#guard (computeReturn (py 2023) { taxpayerAge := 70, taxpayerBlind := true }).standardDeduction = 17550
-- Dependent with $500 of wages, 2022: greater of $1,150 and $500 + $400: $1,150.
#guard (computeReturn (py 2022) { wages := 500, canBeClaimedAsDependent := true }).standardDeduction = 1150
-- ... with $5,000 of wages: $5,400.
#guard (computeReturn (py 2022) { wages := 5000, canBeClaimedAsDependent := true }).standardDeduction = 5400
-- 2020 unemployment exclusion: $12,000 of benefits, AGI under $150,000: $10,200 excluded.
#guard (computeReturn (py 2020) { wages := 20000, unemployment := 12000 }).agi = 21800
-- 2020 $300 charity: a non-itemizer gets it above the line; an itemizer does not.
#guard (computeReturn (py 2020) { wages := 50000, charityNonItemizer := 500 }).agi = 49700
#guard (computeReturn (py 2020) { wages := 50000, charityNonItemizer := 500, itemizedDeductions := 20000 }).agi = 50000
-- itemized $12,500 vs standard $12,400 + $300 charity: the standard deduction is better.
#guard (computeReturn (py 2020) { wages := 50000, charityNonItemizer := 500, itemizedDeductions := 12500 }).deduction
  = 12400
end

end Legal.USTax.TaxCourt
