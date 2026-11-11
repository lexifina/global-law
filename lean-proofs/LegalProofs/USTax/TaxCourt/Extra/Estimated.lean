import LegalProofs.USTax.TaxCourt.Basic

/-!
# §6654: the addition to tax for underpayment of estimated tax by an individual (tax years 2012–2024)

The rule, as it read every year 2012–2024 (calendar-year individuals; farmers and fishermen, §6654(i), and the
annualized income installment method, §6654(d)(2), are not modelled except through `requiredOverride`):

* **Required annual payment**, §6654(d)(1)(B): the lesser of 90% of the tax for the year and 100% of the tax shown on
  the preceding year's return — 110% if the preceding year's AGI exceeded $150,000 ($75,000 married filing
  separately), §6654(d)(1)(C) — the second option only if a return was filed for a preceding year of 12 months.
* **Installments**, §6654(c)–(d)(1)(A): four, each 25% of the required annual payment, due 15 April, 15 June,
  15 September and 15 January (§7503 moves a weekend or holiday to the next business day; the 2020 April and June
  installments were postponed to 15 July 2020 by Notice 2020-18 and Notice 2020-23).
* **Withholding**, §6654(g)(1): treated as paid in four equal parts on the due dates (unless the taxpayer shows
  otherwise — pass actual dates as `payments` and zero `withholding` for that).
* **Underpayment and period**, §6654(b)–(c): each installment's shortfall runs from its due date to the date paid, or
  15 April of the following year if earlier; payments are credited to the earliest unpaid installment, §6654(b)(3).
* **Rate**, §6654(a): the §6621(a)(2) underpayment rate for each quarter, by day, on a 365- or 366-day year (§6622
  daily compounding does not apply to §6654: §6622(b)).
* **Exceptions**: §6654(e)(1) — no addition if the tax shown on the return (or the tax, if none) less withholding is
  under $1,000; §6654(e)(2) — no addition if the preceding year was a 12-month year, the taxpayer a citizen or resident
  throughout, and there was no liability for it.

Amounts are whole dollars; the addition is computed exactly and rounded once to the dollar.
-/

namespace Legal.USTax.TaxCourt.Extra
open Legal.USTax.TaxCourt

/-! ## Rates and due dates -/

/-- The §6621(a)(2) underpayment rate (percent) for individuals by calendar quarter, from the IRS quarterly
interest-rate announcements (IR news releases; Rev. Ruls. under §6621), 2012 Q1 through 2025 Q2 — enough to compute
any 2012–2024 addition, which runs to 15 April of the following year. `(year, quarter, percent)`. -/
def underpaymentRateTable : List (Int × Int × Int) :=
  -- Sources: Form 2210 instructions for year Y (irs.gov/pub/irs-prior/i2210--Y.pdf), Penalty Worksheet rate
  -- periods 1–4, give Q2–Q4 of Y and Q1 of Y+1. 2012 Q1: i2210--2011 rate period 4 (.03). 2025 Q2: IR-2025-29
  -- (6 Mar 2025), "7% for underpayments".
  -- 2012–2015: 3% every quarter (i2210--2011 … i2210--2015: .03 in every rate period)
  ([2012, 2013, 2014, 2015].flatMap fun y => [(y, 1, 3), (y, 2, 3), (y, 3, 3), (y, 4, 3)]) ++
  [(2016, 1, 3), (2016, 2, 4), (2016, 3, 4), (2016, 4, 4),   -- Q1: i2210--2015 RP4 .03; Q2–Q4: i2210--2016 0.04
   (2017, 1, 4), (2017, 2, 4), (2017, 3, 4), (2017, 4, 4),   -- Q1: i2210--2016 RP4 0.04; Q2–Q4: i2210--2017 0.04
   (2018, 1, 4), (2018, 2, 5), (2018, 3, 5), (2018, 4, 5),   -- Q1: i2210--2017 RP4 0.04; Q2–Q4: i2210--2018 0.05
   (2019, 1, 6), (2019, 2, 6), (2019, 3, 5), (2019, 4, 5),   -- Q1: i2210--2018 RP4 0.06; Q2–Q4: i2210--2019 0.06/0.05/0.05
   (2020, 1, 5), (2020, 2, 5), (2020, 3, 3), (2020, 4, 3),   -- Q1: i2210--2019 RP4 0.05; Q2–Q4: i2210--2020 0.05/0.03/0.03
   (2021, 1, 3), (2021, 2, 3), (2021, 3, 3), (2021, 4, 3),   -- Q1: i2210--2020 RP4 0.03; Q2–Q4: i2210--2021 0.03
   (2022, 1, 3), (2022, 2, 4), (2022, 3, 5), (2022, 4, 6),   -- Q1: i2210--2021 RP4 0.03; Q2–Q4: i2210--2022 0.04/0.05/0.06
   (2023, 1, 7), (2023, 2, 7), (2023, 3, 7), (2023, 4, 8),   -- Q1: i2210--2022 RP4 0.07; Q2–Q4: i2210--2023 0.07/0.07/0.08
   (2024, 1, 8), (2024, 2, 8), (2024, 3, 8), (2024, 4, 8),   -- Q1: i2210--2023 RP4 0.08; Q2–Q4: i2210--2024 0.08
   (2025, 1, 7), (2025, 2, 7)]                               -- Q1: i2210--2024 RP4 0.07; Q2: IR-2025-29 7%

