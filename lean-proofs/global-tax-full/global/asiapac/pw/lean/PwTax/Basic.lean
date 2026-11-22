import TaxKernel.World

/-!
# Palau: wage and salary tax, Palau National Code Title 40 ch 11 as amended by the Palau Tax Reform Act (RPPL No.
11-11), tax year 2025 (calendar year)

Sources (official; files in `pw/law/`):
* RPPL No. 11-11 (Passed as Senate Bill No. 11-15, SD1; palaugov.pw, `RPPL-11-11.pdf`, 107 pages with a text layer):
  Section 5 amends 40 PNC § 1101: "There shall be assessed, levied, collected, and paid a tax of six percent (6%) upon
  the first eight thousand dollars ($8,000), ten percent (10%) upon the amount over the first eight thousand dollars
  ($8,000) but not over forty thousand dollars ($40,000), and twelve percent (12%) upon the amount over the first
  forty thousand dollars ($40,000) of all wages and salaries received by every employee." and § 1104: "If it is shown
  upon application by an employee who is a citizen of the Republic that the employee earned fifteen thousand dollars
  ($15,000) or less in a tax year, then the Director shall refund ... the entire amount of tax withheld from the
  citizen employee's wages or salary pursuant to Section 1101." plus a refund of tuition and donations "not exceed[ing]
  ten percent (10%) of the income taxes paid by that employee in that tax year". Section 21(a): "this Act shall be
  effective on January 1, 2023". § 1106: social assistance payment for the informal makit sector (not modelled).
* Palau National Code Title 40 (palaugov.pw, 2018 consolidation, `Palau-National-Code-Title-40.pdf`): background.
* Later amendments: none found among the palaugov.pw uploads (Internet Archive CDX listing of
  palaugov.pw/wp-content/uploads matching "RPPL", 2018-2025) or in Global law (Palau corpus: Constitution, Titles 1
  and 17 only). Social security (41 PNC) and the Civil Service Pension Plan were not reached: not modelled.
-/

namespace PwTax
open TaxKernel

/-- 40 PNC § 1101 as amended by RPPL 11-11 s 5 (from 1 January 2023). -/
def sched : Schedule := Schedule.ofList [(0, 600), (8000, 1000), (40000, 1200)]
/-- 40 PNC § 1104: full refund for a citizen employee who "earned fifteen thousand dollars ($15,000) or less". -/
def citizenRefundLimit : Int := 15000

structure Person where
  wages : Int
  taxBeforeRefund : Int
  refund : Int
  tax : Int

/-- One employee: the tax is on "all wages and salaries received by every employee" (no allowance), withheld by the
    employer; a citizen whose earnings for the year are at most $15,000 gets it all back on application (§ 1104).
    "Earned" is read as wages and salaries (the tax base); the refund is modelled as claimed. -/
def person (citizen : Bool) (a : Adult) : Person :=
  let w := pos a.wages
  let t := sched.tax Rule.unitDown w
  let r := if citizen && decide (w ≤ citizenRefundLimit) then t else 0
  { wages := w, taxBeforeRefund := t, refund := r, tax := t - r }

def out (c : Canon) : Out :=
  let citizen := (c.bool? "citizen").getD true
  let ps := c.adults.map (person citizen)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income: Business Profits Tax (RPPL 11-11) not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["investment income: not taxed by § 1101 (wages only); other provisions of RPPL 11-11 not modelled"] else [])
  Out.make c "PW" "USD" (sumInts (ps.map (·.tax)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.wages))), Out.d "taxBeforeCitizenRefund" (sumInts (ps.map (·.taxBeforeRefund))),
      Out.d "citizenRefund" (sumInts (ps.map (·.refund))),
      Out.dStr "note" "wage and salary tax 6/10/12 % (8,000/40,000), individual; citizen refund at or below $15,000 (§ 1104) applied when citizen (default true)"])
    (unsupported := unsup ++ ["social security (41 PNC) and Civil Service Pension Plan contributions not reached: employeeSocial = 0",
      "tuition and donation refund (§ 1104, up to 10 % of tax) needs inputs not in the contract"])

def country : Country := { code := "PW", name := "Palau (40 PNC ch. 11, RPPL 11-11)", currency := "USD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- § 1101: 6 % of 8,000 = 480; + 10 % of 32,000 = 3,200 at 40,000. -/
#guard sched.tax Rule.unitDown 8000 = 480
#guard sched.tax Rule.unitDown 40000 = 3680
/- § 1104 cliff: a citizen at $15,000 pays 0 after the refund; at $15,001 pays 1,180 (480 + 10 % of 7,001). -/
#guard (person true { age := 30, wages := 15000, selfEmployment := 0, pension := 0 }).tax = 0
#guard (person true { age := 30, wages := 15001, selfEmployment := 0, pension := 0 }).tax = 1180
#guard (person false { age := 30, wages := 15000, selfEmployment := 0, pension := 0 }).tax = 1180

end PwTax
