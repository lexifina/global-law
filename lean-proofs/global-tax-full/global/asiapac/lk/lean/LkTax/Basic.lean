import TaxKernel.World

/-!
# Sri Lanka: income tax of a resident individual, year of assessment 2025/26 (1 April 2025 - 31 March 2026)

Access tier A (tax), EPF rate official secondary. Statute: Inland Revenue Act, No. 24 of 2017, read with its amending
Acts in Global law (`sri-lanka/national/acts/act/...`, Parliament of Sri Lanka; each act's official PDF is on
parliament.lk): No. 10 of 2021 s. 55, No. 45 of 2022 ss. 19, 33, 36, No. 4 of 2023 s. 18, No. 2 of 2025 ss. 3, 5
("shall come into operation on April 1, 2025"), and No. 11 of 2026 (parliament.lk 6420.pdf, sha256 25c44cdd...: it
amends the Fifth Schedule from 1 April 2025 only for institutions, para 1(a)(i); the reliefs used here are unchanged).
Global law prints the 2017 text of the schedules unamended; the amendments are separate acts and are applied here by
hand (CONTRACTWORLD: "as enacted" corpora need the amendment chain).

Employees' Provident Fund: the Act (No. 15 of 1958) is not in Global law; the copy on epf.lk (`epf_act_1958.pdf`,
Cap. 623 edition) still prints "six per centum"; the EPF Department's current pages ("Employee's Contribution: A minimum
of 8% of the total monthly earnings", epf.lk/?p=171 and ?page_id=811, saved with sha256) are used as official secondary.
-/

namespace LkTax
open TaxKernel

/-- First Schedule para 1 (1D), inserted by Act No. 2 of 2025 s. 3 (1)(b), "for a year of assessment commencing from
April 1, 2025": "Not exceeding Rs. 1,000,000 6% ...; Exceeding Rs. 1,000,000 but not exceeding Rs. 1,500,000 Rs. 60,000
plus 18% ...; ... Rs. 2,000,000 Rs. 150,000 plus 24% ...; ... Rs. 2,500,000 Rs. 270,000 plus 30% ...; Exceeding
Rs. 2,500,000 Rs. 420,000 plus 36% of the amount in excess of Rs. 2,500,000". -/
def sched : Schedule :=
  Schedule.ofList [(0, 600), (1000000, 1800), (1500000, 2400), (2000000, 3000), (2500000, 3600)]

/- The printed fixed amounts (60,000 / 150,000 / 270,000 / 420,000) are the band sums. -/
def cum (x : Int) : Int := sched.ticks x / BP
#guard cum 1000000 = 60000 ∧ cum 1500000 = 150000 ∧ cum 2000000 = 270000 ∧ cum 2500000 = 420000

/-- Fifth Schedule para 2 (a)(v), added by Act No. 2 of 2025 s. 5 (3): personal relief "Rs. 1,800,000, for each year of
assessment commencing on or after April 1, 2025"; para 2(a) as substituted by Act 45 of 2022 s. 36: "the relief shall
not be deducted against gains from the realisation of investment assets". -/
def personalRelief : Int := 1800000

/-- Fifth Schedule para 2 (c) (2017, not amended): "an amount equal to 25 percent of the total rental income". -/
def rentRelief (rent : Int) : Int := rent / 4

/-- Fifth Schedule para 1 (a)(ii)(iia): donation to an approved charitable institution, "one-third of the taxable
income of the individual or Rupees seventy five thousand, whichever is less" (read: of the income before the
donation). -/
def donationCap (base : Int) : Int := min (base / 3) 75000

/-- First Schedule para 1 (2)(a): "gains from the realisation of investment assets shall be taxed at the rate of 10%". -/
def gainsRate : Int := 1000

/-- s. 88 (1A)(aa) (Act 45 of 2022 s. 19): "on or after January 1, 2023, dividends paid by a resident company" are final
withholding payments; rate First Schedule para 10 (1)(d)(v) (Act 45 of 2022 s. 33 (6)): "dividend paid-15%". -/
def dividendRate : Int := 1500

/-- EPF: employee 8 % of total earnings (official secondary, see header); no ceiling. -/
def epfRate : Int := 800

def roundR : Rule := { mode := .halfUp }

structure PersonOut where
  ti : Int
  tax : Int
  gainsTax : Int
  divTax : Int
  epf : Int

def person (wages se pension rent interest div gains donation : Int) : PersonOut :=
  let assess := wages + se + pension + rent + interest
  let reliefs := min (pos assess) (personalRelief + rentRelief rent)
  let base := pos (assess - reliefs)
  let qp := min donation (donationCap base)
  let ti := pos (base - qp)
  let tax := sched.tax roundR ti
  { ti, tax, gainsTax := divR .halfUp (gainsRate * pos gains) BP, divTax := divR .halfUp (dividendRate * pos div) BP,
    epf := divR .halfUp (epfRate * pos wages) BP }

def compute (c : Canon) : Out :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let rs := (c.adults.zip (List.range n)).map fun (a, i) =>
    person a.wages a.selfEmployment a.pension (share c.rentalIncome i) (share c.interest i) (share c.dividends i)
      (share c.capitalGains i) (if i = 0 then c.charitable else 0)
  let s (f : PersonOut → Int) := sumInts (rs.map f)
  Out.make c "LK" "LKR" (s (·.tax))
    (surtaxes := [("gainsInvestmentAssets10", s (·.gainsTax)), ("dividendFinalWHT15", s (·.divTax))])
    (employeeSocial := s (·.epf))
    (detail := [Out.d "taxableIncome" (s (·.ti)), Out.dStr "epf" "8 % employee (EPF Department, official secondary)"])
    (unsupported := ["terminal benefits (First Schedule para 1(2)(b)), foreign-currency service income at 15 % (para 1(6)) and betting/liquor/tobacco business income at 45 % not modelled",
      "interest: WHT 10 % (para 10 (1)(d)(ii)(b)) is an advance tax credited against the annual tax; included at normal rates"])

def country : Country :=
  { code := "LK", name := "Sri Lanka (year of assessment 2025/26)", currency := "LKR", year := "2025/26", compute := compute }

theorem sched_progressive : sched.progressive = true := by decide

end LkTax
