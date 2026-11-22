import TaxCode.Individual.A.AGI
import TaxCode.Individual.A.SelfEmployment
import TaxCode.Individual.B.Deductions
import TaxCode.Individual.C.AMT
import TaxCode.Individual.D.Ordering
import Lean.Data.Json

/-!
# The whole return, in Form 1040 order (tax year 2025)

Groups A–D each copied one part of the Code. This file joins them in the order the Code and the form compute:
adjusted gross income (A), deductions and taxable income (B), the tax and the alternative minimum tax (C), credits
(D), then the other taxes on Schedule 2 (self-employment tax, additional Medicare tax, net investment income tax).
Nothing here changes a provision; where a group needs a fact the shared `Household` does not carry, the default the
group documents is used and noted below.

Assumptions made only here:
* §25B contributions are split evenly between spouses on a joint return, and none were distributed.
* Social Security and Medicare taxes for §24(d)(2) are the employee's 7.65% of wages (up to the wage base) plus half the
  self-employment tax.
* §36B household income is AGI plus tax-exempt interest plus untaxed Social Security benefits (§36B(d)(2)(B)).
* No advance premium tax credit, foreign tax credit, or excluded foreign income.
-/

namespace TaxCode.Individual

open Lean

structure Line where
  agi : Int
  taxableSocialSecurity : Int
  standardDeduction : Int
  itemized : Int
  deduction : Int
  belowTheLine : Int
  qbiDeduction : Int
  taxableIncome : Int
  regularTax : Int
  amt : Int
  taxBeforeCredits : Int
  nonrefundableCredits : Int
  incomeTaxAfterCredits : Int   -- Form 1040 line 22
  seTax : Int
  additionalMedicare : Int
  niit : Int
  totalTax : Int                -- line 24
  refundableCredits : Int
  netTax : Int                  -- line 24 minus refundable credits (negative: a refund beyond withholding)
  ctc : Int
  odc : Int
  actc : Int
  eitc : Int
  cdcc : Int
  aotc : Int
  llc : Int
  saver : Int
  ptc : Int
  deriving Repr, ToJson

def ficaEmployee (h : Household) : Int :=
  bp (min (A.headWages h) 176100) 620 + bp (min h.wagesSpouse 176100) 620 + bp h.wages 145

/-- Schedule C profit counts as qualified business income, less the deductible part of self-employment tax
(Reg. §1.199A-3(b)(1)(vi)). The business is assumed not to be a specified service business; `h.qbi` carries any other QBI. -/
def withScheduleCQbi (h : Household) : Household :=
  if h.seIncome = 0 then h else { h with qbi := h.qbi + (h.seIncome - A.halfSeTax h) }

def form1040With (f : B.Facts) (h0 : Household) : Line :=
  let h := withScheduleCQbi h0
  let agi := A.agi h
  let ss := A.taxableSocialSecurity h
  let std := B.standardDeduction h f
  let itm := B.itemized h agi f
  let ded := B.deduction h agi f
  let itemizing := match f.electItemize with | some e => e | none => decide (itm > std)
  let btl := B.belowTheLine h agi f
  let tbq := B.taxableBeforeQbi h agi f
  let qbi := B.qbiDeduction h tbq (B.netCapitalGain h) f
  let ti := B.taxableIncome h agi f
  let qdcg := B.netCapitalGain h
  let regular := C.regularTax h.filing ti qdcg
  let salt := if itemizing then B.saltDeduction h (B.magi agi f) else 0
  let senior := B.seniorDeduction h (B.magi agi f) f
  let amt := C.amtForReturn h.filing ti salt (if itemizing then 0 else std) senior qdcg
  let before := regular + amt
  let se := A.seTax h
  let half := A.halfSeTax h
  let earned := h.wages + h.seIncome - half
  let saverPeople : List (Int × Int) :=
    if h.filing == .mfj then [(h.retirementContributions / 2, 0), (h.retirementContributions - h.retirementContributions / 2, 0)]
    else [(h.retirementContributions, 0)]
  let ctx : D.CreditContext :=
    { agi := agi, magiCtc := agi, magiEducation := agi, agiSaver := agi,
      householdIncome := agi + h.taxExemptInterest + (h.socialSecurity - ss),
      earnedIncome := earned, earnedHead := A.headWages h + h.seIncome - half, earnedSpouse := h.wagesSpouse,
      taxBeforeCredits := before, socialSecurityTaxes := ficaEmployee h + half, saverPeople := saverPeople }
  let cr := D.credits2025 h ctx
  let addl := A.additionalMedicare h
  let niit := A.niit h agi
  let after := before - cr.nonrefundableCredits
  let total := after + se + addl + niit
  { agi := agi, taxableSocialSecurity := ss, standardDeduction := std, itemized := itm, deduction := ded,
    belowTheLine := btl, qbiDeduction := qbi, taxableIncome := ti, regularTax := regular, amt := amt,
    taxBeforeCredits := before, nonrefundableCredits := cr.nonrefundableCredits, incomeTaxAfterCredits := after,
    seTax := se, additionalMedicare := addl, niit := niit, totalTax := total, refundableCredits := cr.refundableCredits,
    netTax := total - cr.refundableCredits, ctc := cr.ctc, odc := cr.odc, actc := cr.actc, eitc := cr.eitc,
    cdcc := cr.cdcc, aotc := cr.aotcNonref + cr.aotcRef, llc := cr.llc, saver := cr.saver, ptc := cr.ptc }

/-- The tax a return finally owes or is refunded: total tax less refundable credits (`netTax`). -/
def Line.net (l : Line) : Int := l.netTax

/-- §63(e): the taxpayer may elect to itemize even when itemized deductions are smaller than the standard deduction
(Form 1040 instructions: "you may benefit from itemizing ... if you are subject to the AMT"). The return is computed
both ways and the cheaper one kept; on a tie, the larger deduction. -/
def form1040 (h : Household) : Line :=
  let byDefault := form1040With {} h
  let other := form1040With { electItemize := some (byDefault.itemized ≤ byDefault.standardDeduction) } h
  if other.net < byDefault.net then other else byDefault

end TaxCode.Individual