/-- A rate period: from `start` (inclusive) to the next period's start, at `pct` percent. -/
structure RatePeriod where
  start : Date
  pct : Int
  deriving Repr, Inhabited, DecidableEq

/-- The quarterly table as rate periods, closed by a final zero-rate period starting after the last quarter. -/
def ratePeriods (tbl : List (Int × Int × Int) := underpaymentRateTable) : List RatePeriod :=
  let ps := tbl.map fun (y, q, r) => (⟨⟨y, 3 * q - 2, 1⟩, r⟩ : RatePeriod)
  match tbl.getLast? with
  | some (y, q, _) => ps ++ [⟨if q = 4 then ⟨y + 1, 1, 1⟩ else ⟨y, 3 * q + 1, 1⟩, 0⟩]
  | none => ps

/-- Due dates of the four installments for tax year `y` (2012–2024): the dates printed in that year's Form 1040-ES
(irs.gov/pub/irs-prior/f1040es--Y.pdf, "Record of Estimated Tax Payments"), i.e. 15 April / 15 June / 15 September /
15 January moved by §7503 for weekends, holidays and the D.C. Emancipation Day holiday in April; for 2020 the April
and June installments are both 15 July 2020 (Notice 2020-18; Notice 2020-23, as applied in the 2020 Form 2210
instructions, "Postponed due dates" and Table 2). Note: the Form 2210 Penalty Worksheet (other than 2020) counts days
from the nominal 15th (columns headed 4/15, 6/15, 9/15, 1/15), not the shifted date; pass `dueDates` to follow it.
Outside 2012–2024: the statutory 15 April, 15 June, 15 September, 15 January. -/
def installmentDueDates (y : Int) : List Date :=
  match y with
  | 2012 => [⟨2012, 4, 17⟩, ⟨2012, 6, 15⟩, ⟨2012, 9, 17⟩, ⟨2013, 1, 15⟩]  -- f1040es--2012
  | 2013 => [⟨2013, 4, 15⟩, ⟨2013, 6, 17⟩, ⟨2013, 9, 16⟩, ⟨2014, 1, 15⟩]  -- f1040es--2013
  | 2014 => [⟨2014, 4, 15⟩, ⟨2014, 6, 16⟩, ⟨2014, 9, 15⟩, ⟨2015, 1, 15⟩]  -- f1040es--2014
  | 2015 => [⟨2015, 4, 15⟩, ⟨2015, 6, 15⟩, ⟨2015, 9, 15⟩, ⟨2016, 1, 15⟩]  -- f1040es--2015
  | 2016 => [⟨2016, 4, 18⟩, ⟨2016, 6, 15⟩, ⟨2016, 9, 15⟩, ⟨2017, 1, 17⟩]  -- f1040es--2016
  | 2017 => [⟨2017, 4, 18⟩, ⟨2017, 6, 15⟩, ⟨2017, 9, 15⟩, ⟨2018, 1, 16⟩]  -- f1040es--2017
  | 2018 => [⟨2018, 4, 17⟩, ⟨2018, 6, 15⟩, ⟨2018, 9, 17⟩, ⟨2019, 1, 15⟩]  -- f1040es--2018
  | 2019 => [⟨2019, 4, 15⟩, ⟨2019, 6, 17⟩, ⟨2019, 9, 16⟩, ⟨2020, 1, 15⟩]  -- f1040es--2019
  | 2020 => [⟨2020, 7, 15⟩, ⟨2020, 7, 15⟩, ⟨2020, 9, 15⟩, ⟨2021, 1, 15⟩]  -- f1040es--2020 (Sep, Jan); i2210--2020 (Jul)
  | 2021 => [⟨2021, 4, 15⟩, ⟨2021, 6, 15⟩, ⟨2021, 9, 15⟩, ⟨2022, 1, 18⟩]  -- f1040es--2021
  | 2022 => [⟨2022, 4, 18⟩, ⟨2022, 6, 15⟩, ⟨2022, 9, 15⟩, ⟨2023, 1, 17⟩]  -- f1040es--2022
  | 2023 => [⟨2023, 4, 18⟩, ⟨2023, 6, 15⟩, ⟨2023, 9, 15⟩, ⟨2024, 1, 16⟩]  -- f1040es--2023
  | 2024 => [⟨2024, 4, 15⟩, ⟨2024, 6, 17⟩, ⟨2024, 9, 16⟩, ⟨2025, 1, 15⟩]  -- f1040es--2024
  | _ => [⟨y, 4, 15⟩, ⟨y, 6, 15⟩, ⟨y, 9, 15⟩, ⟨y + 1, 1, 15⟩]

