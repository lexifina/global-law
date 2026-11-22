import TaxKernel.World

/-!
# Uganda: income tax of a resident individual, Income Tax Act (Revised Edition text in force 2024-12-23),
year of income 1 July 2024 - 30 June 2025

Year: the Act's "year of income" is "the period of twelve months ending on 30th June" (s. 2). The year beginning in
2025 (2025/26) would follow any Income Tax (Amendment) Act 2025; none was reachable (ULII lists none for 2025 in its
legislation index, the Parliament's "Acts" pages stop at 2024), so the model is the year 2024/25 (CONTRACTWORLD: the
statute's latest accessible text is the earlier year).

Sources (files in `ug/law/`):
* Income Tax Act as in the Revised Edition, version 2024-12-23 (ULII, Internet Archive capture 2025-10-20 of
  ulii.org/en/akn/ug/act/1997/11/eng@2024-12-23; ULII answers scripts 403, not bypassed): s. 6(1) "The chargeable income
  of an individual for a year of income is charged to income tax at the rates prescribed in Part I of Schedule 4";
  Schedule 4 Part I para. 1: "Not exceeding Ushs. 2,820,000 | Nil | Exceeding Ushs. 2,820,000 but not exceeding Ushs.
  4,020,000 | 10% of the amount by which chargeable income exceeds Ushs. 2,820,000. | ... not exceeding Ushs. 4,920,000
  | Ushs. 120,000 plus 20% ... | Exceeding Ushs. 4,920,000 | (a) Ushs. 300,000 plus 30% of the amount by which
  chargeable income exceeds shs. 4,920,000; and (b) where the chargeable income of an individual exceeds Ushs.
  120,000,000 an additional 10% charged on the amount by which chargeable income exceeds Ushs. 120,000,000."
* Income Tax (Amendment) Act 2024 (Parliament of Uganda, cmis.parliament.go.ug, `ita_amend_2024.pdf`): amends the
  First and Third Schedules (withholding on payment-service-provider commissions) only; the individual rates are
  unchanged for 2024/25.
* National Social Security Fund Act (ULII version 2022-01-07, `nssf_2022-01-07.html`)
  s. 12(1): "the employee's share of a standard contribution of 5 percent calculated on the total wages paid during
  that month"; s. 11(1): standard contribution "of 15 percent". No ceiling. The ITA has no deduction for it (no
  provision on NSSF contributions was found in the Act's text).
* Local service tax: Local Governments Act s. 83(2)(b) (Global law `uganda/national/acts/local-governments/sec-083.md`)
  levies it "on all persons in gainful employment"; its rates are not in the consolidated Act (Schedule not in the
  record): not modelled.
-/

namespace UgTax
open TaxKernel

/-- Schedule 4 Part I para. 1 (resident individuals), annual, with the 10 % addition above 120,000,000 as a band. -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (2820000, 1000), (4020000, 2000), (4920000, 3000), (120000000, 4000)]
def nssfRate : Int := 500

def pct (bp x : Int) : Int := divR .down (bp * x) BP

def person (a : Adult) : Int × Int × Int :=
  let w := pos a.wages
  let nssf := perPeriod 12 (fun m => pct nssfRate (pos m)) w
  let ci := w
  (sched.tax Rule.unitDown ci, ci, nssf)

def out (c : Canon) : Out :=
  let ps := c.adults.map person
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 then ["interest and dividends (final withholding tax) not modelled"] else []) ++
    (if c.rentalIncome ≠ 0 then ["rental income: separate rental tax (Schedule 4 Part II) not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["capital gains not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled"] else [])
  Out.make c "UG" "UGX" (sumInts (ps.map (·.1))) (employeeSocial := sumInts (ps.map (·.2.2)))
    (detail := [Out.d "chargeableIncome" (sumInts (ps.map (·.2.1))),
      Out.dStr "year" "year of income 2024/25 (1 July 2024 - 30 June 2025)",
      Out.dStr "note" "individual taxation; Schedule 4 Part I rates on employment income; NSSF 5 % not deductible"])
    (unsupported := unsup ++ ["local service tax (Local Governments Act s. 83): rates not in the consolidated Act",
      "Income Tax (Amendment) Act 2025 (if any) not reached: year 2024/25 modelled"])

def country : Country := { code := "UG", name := "Uganda (Income Tax Act)", currency := "UGX", year := "2024/25", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- The printed fixed amounts of Schedule 4 Part I: 120,000 at 4,020,000 and 300,000 at 4,920,000. -/
#guard sched.tax Rule.unitDown 4020000 = 120000
#guard sched.tax Rule.unitDown 4920000 = 300000
/- Above 120,000,000 the marginal rate is 40 % (30 % + the additional 10 %). -/
#guard sched.rate 120000000 = 4000 ∧ sched.rate 119999999 = 3000

end UgTax
