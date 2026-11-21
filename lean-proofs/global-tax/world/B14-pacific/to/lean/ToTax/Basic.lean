import TaxKernel.World

/-!
# Tonga: income tax on individuals, Income Tax Act (Cap. 11.05, Act 10 of 2007), fiscal year 2025/26 (1 July 2025 -
30 June 2026)

Sources (official; files in `to/law/`):
* Income Tax Act, 2020 Revised Edition (Attorney General's Office, ago.gov.to, `IncomeTaxAct_3.pdf`): s 2 "fiscal year"
  means "(b) in any other case, the period of 12 months ending on 30th June"; s 5(1) "The Minister shall, with the
  approval of Cabinet by Order impose ... income tax for each fiscal year on a person who has chargeable income";
  s 5(2) tax = rates under the Order applied to chargeable income less credits; s 13 employment income; s 21 exempt
  dividends; s 35 (deduction for an employer's retirement-fund contribution only). The AGO point-in-time list of
  acts in force on 2025-07-01 (POST `pointintime=2025-07-01`, `b14to_I.html`) shows the 2020 Revised Edition and one
  later amendment, the Income Tax (Amendment) Act 2020 (Act 12 of 2020, in force 11 August 2021: administrative
  sections and s 20A only; read, `IncomeTaxAmendmentAct2020.pdf`).
* Income Tax (Amendment) Order 2017 (Revenue and Customs, revenue.gov.to "new legislations" page, fetched from the
  laptop: the site does not answer lean1; `IncomeTaxAmendmentOrder2017_English.pdf`, sha256 988387ec...): "This Order
  shall come into effect on 1 July 2017"; replaces paragraph 2 of the Principal Order (Order in Council No. 5 of 21
  January 2008): "$0-$10,000 0% | $10,001-$30,000 10% | $30,001-$60,000 20% | $60,001 and over 25%". It is the latest
  income tax Order the Ministry lists; the AGO revised edition does not carry Orders. Access grade B for this reason.
* National Retirement Benefits Fund Act (Cap. 8.08, 2020 Revised Edition, `NationalRetirementBenefitsFundAct_3.pdf`),
  Second Schedule: "Contribution rates payable by employers and employees shall not be less than the following
  percentages of each complete pa'anga of insurable earnings: ... After the first five years of this Act | 7.5 per
  cent | 5 per cent" (Act commenced 1 July 2011). Public servants are in the Retirement Fund Act 1998 instead (not
  modelled).
-/

namespace ToTax
open TaxKernel

/-- Income Tax (Amendment) Order 2017 para 2 (in force 1 July 2017; the latest Order on record). -/
def sched : Schedule := Schedule.ofList [(0, 0), (10000, 1000), (30000, 2000), (60000, 2500)]
/-- NRBF Act Second Schedule, employees: 5 per cent of each complete pa'anga of insurable earnings. -/
def nrbfRate : Int := 500

structure Person where
  chargeable : Int
  tax : Int
  nrbf : Int

/-- Individual assessment (s 5): chargeable income = employment + business + property income (ss 10-14); employee
    NRBF contributions are not deductible (s 35 allows only the employer's). Dividends are exempt (s 21). -/
def person (publicSector : Bool) (a : Adult) (rent : Int) : Person :=
  let ci := pos (pos a.wages + a.selfEmployment + rent)
  { chargeable := ci, tax := sched.tax Rule.unitDown ci,
    nrbf := if publicSector then 0 else divR .down (nrbfRate * pos a.wages) BP }

def persons (c : Canon) : List Person :=
  let pub := (c.str? "toSector").getD "private" == "public"
  match c.adults with
  | [a] => [person pub a c.rentalIncome]
  | a :: b :: _ => [person pub a (half1 c.rentalIncome), person pub b (half2 c.rentalIncome)]
  | [] => []

def out (c : Canon) : Out :=
  let ps := persons c
  let pub := (c.str? "toSector").getD "private" == "public"
  let unsup :=
    (if c.interest ≠ 0 then ["interest: the Act's 10 per cent withholding from interest (Part on withholding; section not read in full) not modelled; interest ignored"] else []) ++
    (if c.capitalGains ≠ 0 then ["capital gains not modelled"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income taxed in chargeable income; small business tax (s 8, Third Schedule) not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions from approved funds are exempt (s 19(2)); pension input ignored"] else []) ++
    (if pub then ["public servant: Retirement Fund Act 1998 contributions not modelled (employee contribution set to 0)"] else [])
  Out.make c "TO" "TOP" (sumInts (ps.map (·.tax)))
    (employeeSocial := sumInts (ps.map (·.nrbf)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.chargeable))), Out.d "nrbfEmployee" (sumInts (ps.map (·.nrbf))),
      Out.dStr "note" "individual assessment; Income Tax (Amendment) Order 2017 rates 0/10/20/25 % (10,000/30,000/60,000); NRBF 5 % not deductible; fiscal year 2025/26"])
    (unsupported := unsup ++ ["rates Order: the 2017 Order is the latest the Ministry of Revenue and Customs lists; later Orders, if any, not reached (access B)"])

def country : Country := { code := "TO", name := "Tonga (Income Tax Act Cap. 11.05)", currency := "TOP", year := "2025/26", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Order 2017 bands: 10 % of 20,000 = 2,000 at 30,000; + 20 % of 30,000 = 8,000 at 60,000. -/
#guard sched.tax Rule.unitDown 10000 = 0
#guard sched.tax Rule.unitDown 30000 = 2000
#guard sched.tax Rule.unitDown 60000 = 8000
#guard sched.tax Rule.unitDown 100000 = 18000
#guard (person false { age := 30, wages := 20000, selfEmployment := 0, pension := 0 } 0).nrbf = 1000

end ToTax
