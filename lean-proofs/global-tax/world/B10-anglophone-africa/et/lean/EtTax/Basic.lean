import TaxKernel.World

/-!
# Ethiopia: employment income tax (Schedule "A"), Federal Income Tax Proclamation No. 979/2016 as amended by the Income
Tax (Amendment) Proclamation No. 1395/2025, Ethiopian fiscal year 2018 E.C. (8 July 2025 - 7 July 2026)

Year: the federal tax year runs from 8 July (Proclamation 1395/2025 art. 4: "all other provisions of this amendment
shall be applicable on income derived as of July 8, 2025"); the year beginning in 2025 is modelled (CONTRACTWORLD).
Federal law: the model is federal employment income tax (Addis Ababa / federal employers); the regions' own
proclamations are not modelled.

Sources:
* Proclamation No. 1395/2025, Federal Negarit Gazette No. 64, "1st september, 2025" (Ministry of Revenue,
  mor.gov.et/website-api/domestic-proclamations, item 31, fetched from the laptop; `et/law/mor_proc_1395.pdf`, English
  text layer): art. 1(6) "Article 11 of the Proclamation is hereby deleted and replaced by the following new Article
  11: 11. Employment Income Tax Rates. The monthly rate of employment income tax is: Monthly Income from Employment (in
  Birr) | 0 -2,000 0% | 2,001-4,000 15% | 4,001-7,000 20% | 7,001-10,000 25% | 10,001 -14,000 30% | Over 14,000 35%".
* Proclamation No. 979/2016 (Global law `ethiopia/national/acts/income-tax`, as enacted): art. 12(2) "Employment
  income shall not include exempt income"; art. 65(1)(c) exempts employer contributions to a retirement fund up to 15 %
  of monthly employment income; no article deducts the employee's own pension contribution. The replaced art. 11 (0-600
  0 % ... over 10,900 35 %) applied to income derived before 8 July 2025.
* Private Organization Employees' Pension Proclamation No. 1268/2022 (Global law
  `ethiopia/national/acts/private-employees-pension/art-010.md`) art. 10: contributions "based on the salary of the
  employee ... 1/ by the employer, 11%; 2/ by the employee, 7%."
Reading: art. 11 prints brackets and rates without saying "on the portion"; the model applies each rate to the part of
monthly income within its bracket (graduated). Brackets in whole birr (0-2,000; 2,001-4,000; ...).
-/

namespace EtTax
open TaxKernel

/-- Proclamation 1395/2025 art. 1(6) (new art. 11), monthly. -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (2000, 1500), (4000, 2000), (7000, 2500), (10000, 3000), (14000, 3500)]
/-- The replaced art. 11 of Proclamation 979/2016 (income derived before 8 July 2025; kept for comparison). -/
def sched979 : Schedule :=
  Schedule.ofList [(0, 0), (600, 1000), (1650, 1500), (3200, 2000), (5250, 2500), (7800, 3000), (10900, 3500)]
/-- Proclamation 1268/2022 art. 10(2). -/
def pensionEmployee : Int := 700

def taxMonth (m : Int) : Int := sched.tax Rule.unitDown (pos m)
def pensionMonth (m : Int) : Int := divR .down (pensionEmployee * pos m) BP

def out (c : Canon) : Out :=
  let tax := sumInts (c.adults.map fun a => perPeriod 12 taxMonth (pos a.wages))
  let pen := sumInts (c.adults.map fun a => perPeriod 12 pensionMonth (pos a.wages))
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income (Schedule C) not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["Schedule B (rental) and D (other income) not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled"] else [])
  Out.make c "ET" "ETB" tax (employeeSocial := pen)
    (detail := [Out.d "employmentIncomeTax" tax, Out.d "pensionEmployee" pen,
      Out.dStr "year" "Ethiopian fiscal year 2018 E.C. (8 July 2025 - 7 July 2026)",
      Out.dStr "note" "monthly art. 11 (Proclamation 1395/2025) on gross salary; private-sector pension 7 % (Proclamation 1268/2022), not deductible"])
    (unsupported := unsup ++ ["public servants' pension scheme not modelled (private-sector default)", "regional employment income tax not modelled (federal)",
      "wages paid evenly over 12 months (the tax is monthly and final)"])

def country : Country := { code := "ET", name := "Ethiopia (Federal Income Tax Proclamation 979/2016 as amended)", currency := "ETB", year := "2025/26 (EFY 2018)", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed: 20,000 birr a month: 300 + 600 + 750 + 1,200 + 2,100 = 4,950. -/
#guard taxMonth 20000 = 4950
#guard taxMonth 2000 = 0 ∧ taxMonth 4000 = 300 ∧ taxMonth 14000 = 2850
/- The 2025 reform: 10,000 birr a month cost 2,045 under the old table and 1,650 under the new one. -/
#guard sched979.tax Rule.unitDown 10000 = 2045 ∧ taxMonth 10000 = 1650

end EtTax
