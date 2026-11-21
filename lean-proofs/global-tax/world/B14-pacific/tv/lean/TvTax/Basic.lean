import TaxKernel.World

/-!
# Tuvalu: income tax on individuals, Income Tax Act (Cap. 26.16), year 2025

Global law holds no Tuvalu text (its corpus is paused because the publisher's copyright notice forbids
redistribution); the model reads the official Tuvalu Legislation site (Attorney-General, tuvalu-legislation.tv) and
quotes only short phrases. Files in `tv/law/`:
* Point-in-time list of acts in force on 2025-07-01 (POST `pointintime=2025-07-01 00:00:00`, `b14tv_I.html`): "Income
  Tax Act ... Version: 2 Date Commenced: Saturday, 31 December 2022 Details: Consolidated as part of the 2022 Revised
  Edition Date Superseded: CURRENT FILE": no later version or amending act in force in 2025.
* Income Tax Act, 2022 Revised Edition (`1992-0005_2.pdf`), Schedule 6 (endnote 26: "Amended by LN 16/1995, LN 1/1996,
  LN 19/1999, Act 10 of 2008, and LN 2/2021"): "1. ... income tax shall be payable at the rates set out below in respect
  of that person's taxable income for that year: | % of taxable income | (a) Taxable income of an individual, not
  exceeding ten thousand dollars 0% | (b) ... exceeding ten thousand dollars but not exceeding fourteen thousand
  dollars 15% | (c) ... exceeding fourteen thousand dollars 30%". s 15(1)(a): "any sum contributed to an approved fund"
  is a deductible cost.
* Income Tax Regulations (Cap. 26.16.1, 2022 Revised Edition, `2021-0125_1.pdf`) reg 4: withholding grosses the
  period wage "(a - b) x c" where "b is the amount of any contributions taken from the employee's gross wage as
  contributions to an approved fund", then applies "the progressive tax rates specified in paragraphs 1(a) to (c) of
  Schedule 6 ... with allowance made for the annual tax-free threshold of ten thousand dollars".
* Provident Fund (Contributions) Regulations (Cap. 32.08.4, 2022 Revised Edition, `1985-0016_2.pdf`) Schedule 1: "1.
  Group 1 contributions (employed persons) (i) The contribution shall be 13 per cent of the member's gross earnings";
  "2. Group 2 contributions (employers) ... 10 per cent ... subject to recovery of the group 1(i) contribution from the
  employee by deduction from salary".
Readings (statute-visible): Schedule 6 heads its column "% of taxable income" and lists each rate against a band of
the whole taxable income, which read literally is a slab tariff (`tvReading: "slab"`); the Regulations' "progressive
tax rates ... with allowance made for the annual tax-free threshold" read it as graduated (default). The Provident
Fund is treated as an approved fund (reg 4 deducts its contributions before tax), switch `tvPFApproved: false`.
-/

namespace TvTax
open TaxKernel

/-- Schedule 6 para 1(a)-(c), graduated reading. -/
def sched : Schedule := Schedule.ofList [(0, 0), (10000, 1500), (14000, 3000)]
/-- Schedule 6, literal slab reading: the rate of the band on the whole taxable income. -/
def slabRate (x : Int) : Int := if x ≤ 10000 then 0 else if x ≤ 14000 then 1500 else 3000
def slabTax (x : Int) : Int := divR .down (slabRate x * pos x) BP
/-- Provident Fund (Contributions) Regulations Schedule 1 para 1(i). -/
def pfRate : Int := 1300

structure Person where
  taxable : Int
  tax : Int
  pf : Int

def person (slab approved : Bool) (a : Adult) (rent : Int) : Person :=
  let w := pos a.wages
  let pf := divR .down (pfRate * w) BP
  let ti := pos (w + a.selfEmployment + rent - (if approved then pf else 0))
  { taxable := ti, tax := if slab then slabTax ti else sched.tax Rule.unitDown ti, pf := pf }

def persons (slab approved : Bool) (c : Canon) : List Person :=
  match c.adults with
  | [a] => [person slab approved a c.rentalIncome]
  | a :: b :: _ => [person slab approved a (half1 c.rentalIncome), person slab approved b (half2 c.rentalIncome)]
  | [] => []

def out (c : Canon) : Out :=
  let slab := (c.str? "tvReading").getD "graduated" == "slab"
  let approved := (c.bool? "tvPFApproved").getD true
  let ps := persons slab approved c
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.capitalGains ≠ 0 then ["interest, dividends and gains: withholding (Schedule 5) and dividend rules not modelled; ignored"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income taxed in taxable income; presumptive tax (s 5A, Regulations reg 3) and deductions not modelled"] else [])
  Out.make c "TV" "AUD" (sumInts (ps.map (·.tax)))
    (employeeSocial := sumInts (ps.map (·.pf)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.taxable))), Out.d "providentFundEmployee" (sumInts (ps.map (·.pf))),
      Out.dStr "reading" (if slab then "slab" else "graduated"),
      Out.dStr "note" "individual; Schedule 6: 0 % to 10,000, 15 % to 14,000, 30 % above; Provident Fund 13 % deducted as an approved-fund contribution (s 15(1)(a))"])
    (unsupported := unsup)

def country : Country := { code := "TV", name := "Tuvalu (Income Tax Act Cap. 26.16)", currency := "AUD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Graduated: 15 % of 4,000 = 600 at 14,000; + 30 % above. -/
#guard sched.tax Rule.unitDown 14000 = 600
#guard sched.tax Rule.unitDown 20000 = 2400
/- Slab reading: $1 above 10,000 costs 1,500; $1 above 14,000 raises the tax from 2,100 to 4,200. -/
#guard slabTax 10000 = 0 ∧ slabTax 10001 = 1500
#guard slabTax 14000 = 2100 ∧ slabTax 14001 = 4200
/- PF 13 % deducted: a wage of 20,000 leaves taxable income 17,400 and tax 600 + 30 % of 3,400 = 1,620. -/
#guard (person false true { age := 30, wages := 20000, selfEmployment := 0, pension := 0 } 0).tax = 1620

end TvTax
