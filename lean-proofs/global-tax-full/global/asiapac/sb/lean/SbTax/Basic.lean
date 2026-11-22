import TaxKernel.World

/-!
# Solomon Islands: income tax on individuals, Income Tax Act (Cap. 123), year 2025

Sources (official: Inland Revenue Division, ird.gov.sb "Tax Legislation", `INCOME-TAX-ACT-CAP-123.pdf`: "REPRINT ...
As in force at: 5 February 2024 ... Reprint authorised by the Attorney General and published under the Legislation Act
2023"; files in `sb/law/`):
* s 28(1): "an individual is entitled to a personal exemption for a year of $30,080.00" (endnotes: s 28 last amended
  by Act No. 4 of 2019, commenced 1 January 2020); (1A) "Subsection (1) applies only to payments made under tax
  deduction provisions other than section 38" (s 38: non-resident withholding).
* s 32: "tax on the chargeable income ... of an individual for any year shall be charged at the rates specified in
  the Fifth Schedule after the application of the personal exemption amount provided for in section 28: Provided that
  where the tax owing to or by any individual for any year, after subtracting all tax paid by him by deduction or
  otherwise, is less than five dollars the amount of tax shall be increased or decreased ... for the purpose of
  cancelling such tax."
* Fifth Schedule (s 32; endnote "amd by Act No. 14 of 1999"): "RATES OF INDIVIDUAL INCOME TAX | Income Bracket | Rate
  | $1 to $15,000.00 | $0.11 | $15,001.00 to $30,000.00 | $0.23 | $30,001.00 to $60,000.00 | $0.35 | $60,001.00 and
  over | $0.40".
Reading: the bracket rates apply to the part of the income in each bracket (graduated, default); the alternative that
the whole income bears the rate of its bracket (slab) is the input `sbReading: "slab"` (statute-visible ambiguity:
the Schedule does not say "on the next" or "on the excess").
Solomon Islands National Provident Fund Act (Cap. 109): PacLII refuses scripts with a challenge (not bypassed); the
Internet Archive copy of PacLII's consolidated text (capture 2022-06-26, `paclii_sinpfa421.pdf`, a scan of the 1996
Revised Edition, OCR checked against the page image) gives s 13(1) (monthly contribution "at the appropriate rates set
out in the Second Schedule"; "(a) no contribution shall be payable in any one month for an employee who in the
preceding month (i) earned less than $20.00") and the Second Schedule: the employer pays "twelve and one half cents in
respect of each complete dollar in the amount of the wages of the employee for the preceding month" and may recover
from the employee "five cents in respect of each complete dollar in the amount of such wages". The SINPF (Amendment)
Act 2018 (No. 10 of 2018, archived PacLII copy) does not touch the Second Schedule; later amendments were not found
in PacLII's numbered acts (Internet Archive listing). Source tier: archived PacLII copy (official secondary).
-/

namespace SbTax
open TaxKernel

/-- s 28(1). -/
def personalExemption : Int := 30080
/-- Fifth Schedule, graduated reading. -/
def sched : Schedule := Schedule.ofList [(0, 1100), (15000, 2300), (30000, 3500), (60000, 4000)]
/-- Fifth Schedule, slab reading: the bracket's rate on the whole amount. -/
def slabRate (x : Int) : Int :=
  if x ≤ 15000 then 1100 else if x ≤ 30000 then 2300 else if x ≤ 60000 then 3500 else 4000
def slabTax (x : Int) : Int := divR .down (slabRate x * pos x) BP
/-- SINPF Act Second Schedule: employee 5 cents per complete dollar of the month's wages; none under $20 a month. -/
def npfCentsPerDollar : Int := 5
def npfMinMonth : Int := 20
def npfMonthCents (mCents : Int) : Int :=
  if mCents < npfMinMonth * 100 then 0 else npfCentsPerDollar * (mCents / 100)
def npfYear (w : Int) : Int := if w ≤ 0 then 0 else divR .down (perPeriod 12 npfMonthCents (w * 100)) 100

structure Person where
  chargeable : Int
  tax : Int

/-- Chargeable income of an individual (employment, business and property income; dividends are taxed with a
    credit under s 36, not modelled), less the personal exemption, at the Fifth Schedule rates. -/
def person (slab : Bool) (a : Adult) (rent : Int) : Person :=
  let ci := pos (pos a.wages + a.selfEmployment + rent)
  let x := pos (ci - personalExemption)
  { chargeable := ci, tax := if slab then slabTax x else sched.tax Rule.unitDown x }

def persons (slab : Bool) (c : Canon) : List Person :=
  match c.adults with
  | [a] => [person slab a c.rentalIncome]
  | a :: b :: _ => [person slab a (half1 c.rentalIncome), person slab b (half2 c.rentalIncome)]
  | [] => []

def out (c : Canon) : Out :=
  let slab := (c.str? "sbReading").getD "graduated" == "slab"
  let ps := persons slab c
  let npf := (c.int? "sbNpfEmployee").getD (sumInts (c.adults.map (fun a => npfYear (pos a.wages))))
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 then ["interest and dividends: withholding and the s 36 dividend credit not modelled; ignored"] else []) ++
    (if c.capitalGains ≠ 0 then ["capital gains not modelled"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income taxed in chargeable income; deductions not modelled"] else [])
  Out.make c "SB" "SBD" (sumInts (ps.map (·.tax)))
    (employeeSocial := npf)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (fun p => pos (p.chargeable - personalExemption)))),
      Out.d "chargeableIncome" (sumInts (ps.map (·.chargeable))),
      Out.dStr "reading" (if slab then "slab" else "graduated"),
      Out.dStr "note" "individual assessment; personal exemption 30,080 (s 28); Fifth Schedule 11/23/35/40 % on brackets of the income above the exemption (s 32)"])
    (unsupported := unsup ++ ["National Provident Fund: 5 cents per complete dollar of monthly wages (Cap. 109 Second Schedule, archived PacLII copy); override with sbNpfEmployee (annual SBD)",
      "the s 32 proviso (a balance under $5 is cancelled) is not applied"])

def country : Country := { code := "SB", name := "Solomon Islands (Income Tax Act Cap. 123)", currency := "SBD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Graduated: 11 % of 15,000 = 1,650; 23 % of 15,000 = 3,450; 35 % of 30,000 = 10,500. -/
#guard sched.tax Rule.unitDown 15000 = 1650
#guard sched.tax Rule.unitDown 30000 = 5100
#guard sched.tax Rule.unitDown 60000 = 15600
/- The slab reading jumps at each bracket edge: $1 above 15,000 adds 23 % of 15,000 - 11 % of 15,000 = 1,800. -/
#guard slabTax 15000 = 1650 ∧ slabTax 15001 = 3450
#guard slabTax 60001 - slabTax 60000 = 3000
/- NPF: $1,000.50 a month gives 5 x 1,000 cents = $50.00; $19.99 a month gives nothing. -/
#guard npfMonthCents 100050 = 5000 ∧ npfMonthCents 1999 = 0
#guard npfYear 12000 = 600

end SbTax