/-- `365 × 366`: a common denominator for daily rates in common and leap years. -/
def yearL : Int := 365 * 366

/-- `amount × pct% × days / days-in-year`, summed over the rate periods overlapping `[a, b)`, scaled by `100 × yearL`
(exact; no rounding). -/
def chargeScaled (rates : List RatePeriod) (amount : Int) (a b : Date) : Int :=
  let rec go : List RatePeriod → Int
    | p :: q :: rest =>
      let lo := max a.days p.start.days
      let hi := min b.days q.start.days
      let d := max 0 (hi - lo)
      amount * p.pct * d * (yearL / daysInYear p.start.y) + go (q :: rest)
    | _ => 0
  go rates

/-! ## The computation -/

/-- Findings for §6654. Amounts in whole dollars. -/
structure EstFacts where
  year : Int
  /-- The §6654(f) tax for the year: income tax and self-employment tax (and from 2013 the §1411 and Additional
  Medicare taxes), less credits other than withholding. For (e)(1), the tax shown on the return, or the tax if no
  return was filed. -/
  currentTax : Int
  /-- Income tax withheld (§6654(g)), treated as paid evenly on the due dates. -/
  withholding : Int := 0
  /-- Tax shown on the preceding year's return; `none` if no return was filed or the year was shorter than 12 months. -/
  priorTax : Option Int := none
  /-- AGI shown on the preceding year's return (for §6654(d)(1)(C)). -/
  priorAGI : Int := 0
  /-- Married filing separately in the current year (the §6654(d)(1)(C)(ii) $75,000 threshold). -/
  mfs : Bool := false
  /-- §6654(e)(2): preceding year of 12 months, citizen or resident throughout, and no liability for it. -/
  priorNoLiability : Bool := false
  /-- Estimated tax payments (and other payments credited as made on a date), `(date, amount)`. -/
  payments : List (Date × Int) := []
  /-- The court's due dates if not the printed ones. -/
  dueDates : Option (List Date) := none
  /-- Required installments found otherwise (e.g. the annualized income method, §6654(d)(2)). -/
  requiredOverride : Option (List Int) := none
  deriving Repr, Inhabited

