import TaxKernel.World

/-!
# Rwanda: tax on employment income, Law n° 027/2022 of 20/10/2022 establishing taxes on income, tax period 2025

Sources (amategeko.gov.rw, the Rwanda Law Reform Commission's legal portal, official PDFs of the Official Gazette via
its API `apis.amategeko.gov.rw/v1/site/documents-files/<id>` -> `file_url`; files in `rw/law/`):
* Law n° 027/2022 (O.G. n° Special of 28/10/2022; `law027_2022.pdf`, file 4482). Art. 56 (withholding tax on
  employment income), "Table 2: From the second year after the commencement of this law": "Monthly Taxable Income in
  Rwandan francs (FRW) | From 0 To 60,000 | 0% | 60,001 100,000 | 10% | 100,001 200,000 | 20% | 200,001 More | 30%";
  "This Law comes into force on the date of its publication" (28/10/2022), so Table 2 governs 2025. Art. 15:
  employment income includes all payments; art. 16 2° excludes "contributions made by the employer for the employee to
  the public institution in charge of social security"; no article deducts the employee's own contribution.
* Law n° 051/2023 (`law051_2023.pdf`: corporate income tax rate only) and Law n° 014/2025 of 27/05/2025
  (`law014_2025.pdf`: arts. 37, 50, exemptions, digital services, winnings) do not amend art. 56.
* Presidential Order n° 086/01 of 12/12/2024 (O.G. n° Special of 13/12/2024; `po086_2024_pension.pdf`) art. 1: "The
  rate of contribution under the mandatory pension scheme is fixed at the following percentage of the remuneration
  subject to contribution: (a) from 1st January 2025: 12%"; it repeals P.O. n° 009/01 of 10/05/2016 (6 %, 3 % each).
* Law n° 05/2015 of 30/03/2015 governing the organization of pension schemes (`law05_2015.pdf`) art. 8: "The employer
  and the employee shall contribute equally to the pension scheme": employee share 6 % in 2025.
Not reached: maternity leave benefits contribution, community-based health insurance contribution (amounts set by
other laws/orders): listed unsupported.
-/

/-!
W5 pattern A (2026-11-20; amategeko.gov.rw API, gazette PDFs in `rw/law/w5/`):
* Law n° 003/2016 of 30/03/2016 establishing the maternity leave benefits scheme (O.G. n° Special of 20/04/2016)
  art. 7: "The contribution for maternity leave benefits is equal to zero point six percent (0.6%) of the salary to
  which the contribution is subscribed. The employer and the employee each contributes zero point three percent (0.3%)";
  art. 6: the contribution "is based on the gross salary". Law n° 049/2024 amends arts. 2, 5, 11-13 only (rate kept).
* Prime Minister's Order n° 105/03 of 30/09/2020 related to the CBHI scheme contributions (O.G. n° Special of
  01/10/2020) art. 5: "The contribution of an employee in a State organ and the contribution of an employee in private
  sector is zero point five percent (0.5%) of the net salary of the employee". Replaced only by P.M.O. n° 001/03 of
  16/02/2026 (in force on publication, O.G. 23/02/2026; same 0,5 %), so the 2020 Order governs 2025. "Net salary" is
  not defined in the Order: read as gross salary less PAYE and the employee's pension and maternity contributions.
Neither is deducted for PAYE (art. 56 taxes gross employment income; no deduction article). Input `"w5Contrib": false`
drops both.
-/

namespace RwTax
open TaxKernel

/-- Art. 56 Table 2, monthly. -/
def sched : Schedule := Schedule.ofList [(0, 0), (60000, 1000), (100000, 2000), (200000, 3000)]
/-- P.O. 086/01 art. 1 (12 % from 1 January 2025) shared equally (Law 05/2015 art. 8). -/
def pensionEmployee : Int := 600

def payeMonth (m : Int) : Int := sched.tax Rule.unitDown (pos m)
def pensionMonth (m : Int) : Int := divR .down (pensionEmployee * pos m) BP

/-- Law 003/2016 art. 7: employee 0.3 % of gross salary. -/
def maternityMonth (m : Int) : Int := divR .down (30 * pos m) BP
/-- P.M.O. 105/03 of 2020 art. 5: 0.5 % of net salary (gross - PAYE - pension - maternity). -/
def cbhiMonth (m : Int) : Int := divR .down (50 * pos (m - payeMonth m - pensionMonth m - maternityMonth m)) BP

#guard maternityMonth 300000 = 900 ∧ cbhiMonth 300000 = 1135   -- net 300,000 - 54,000 - 18,000 - 900 = 227,100

def out (c : Canon) : Out :=
  let w5 := (c.bool? "w5Contrib").getD true
  let tax := sumInts (c.adults.map fun a => perPeriod 12 payeMonth (pos a.wages))
  let mat := if w5 then sumInts (c.adults.map fun a => perPeriod 12 maternityMonth (pos a.wages)) else 0
  let cbhi := if w5 then sumInts (c.adults.map fun a => perPeriod 12 cbhiMonth (pos a.wages)) else 0
  let pen := sumInts (c.adults.map fun a => perPeriod 12 pensionMonth (pos a.wages))
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business profits (art. 12 annual tables) not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["investment and rental income not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions (exempt from the public institution, art. 16 3°) not modelled"] else [])
  Out.make c "RW" "RWF" tax (employeeSocial := pen + mat + cbhi)
    (detail := [Out.d "paye" tax, Out.d "pensionEmployee" pen, Out.d "maternityEmployee" mat, Out.d "cbhiEmployee" cbhi,
      Out.dStr "note" "art. 56 Table 2 monthly on gross employment income (employee pension share not deducted); pension 6 % (12 % shared equally)"])
    (unsupported := unsup ++ ["wages paid evenly over 12 months (the tax is withheld monthly, art. 56; annual declaration rules not modelled)"])

def country : Country := { code := "RW", name := "Rwanda (Law 027/2022)", currency := "RWF", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Hand-computed: 300,000 a month: 4,000 + 20,000 + 30,000 = 54,000. -/
#guard payeMonth 300000 = 54000
#guard payeMonth 60000 = 0 ∧ payeMonth 100000 = 4000 ∧ payeMonth 200000 = 24000
/- Monthly tax without annual reconciliation: 3,600,000 a year paid evenly costs 12 x 54,000 = 648,000; in one month
   1,044,000 (30 % of everything above 200,000 plus 24,000). -/
#guard 12 * payeMonth 300000 = 648000 ∧ payeMonth 3600000 = 1044000

end RwTax
