import TaxKernel.World

/-!
# Nigeria: personal income tax under the Personal Income Tax Act (Cap. P8), year of assessment 2025 (Lagos State PAYE)

The Nigeria Tax Act 2025 (Global law `nigeria/national/acts/tax`) applies from 1 January 2026 and is not used for 2025.
Statutes read (the Lagos State Internal Revenue Service's "Tax Legislations" page, lirs.gov.ng; scanned gazettes read
by OCR and checked against the page image; files in `ng/law/`):
* Personal Income Tax (Amendment) Act 2011 No. 20 (PITA-Ammendment.pdf, sha256 f8c30828…), s. 34, new Sixth Schedule:
  "(1) A consolidated relief allowance … ₦200,000 plus 20 per cent of gross income. (2) Tax Exempt: … (d) National
  Pension Scheme …"; "Graduated Tax rates … subject to a minimum tax of 1 per cent of Gross Income whichever is higher.
  1. First ₦300,000 @ 7 per cent 2. Next ₦300,000 @ 11 3. Next ₦500,000 @ 15 4. Next ₦500,000 @ 19 5. Next
  ₦1,600,000 @ 21 6. Above ₦3,200,000 @ 24 per cent" (page 13 image checked); s. 5: s. 33 (1) "consolidation relief
  allowance of ₦200,000.00 subject to a minimum of 1 percent of gross income whichever is higher plus 20 per cent of
  the gross income".
* Finance Act 2020 (FINANCEACT.pdf, sha256 9b9148fc…) s. 29: s. 33 (2) "gross income" = "income from all sources less
  all non-taxable income, income on which no further tax is payable, tax-exempt items listed in paragraph (2) of the
  Sixth Schedule"; s. 30: s. 37 proviso, minimum tax "shall not apply to a person … where such person earns the
  National Minimum Wage or less from an employment".
* Pension Reform Act 2014 (pencom.gov.ng PRA_2014.pdf, sha256 66c91953…, OCR) s. 4 (1) (b) "a minimum of eight per cent
  by the employee" of "monthly emoluments".
Unit: individual. The model applies the employee pension contribution to total wages (the Act's "emoluments" are basic,
housing and transport pay, which the contract does not separate; flagged).
-/

namespace NgTax
open TaxKernel

/-- Sixth Schedule tax table (PITA (Amendment) Act 2011 s. 34). -/
def sched : Schedule :=
  Schedule.ofList [(0, 700), (300000, 1100), (600000, 1500), (1100000, 1900), (1600000, 2100), (3200000, 2400)]
def craFixed : Int := 200000
def craPct : Int := 2000
def craMinPct : Int := 100
def minTaxPct : Int := 100
def pension : Contribution := { name := "pension (PRA 2014 s. 4)", sched := Schedule.flat 800 }

def pct (bp x : Int) : Int := divR .down (bp * x) BP

/-- Finance Act 2020 s. 33 (Third Schedule para. 33): "The income of a person from an employment where such person
earns gross income of National Minimum Wage or less from such employment" is exempt; s. 30 (s. 37 proviso): the minimum
tax "under this section or as provided for under the Sixth Schedule ... shall not apply to a person in any year of
assessment where such person earns the National Minimum Wage or less from an employment" (s. 108: the extant National
Minimum Wage under the National Minimum Wage Act). The amount is not in the statutes read: optional input
`ngMinWageMonthly` (naira a month; the year's employment income is compared with 12 times it). -/
def earnsMinWageOrLess (nmw : Option Int) (a : Adult) : Bool :=
  match nmw with
  | some w => a.wages > 0 && a.wages ≤ 12 * w
  | none => false

/-- (tax, taxable income, gross income, pension) of one person. -/
def person (nmw : Option Int) (a : Adult) (rental : Int) : Int × Int × Int × Int :=
  let pen := pension.amount a.wages
  let exempt := earnsMinWageOrLess nmw a
  let empIncome := if exempt then 0 else a.wages - pen
  let gi := pos (empIncome + a.selfEmployment + rental)
  let cra := max craFixed (pct craMinPct gi) + pct craPct gi
  let ti := pos (gi - cra)
  let t := sched.tax Rule.unitDown ti
  (if exempt then t else max t (pct minTaxPct gi), ti, gi, pen)

def out (c : Canon) : Out :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let nmw := c.int? "ngMinWageMonthly"
  let rs := (c.adults.zip (List.range n)).map fun (a, i) => person nmw a (share c.rentalIncome i)
  Out.make c "NG" "NGN" (sumInts (rs.map (·.1))) (employeeSocial := sumInts (rs.map (·.2.2.2)))
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.2.1))), Out.d "grossIncome" (sumInts (rs.map (·.2.2.1))),
      Out.dStr "region" "Lagos State (PITA is uniform; administered by the State of residence)"])
    (unsupported := (if nmw.isNone && c.adults.any (·.wages > 0) then ["Third Schedule para. 33 and s. 37 proviso (FA 2020: employment income of a person earning the National Minimum Wage or less is exempt, and the minimum tax does not apply) need ngMinWageMonthly; not applied"] else []) ++ [
      "National Housing Fund (2.5 %) and NHIS contributions not modelled (Acts not read)",
      "interest and dividends: final withholding tax (no further tax), rates not read; excluded",
      "pensions and capital gains (Capital Gains Tax Act) not modelled",
      "pension contribution applied to total wages (PRA 'monthly emoluments' = basic + housing + transport)",
      "minimum tax (Sixth Schedule: 1 per cent of 'Gross Income') read on the s. 33 (2) gross income (net of the tax-exempt pension contribution), as the consolidated relief allowance in the same sentence"])

def country : Country := { code := "NG", name := "Nigeria (PITA, Lagos)", currency := "NGN", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- The table's cumulative tax at the top of each band: -/
#guard sched.ticks 3200000 = (21000 + 33000 + 75000 + 95000 + 336000) * BP

/- FA 2020 (Third Schedule para. 33, s. 37 proviso): with a National Minimum Wage of 70,000 a month (an input, not read
from statute here), 840,000 of wages is exempt and pays nothing; 840,001 is taxed under the Sixth Schedule
(CRA on gross income net of the 8 % pension: 34,006), a notch. Without the input the minimum tax applies (1 %). -/
def adultW (w : Int) : Adult := { age := 40, wages := w, selfEmployment := 0, pension := 0 }
#guard (person (some 70000) (adultW 840000) 0).1 = 0
#guard (person (some 70000) (adultW 840001) 0).1 = 34006
#guard (person none (adultW 100000) 0).1 = 920

end NgTax