structure EstOutcome where
  /-- §6654(d)(1)(B) required annual payment, whole dollars. -/
  requiredAnnual : Int
  /-- Whether §6654(e)(1) or (e)(2) excepts the taxpayer. -/
  excepted : Bool
  /-- The addition to tax, whole dollars. -/
  addition : Int
  deriving Repr, Inhabited, DecidableEq

/-- §6654(d)(1)(C): the prior-year percentage (100 or 110). -/
def priorYearPct (priorAGI : Int) (mfs : Bool) : Int :=
  if priorAGI > (if mfs then 75000 else 150000) then 110 else 100

/-- §6654(d)(1)(B): the required annual payment (each option rounded to the dollar, as Form 2210 lines 5–9). -/
def requiredAnnualPayment (currentTax : Int) (priorTax : Option Int) (priorAGI : Int) (mfs : Bool) : Int :=
  let ninety := pos (roundDollar (currentTax * 9) 10)
  match priorTax with
  | none => ninety
  | some p => min ninety (pos (roundDollar (p * priorYearPct priorAGI mfs) 100))

/-- One event: a payment (`kind = 0`) or an installment falling due (`kind = 1`), amounts in quarter-dollars. -/
structure EstEvent where
  date : Date
  kind : Nat
  amount : Int
  deriving Repr, Inhabited

/-- Credit a payment on `p` to the outstanding shortfalls in order (§6654(b)(3)); returns the shortfalls still
outstanding, the unapplied excess and the charge accrued (scaled). Charges stop at `stop`. -/
def applyPayment (rates : List RatePeriod) (stop p : Date) :
    List (Date × Int) → Int → Int → List (Date × Int) × Int × Int
  | [], a, acc => ([], a, acc)
  | (d, u) :: rest, a, acc =>
    let upto := if p.days ≤ stop.days then p else stop
    if a ≥ u then applyPayment rates stop p rest (a - u) (acc + chargeScaled rates u d upto)
    else ((d, u - a) :: rest, 0, acc + chargeScaled rates a d upto)

/-- Run the events in date order (payments before installments on the same day). State: outstanding shortfalls,
unapplied credit, accrued charge. -/
def runEvents (rates : List RatePeriod) (stop : Date) :
    List EstEvent → List (Date × Int) → Int → Int → List (Date × Int) × Int
  | [], out, _, acc => (out, acc)
  | e :: es, out, credit, acc =>
    if e.kind = 0 then
      let (out', left, acc') := applyPayment rates stop e.date out e.amount acc
      runEvents rates stop es out' (credit + left) acc'
    else
      let used := min credit e.amount
      let short := e.amount - used
      runEvents rates stop es (if short > 0 then out ++ [(e.date, short)] else out) (credit - used) acc

