import TaxKernel.World

/-!
# Dominica: income tax of a resident individual and the employee's Social Security contribution, 2025

Sources (dominica.gov.dm "Laws of Dominica" search, the Inland Revenue Division's links; files in `dm/law/`):
* Income Tax Act Chap. 67:01 (Revised Laws 1990, scanned PDF of 2008, OCR checked): s. 47 "A resident individual shall
  be entitled to an allowance of twelve thousand dollars irrespective of the nature of his income"; s. 61 and the Fifth
  Schedule (rates).
* Amending Acts (text layers): Act 15 of 2007 (Fifth Schedule 18/28/38 %, from 1 January 2008); Act 9 of 2008 s. 3
  (s. 47 "eighteen" -> "twenty") and s. 4: Fifth Schedule para. 1 "(a) for every dollar of the first 20,000 ... 16% (b)
  for every dollar of the next 30,000 ... 26% (c) for every dollar over 50,000 ... 36%" from 1 January 2009; Act 7 of
  2014 s. 4 (s. 47 "twenty" -> "twenty-five", from 1 January 2015); Act 6 of 2018 s. 11 (s. 47 "twenty-five" ->
  "thirty"; s. 1(4): "Section 11 is deemed to have come into force on the 1st day of January, 2018"); Acts 13/2015,
  3/2020 (rental rate, Fifth Schedule para. 3), 13/2021 (residential rent exempt), 18/2023 (returns): no change to
  para. 1 or s. 47. These are all the "Income Tax (Amendment)" instruments the search lists after 2006.
* Social Security (Collection of Contributions) (Amendments) Regulations 2008 (S.R.O. 8 of 2008, in force 1 March
  2008): insurable earnings "$1,386" weekly / "$6,000" (monthly); Schedule: "Employees ... 4%". The 2018 (S.R.O. 12)
  and 2019 (S.R.O. 22) amending Regulations are listed on dominica.gov.dm but their links answer 404 (lean1 and
  laptop): the 2025 rate and ceiling may differ (official secondary not found: dss.dm gives ages "between the ages of
  16 and the Pensionable Age of 65", no rates).
-/

namespace DmTax
open TaxKernel

/-- Fifth Schedule para. 1 (Act 9 of 2008). -/
def sched : Schedule := Schedule.ofList [(0, 1600), (20000, 2600), (50000, 3600)]

def allowance : Int := 30000

/-- Social Security employee's share: 4 % of monthly insurable earnings up to 6,000 (S.R.O. 8 of 2008). -/
def ssMonth (m : Int) : Int := divR .down (400 * min (pos m) 6000) 10000

structure Person where
  ss : Int
  chargeable : Int
  tax : Int

def person (a : Adult) : Person :=
  let w := pos a.wages
  let ss := if a.age ≥ 16 && a.age < 65 then perPeriod 12 ssMonth w else 0
  let assessable := w + pos a.selfEmployment + pos a.pension
  let chargeable := pos (assessable - allowance)
  { ss := ss, chargeable := chargeable, tax := sched.tax Rule.unitDown chargeable }

def out (c : Canon) : Out :=
  let ps := c.adults.map person
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then
      ["interest, dividends, rents (residential rent exempt, s. 27A) and gains not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pension exemptions (s. 25(1)(jj),(kk), SRO 4/2009) not modelled"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employed Social Security not modelled"] else [])
  Out.make c "DM" "XCD" (sumInts (ps.map (·.tax))) (employeeSocial := sumInts (ps.map (·.ss)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.chargeable))), Out.d "socialSecurity" (sumInts (ps.map (·.ss))),
      Out.dStr "note" "individual taxation; s. 47 allowance 30,000 (Act 6/2018); 16/26/36 % at 20,000/50,000 (Act 9/2008); Social Security 4 % to 6,000/month (SRO 8/2008; later SROs unreachable)"])
    (unsupported := unsup ++ ["Social Security rate and ceiling as of S.R.O. 8 of 2008: S.R.O.s 12/2018 and 22/2019 not reachable (404)",
      "mortgage and other deductions (ss. 48-48C) need inputs"])

def country : Country := { code := "DM", name := "Dominica (Income Tax Act Chap. 67:01)", currency := "XCD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard sched.tax Rule.unitDown 20000 = 3200
#guard sched.tax Rule.unitDown 50000 = 11000
#guard ssMonth 6000 = 240

end DmTax
