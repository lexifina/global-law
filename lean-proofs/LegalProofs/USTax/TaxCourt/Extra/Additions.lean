import LegalProofs.USTax.TaxCourt.Extra.Estimated

/-!
# Did the addition apply? Liability predicates for §6651(a)(1)–(3) and §6654

Many Tax Court holdings say only that an addition applies (or not), leaving the amount to the Rule 155 computation.
These predicates let such a holding be checked from the findings without amounts.

* **§6651(a)(1)** failure to file: a return not filed by its due date (with extensions), unless due to reasonable
  cause and not willful neglect; nothing to add if no net amount was required to be shown (§6651(b)(1)).
* **§6651(a)(2)** failure to pay the tax shown on a return by the date prescribed for payment (without extension);
  a §6020(b) substitute for return counts as the return shown (§6651(g)(2)); reasonable cause excepts.
* **§6651(a)(3)** failure to pay tax not shown on a return within 21 calendar days of notice and demand (10 business
  days if the amount is $100,000 or more); reasonable cause excepts.
* **§6651(c)(1)**: for any month to which both (a)(1) and (a)(2) apply, (a)(1) is reduced by (a)(2).
* **§6654**: an underpayment of a required installment, no (e)(1)/(e)(2) exception, no (e)(3) waiver.
* **§7491(c)**: in a deficiency case against an individual the Commissioner bears the burden of production for an
  addition; if it is not met, the addition does not apply (`productionMet`).
-/

namespace Legal.USTax.TaxCourt.Extra
open Legal.USTax.TaxCourt

/-- Findings for §6651. Amounts in whole dollars. -/
structure AdditionFacts where
  /-- Date the return was due, with any extension (for (a)(1)). -/
  fileDue : Date
  /-- Date prescribed for payment, without extension (for (a)(2)). -/
  payDue : Date
  /-- Date the return was filed; `none`: not filed by `asOf`. -/
  filed : Option Date := none
  /-- The Commissioner prepared a §6020(b) substitute for return (§6651(g)). -/
  substituteReturn : Bool := false
  /-- Date the tax shown was paid in full; `none`: unpaid at `asOf`. -/
  paid : Option Date := none
  /-- The date the question is asked at (trial or decision). -/
  asOf : Date
  /-- Tax required to be shown, and tax shown (on the return or the substitute). -/
  requiredTax : Int
  shownTax : Int
  /-- Withholding, estimated tax and credits paid by the payment due date (§6651(b)). -/
  timelyPayments : Int := 0
  reasonableCauseFiling : Bool := false
  reasonableCausePayment : Bool := false
  /-- (a)(3): date of notice and demand for tax not shown, the amount demanded, and the date paid. -/
  noticeDate : Option Date := none
  noticeAmount : Int := 0
  noticePaid : Option Date := none
  reasonableCauseNotice : Bool := false
  /-- §7491(c): the Commissioner met the burden of production. -/
  productionMet : Bool := true
  deriving Repr, Inhabited

/-- Day of the week, 0 = Monday (1 January 2024 was a Monday). -/
def weekday (d : Date) : Int := (d.days - (⟨2024, 1, 1⟩ : Date).days) % 7

/-- The date `n` business days (Monday–Friday; federal holidays not modelled) after `d`. -/
def addBusinessDays (d : Date) (n : Nat) : Int :=
  let rec go (day : Int) : Nat → Nat → Int
    | 0, _ => day
    | _, 0 => day
    | k + 1, fuel + 1 =>
      let nd := day + 1
      let wd := (nd - (⟨2024, 1, 1⟩ : Date).days) % 7
      if wd < 5 then go nd k fuel else go nd (k + 1) fuel
  go d.days n (3 * n + 7)

/-- **§6651(a)(1)** applies. -/
def failureToFileApplies (a : AdditionFacts) : Bool :=
  a.productionMet && !a.reasonableCauseFiling && decide (a.requiredTax - a.timelyPayments > 0) &&
    decide ((a.filed.getD a.asOf).days > a.fileDue.days)

/-- **§6651(a)(2)** applies. -/
def failureToPayApplies (a : AdditionFacts) : Bool :=
  a.productionMet && !a.reasonableCausePayment && (a.filed.isSome || a.substituteReturn) &&
    decide (a.shownTax - a.timelyPayments > 0) && decide ((a.paid.getD a.asOf).days > a.payDue.days)

/-- **§6651(a)(3)** applies: the deadline is 21 calendar days after notice and demand, or 10 business days if the
amount demanded is $100,000 or more. -/
def failureToPayNoticeApplies (a : AdditionFacts) : Bool :=
  match a.noticeDate with
  | none => false
  | some n =>
    let deadline := if a.noticeAmount ≥ 100000 then addBusinessDays n 10 else n.days + 21
    a.productionMet && !a.reasonableCauseNotice && decide (a.noticeAmount > 0) &&
      decide ((a.noticePaid.getD a.asOf).days > deadline)

