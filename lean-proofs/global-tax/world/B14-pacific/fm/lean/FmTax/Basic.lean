import TaxKernel.World

/-!
# Federated States of Micronesia: national wage and salary tax (54 F.S.M.C. ch. 1) and FSM Social Security
(53 F.S.M.C.), calendar year 2025

Sources (files in `fm/law/`): the Code of the Federated States of Micronesia Annotated 2014 edition, as published by
the FSM Legal Information System (fsmlaw.org, the publisher Global law uses for the FSM; `T54_Ch01_SubChpII_2014.html`,
`T53_Ch06_2014.html`, `T53_Ch09_2014.html`):
* 54 F.S.M.C. 121: "There shall be assessed, levied, collected, and paid a tax of six percent upon the first $11,000
  and ten percent upon the amount over the first $11,000 of all wages and salaries received by every employee, as
  defined, except as provided in section 122 of this chapter."
* 54 F.S.M.C. 122(1): "Every employee, as defined, except those whose gross annual wages and salaries are $5,000 or
  more, shall be allowed a deduction of $1,000 per year from all wages and salaries subject to tax levied by section
  121"; (2) claimed by refund under § 123.
* 54 F.S.M.C. 141 (gross revenue tax on a "business", which excludes employees): "$80 per year upon that portion of
  ... gross revenues ... which does not exceed $10,000", "three percent ... in excess of $10,000"; "(3) Businesses
  which earn gross revenues of not more than $2,000 per year are exempt".
* 53 F.S.M.C. 901(1)(g): employee tax "with respect to wages paid on and after January 1, 2013, the rate shall be seven
  point five (7.5) percent"; 53 F.S.M.C. 603(15)(a): wages exclude "that part of remuneration ... in excess of $9,000
  beginning on January 1, 2023, and in excess of $10,000 beginning on January 1, 2028, paid in a quarterly reporting
  period by one employer".
* Later amendments: Global law's record of FSM public laws (323 laws to 2026-11-03) holds no law amending §§ 121, 122,
  141, 603 or 901 (searches "121 of title 54", "122 of title 54", "chapter 1 of title 54", "section 603/901 of title
  53"); PL 21-145 (2020) adds § 161 (unemployment assistance, 10 %), not wages.
-/

namespace FmTax
open TaxKernel

/-- 54 F.S.M.C. 121. -/
def sched : Schedule := Schedule.ofList [(0, 600), (11000, 1000)]
/-- 54 F.S.M.C. 122: $1,000 deduction for employees with gross annual wages under $5,000. -/
def lowWageDeduction : Int := 1000
def lowWageLimit : Int := 5000
/-- 53 F.S.M.C. 901(1)(g) and 603(15)(a) (quarterly ceiling per employer, 2023-2027). -/
def ssRate : Int := 750
def ssQuarterCap : Int := 9000
/-- 54 F.S.M.C. 141. -/
def grtFlat : Int := 80
def grtBand : Int := 10000
def grtRate : Int := 300
def grtExempt : Int := 2000

def wageTax (w : Int) : Int :=
  let base := if w < lowWageLimit then pos (w - lowWageDeduction) else w
  sched.tax Rule.unitDown (pos base)

/-- Employee social security for the year: wages paid evenly over four quarters by `n` employers in equal shares,
    each share capped at $9,000 a quarter (the ceiling is "by one employer"). -/
def ssEmployee (n : Int) (w : Int) : Int :=
  let k := max 1 n
  divR .down (ssRate * min (pos w) (4 * ssQuarterCap * k)) BP

/-- Gross revenue tax (§ 141) on a business's gross revenue; the contract's self-employment amount is used as gross
    revenue (a documented reading: the contract has no turnover field). -/
def grossRevenueTax (g : Int) : Int :=
  if g ≤ grtExempt then 0 else grtFlat + divR .down (grtRate * pos (g - grtBand)) BP

structure Person where
  wages : Int
  tax : Int
  grt : Int
  ss : Int

def person (n : Int) (a : Adult) : Person :=
  let w := pos a.wages
  { wages := w, tax := wageTax w, grt := grossRevenueTax (pos a.selfEmployment), ss := ssEmployee n w }

def out (c : Canon) : Out :=
  let n := (c.int? "fmEmployers").getD 1
  let ps := c.adults.map (person n)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employment: gross revenue tax (§ 141) applied to the self-employment amount read as gross revenue; self-employed social security (53 F.S.M.C. 603(15)) not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["investment income: no national tax on an individual's interest, dividends or gains in 54 F.S.M.C. ch. 1 (rents of a business fall under § 141, not modelled); state taxes not modelled"] else [])
  Out.make c "FM" "USD" (sumInts (ps.map (·.tax)))
    (surtaxes := [("GrossRevenueTax", sumInts (ps.map (·.grt)))])
    (employeeSocial := sumInts (ps.map (·.ss)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.wages))), Out.d "socialSecurityEmployee" (sumInts (ps.map (·.ss))),
      Out.dStr "note" "national wage tax 6 % to $11,000 and 10 % above (§ 121); $1,000 deduction below $5,000 of wages (§ 122); social security 7.5 % to $9,000 a quarter per employer (53 F.S.M.C. 603, 901)"])
    (unsupported := unsup ++ ["wages paid evenly; social security ceiling applied per quarter per employer (input fmEmployers, default 1)"])

def country : Country := { code := "FM", name := "Micronesia (54 F.S.M.C. ch. 1; 53 F.S.M.C.)", currency := "USD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- § 121: 6 % of 11,000 = 660. -/
#guard wageTax 11000 = 660
#guard wageTax 20000 = 660 + 900
/- § 122 cliff: at $4,999 of wages the tax is 6 % of 3,999 = 239; at $5,000 it is 300 (+61 for $1 more). -/
#guard wageTax 4999 = 239
#guard wageTax 5000 = 300
/- Social security ceiling: 7.5 % of 36,000 = 2,700 a year with one employer. -/
#guard ssEmployee 1 50000 = 2700
#guard ssEmployee 2 50000 = 3750
#guard grossRevenueTax 2000 = 0 ∧ grossRevenueTax 2001 = 80 ∧ grossRevenueTax 20000 = 380

end FmTax
