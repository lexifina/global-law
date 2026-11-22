import TaxKernel.World

/-!
# Guyana: income tax of a resident individual and the employee's NIS contribution, year of income 2025

Sources (files in `gy/law/`; Global law holds no tax law for Guyana):
* Income Tax Act Cap. 81:01, Laws of Guyana L.R.O. 1/2012 (Ministry of Legal Affairs, mola.gov.gy volume 14 PDF,
  `ITA_cap81-01_mola.pdf`), as amended by the Acts on parliament.gov.gy (scanned gazette copies, OCR checked by eye):
  - Income Tax (Amendment) Act 2025 (No. 2 of 2025, Official Gazette 6 February 2025) s. 1: "deemed to have come into
    operation with respect to and from the year of income commencing on 1st January, 2025"; s. 3 replaces s. 20: "(1)
    ... there shall be allowed the deductions of - (a) one million five hundred and sixty thousand dollars or one third
    of an individual's total income from all sources excluding income subject to withholding taxes under section 39(1)
    (per annum) whichever is greater; (b) one hundred and twenty thousand dollars per annum in respect of any child ...
    under the age of eighteen ... (c) six hundred thousand dollars of income earned from a second job ... (d) six
    hundred thousand dollars of income earned for overtime work"; s. 20(2): where more than one person is entitled to
    (b) "the persons shall elect for one of them". s. 4: s. 36 "twenty eight percent" -> "twenty five percent",
    "two million four hundred thousand dollars" -> "three million one hundred and twenty thousand dollars"; s. 5: s. 36A
    the same threshold and "forty percent" -> "thirty five percent".
  - Income Tax (Amendment) Act 2017 (No. 12 of 2017) s. 7: s. 36 reads "twenty-eight percent of the chargeable income
    for every person less than one million four hundred and forty thousand dollars per annum"; s. 8 inserts s. 36A: "The
    chargeable income of every person, other than a company, in excess of one million, four hundred and forty thousand
    dollars shall be taxed at the rate of forty percent" (thresholds raised by Acts 8/2019, 5/2022, 3/2023, 2/2024).
  - Income Tax (Amendment) Act 2015 (No. 8 of 2015) s. 2: s. 16(1)(k) deduction of "National Insurance contributions by
    employees"; Fiscal Enactments (Amendment) Act 2022 s. 16(1)(l) insurance premiums (not modelled: no input).
  - s. 34(1): "The income of a married woman living with her husband shall be charged as of an individual in her name".
* National Insurance and Social Security Act Cap. 36:01 (mola.gov.gy, L.R.O. 1/2012), Collection of Contributions
  Regulations reg. 17(1): the contribution is "a percentage determined by actuarial calculations and approved by the
  Board" (not printed in the law). Rates from the National Insurance Scheme's own page (official secondary,
  nis.org.gy/information_on_contributions, read 2026-11-20 from a second machine; the build server gets HTTP 406): "a 5.6% deduction from
  the Employee's pay", "ceiling of $280,000.00 per month", effective January 2020; compulsory "between the ages of
  sixteen (16) and sixty- (60) years".
-/

namespace GyTax
open TaxKernel

/-- s. 36 (25 % up to 3,120,000 of chargeable income) and s. 36A (35 % on the excess), graduated reading. -/
def sched : Schedule := Schedule.ofList [(0, 2500), (3120000, 3500)]

/-- s. 20(1)(a): the greater of 1,560,000 and one third of total income. -/
def basicDeduction (total : Int) : Int := max 1560000 (total / 3)

/-- NIS (official secondary): 5.6 % of monthly pay up to 280,000 a month. -/
def nisMonth (m : Int) : Int := divR .down (560 * min (pos m) 280000) 10000

structure Person where
  nis : Int
  total : Int
  chargeable : Int
  tax : Int

def person (a : Adult) (kids : Int) (secondJob overtime : Int) : Person :=
  let w := pos a.wages
  let nis := if a.age ≥ 16 && a.age < 60 then perPeriod 12 nisMonth w else 0
  let total := w + pos a.selfEmployment
  let ded := basicDeduction total + 120000 * kids + min 600000 (pos secondJob) + min 600000 (pos overtime) + nis
  let chargeable := pos (total - ded)
  { nis := nis, total := total, chargeable := chargeable, tax := sched.tax Rule.unitDown chargeable }

def out (c : Canon) : Out :=
  let kids : Int := c.childrenUnder 18
  let to2 := c.int? "gyChildTo" == some 2 && c.isCouple
  let sj := (c.int? "secondJobIncome").getD 0
  let ot := (c.int? "overtimeIncome").getD 0
  let ps := (List.range c.adults.length).zip c.adults |>.map (fun (i, a) =>
    person a (if (i == 0 && !to2) || (i == 1 && to2) then kids else 0) (if i == 0 then sj else 0) (if i == 0 then ot else 0))
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then
      ["interest and dividends (withholding s. 39), rents and gains (Capital Gains Tax Act) not modelled"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employed: NIS 12.5 % and presumptive/minimum tax (ss. 28A, 37A) not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled"] else [])
  Out.make c "GY" "GYD" (sumInts (ps.map (·.tax))) (employeeSocial := sumInts (ps.map (·.nis)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.chargeable))), Out.d "nis" (sumInts (ps.map (·.nis))),
      Out.dStr "note" "individual taxation (s. 34); s. 20 as replaced by Act 2/2025 (max(1,560,000, total/3), 120,000 per child under 18 to one parent); NIS deductible (s. 16(1)(k)); 25 % to 3,120,000, 35 % above (ss. 36, 36A)"])
    (unsupported := unsup ++ ["NIS rate and ceiling are Board figures (official secondary, nis.org.gy), not statute",
      "life and medical insurance premiums (s. 16(1)(l)) not modelled", "wages assumed paid evenly over 12 months (NIS ceiling is monthly)"])

def country : Country := { code := "GY", name := "Guyana (Income Tax Act Cap. 81:01 as amended 2025)", currency := "GYD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- s. 36: 780,000 at the 3,120,000 threshold; one third of income overtakes 1,560,000 at 4,680,000. -/
#guard sched.tax Rule.unitDown 3120000 = 780000
#guard sched.tax Rule.unitDown 4120000 = 1130000
#guard basicDeduction 4680000 = 1560000
#guard basicDeduction 6000000 = 2000000
#guard nisMonth 280000 = 15680
#guard nisMonth 500000 = 15680

end GyTax