/-- **§6651(c)(1)**: the (a)(1) addition is reduced by (a)(2) — both apply for an overlapping month. -/
def c1OffsetApplies (a : AdditionFacts) : Bool :=
  failureToFileApplies a && failureToPayApplies a

/-- **§6654** applies: a positive addition on the findings, unless waived under §6654(e)(3) — (A) casualty, disaster
or other unusual circumstances making it inequitable, or (B) retired after 62 or disabled in the year (or the year
before) with reasonable cause — or the burden of production was not met. -/
def estimatedTaxApplies (x : EstFacts) (waived : Bool := false) (productionMet : Bool := true)
    (rates : List RatePeriod := ratePeriods) : Bool :=
  productionMet && !waived && decide ((estimatedTaxAddition x rates).addition > 0)

/-! ## Tests -/

#guard weekday ⟨2024, 1, 1⟩ = 0 ∧ weekday ⟨2023, 4, 18⟩ = 1 ∧ weekday ⟨2024, 6, 15⟩ = 5
-- 10 business days from Friday 1 Mar 2024: Friday 15 Mar 2024.
#guard addBusinessDays ⟨2024, 3, 1⟩ 10 = (⟨2024, 3, 15⟩ : Date).days

private def late : AdditionFacts :=
  { fileDue := ⟨2019, 4, 15⟩, payDue := ⟨2019, 4, 15⟩, filed := some ⟨2019, 8, 20⟩, paid := some ⟨2019, 8, 20⟩,
    asOf := ⟨2021, 1, 1⟩, requiredTax := 10000, shownTax := 10000 }
-- Filed and paid late: both apply, and the (c)(1) offset with them.
#guard failureToFileApplies late ∧ failureToPayApplies late ∧ c1OffsetApplies late
-- Reasonable cause for filing late only: (a)(2) still applies.
#guard !failureToFileApplies { late with reasonableCauseFiling := true } ∧
  failureToPayApplies { late with reasonableCauseFiling := true }
-- Withholding covered the tax: no net amount, neither applies.
#guard !failureToFileApplies { late with timelyPayments := 12000 } ∧
  !failureToPayApplies { late with timelyPayments := 12000 }
-- Never filed, no substitute: (a)(1) applies, (a)(2) does not (no tax shown on any return).
#guard failureToFileApplies { late with filed := none, paid := none } ∧
  !failureToPayApplies { late with filed := none, paid := none }
-- ... with a §6020(b) substitute: (a)(2) applies too (§6651(g)(2)).
#guard failureToPayApplies { late with filed := none, paid := none, substituteReturn := true }
-- Extension to 15 Oct, filed 1 Oct, paid 1 Oct: (a)(1) no, (a)(2) yes.
#guard !failureToFileApplies { late with fileDue := ⟨2019, 10, 15⟩, filed := some ⟨2019, 10, 1⟩ } ∧
  failureToPayApplies { late with fileDue := ⟨2019, 10, 15⟩, filed := some ⟨2019, 10, 1⟩, paid := some ⟨2019, 10, 1⟩ }
-- No burden of production: nothing applies.
#guard !failureToFileApplies { late with productionMet := false }
-- (a)(3): notice 1 Mar 2024 for $5,000; paid 22 Mar (21 days): timely; 23 Mar: late.
private def notice (amt : Int) (paidOn : Date) : AdditionFacts :=
  { late with noticeDate := some ⟨2024, 3, 1⟩, noticeAmount := amt, noticePaid := some paidOn }
#guard !failureToPayNoticeApplies (notice 5000 ⟨2024, 3, 22⟩)
#guard failureToPayNoticeApplies (notice 5000 ⟨2024, 3, 23⟩)
-- $100,000 or more: 10 business days: paid 15 Mar 2024 is timely, 18 Mar 2024 late.
#guard !failureToPayNoticeApplies (notice 150000 ⟨2024, 3, 15⟩)
#guard failureToPayNoticeApplies (notice 150000 ⟨2024, 3, 18⟩)
-- §6654: the 2019 example in `Estimated` ($271) applies unless waived.
private def est : EstFacts := { year := 2019, currentTax := 10000, priorTax := some 8000, priorAGI := 100000 }
#guard estimatedTaxApplies est ∧ !estimatedTaxApplies est (waived := true)
#guard !estimatedTaxApplies { est with priorNoLiability := true }

end Legal.USTax.TaxCourt.Extra