/-- **§6654.** The addition to tax for the year, given the findings and the rate periods (default: the IRS table). -/
def estimatedTaxAddition (x : EstFacts) (rates : List RatePeriod := ratePeriods) : EstOutcome :=
  let rap := requiredAnnualPayment x.currentTax x.priorTax x.priorAGI x.mfs
  let deMinimis := x.currentTax - x.withholding < 1000
  if deMinimis || x.priorNoLiability then ⟨rap, true, 0⟩ else
  let dues := x.dueDates.getD (installmentDueDates x.year)
  -- amounts in quarter-dollars: each installment is exactly 25% of the required annual payment
  let req : List Int := match x.requiredOverride with
    | some r => r.map (4 * ·)
    | none => dues.map fun _ => rap
  let insts : List EstEvent := (dues.zip req).map fun (d, r) => ⟨d, 1, r⟩
  let wh : List EstEvent := dues.map fun d => ⟨d, 0, x.withholding⟩
  let pays : List EstEvent := x.payments.map fun (d, a) => ⟨d, 0, 4 * a⟩
  let evs := (pays ++ wh ++ insts).mergeSort fun a b =>
    a.date.days < b.date.days || (a.date.days == b.date.days && a.kind ≤ b.kind)
  let stop : Date := ⟨x.year + 1, 4, 15⟩
  let (out, acc) := runEvents rates stop evs [] 0 0
  let tail := out.foldl (fun s (d, u) => s + chargeScaled rates u d stop) 0
  ⟨rap, false, roundDollar (acc + tail) (4 * 100 * yearL)⟩

/-! ## Tests -/

-- The table covers 2012 Q1 – 2025 Q2 (54 quarters) and closes on 1 July 2025.
#guard underpaymentRateTable.length = 54
#guard (ratePeriods.getLast?.map (·.start)) = some ⟨2025, 7, 1⟩
-- §6654(d)(1)(C): over $150,000 prior AGI: 110%; $75,000 if married filing separately.
#guard priorYearPct 150000 false = 100 ∧ priorYearPct 150001 false = 110 ∧ priorYearPct 80000 true = 110
#guard requiredAnnualPayment 10000 (some 8000) 100000 false = 8000
#guard requiredAnnualPayment 20000 (some 15000) 200000 false = 16500
#guard requiredAnnualPayment 10000 none 0 false = 9000

-- 2019: tax $10,000, prior-year tax $8,000, nothing paid. Each $2,000 installment (due 15 Apr, 17 Jun, 16 Sep 2019,
-- 15 Jan 2020) runs to 15 Apr 2020 at 6% (2019 Q2), 5% (2019 Q3 – 2020 Q2), by day on 365/366-day years: $270.98.
-- (Checked against an independent day-by-day computation.)
private def est19 : EstFacts := { year := 2019, currentTax := 10000, priorTax := some 8000, priorAGI := 100000 }
#guard (estimatedTaxAddition est19).addition = 271
-- 2023: tax $20,000, withholding $12,000, prior tax $15,000 on AGI $200,000: required 16,500 (110%), installments
-- $4,125 against $3,000 withholding each; a $4,500 payment on 10 Jan 2024 clears the $1,125 shortfalls of Q1–Q3
-- (from 18 Apr, 15 Jun, 15 Sep 2023 at 7%, then 8% from 1 Oct) and covers Q4 in advance: $137.26.
private def est23 : EstFacts :=
  { year := 2023, currentTax := 20000, withholding := 12000, priorTax := some 15000, priorAGI := 200000,
    payments := [(⟨2024, 1, 10⟩, 4500)] }
#guard (estimatedTaxAddition est23).addition = 137
-- §6654(e)(1): tax less withholding under $1,000.
private def est22a : EstFacts := { year := 2022, currentTax := 5000, withholding := 4100 }
#guard estimatedTaxAddition est22a = ⟨4500, true, 0⟩
-- §6654(e)(2): no liability for the preceding 12-month year.
private def est22b : EstFacts := { year := 2022, currentTax := 50000, priorNoLiability := true }
#guard (estimatedTaxAddition est22b).addition = 0
-- Paying every installment in full on time: none.
private def est24 : EstFacts :=
  { year := 2024, currentTax := 40000, priorTax := some 40000, priorAGI := 100000,
    payments := (installmentDueDates 2024).map (·, 9000) }
#guard (estimatedTaxAddition est24).addition = 0
-- 2020: the April and June installments both fell due 15 July 2020.
#guard (installmentDueDates 2020).take 2 = [⟨2020, 7, 15⟩, ⟨2020, 7, 15⟩]

end Legal.USTax.TaxCourt.Extra
