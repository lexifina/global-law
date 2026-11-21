import TaxKernel.World

/-!
# Palestine (Palestinian Authority, West Bank): income tax of resident individuals, 2025

Access tier A for the tax (decree-law and every amendment the official gazette's catalogue lists, as published by
Al-Muqtafi, the Birzeit University legal database that Global law's catalogue cites as its source); contributions not
modelled. Gaza has been administered separately since 2007; this is the PA law.
Sources (Internet Archive copies of muqtafi.birzeit.edu/pg/getleg.asp?id=…, which does not answer directly;
`ps/law/rescue/`, sha256 in SHA256SUMS):
* Decree-Law No. 8 of 2011 on Income Tax (Al-Waqa'i' special issue 5, 2011-10-24; muqtafi id 16266, capture
  2025-01-06): art. 12(1) exemptions of a resident natural person (a) annual exemption, (b)-(c) transport allowance,
  (d) employee contributions to pension/savings/health/social-security funds, (e) housing, (f) university;
  art. 14(1) "يعتبر كل من الزوج والزوجة مكلفاً مستقلاً" (spouses taxed separately), 14(2) each spouse has the
  exemptions except (e) and (f), 14(3) optional joint assessment; art. 16(1) rates on a natural person's taxable income.
* Decree-Law No. 4 of 2014 (issue 106, 2014-04-10; id 16576): art. 16(5) replaced: "تستوفى الضريبة بنسبة (%10) على
  الأرباح ... على أن تقتطع من المصدر" (10 % on dividends, withheld at source); art. 31(8) (5 % final tax on bank
  interest) repealed.
* Decree-Law No. 5 of 2015 (issue 112, 2015-04-29; id 16702): art. 12(1)(a) "إعفاء سنوي مقداره (36.000) شيكل";
  art. 16(1): "من (1) حتى (75.000) شيكل بنسبة (5 %) ... من (75.001) حتى (150000) شيكل بنسبة (10 %) ... ما زاد عن ذلك
  بنسبة (15 %)".
* Decree-Law No. 14 of 2016 (issue 123, 2016-07-31; id 16814): agricultural income exempt (art. 7(20)).
Global law's catalogue of the Waqa'i' (complete to 2026-10-29) lists no later text whose title mentions income tax.
Household mapping: each adult is a separate taxpayer (art. 14(1)); taxable income = wages + self-employment + rent
(net, art. 3 sources) less the 36,000-shekel exemption; dividends 10 % at source (art. 16(5)); transport allowances
and fund contributions (art. 12(1)(b)-(d)) are not in the household contract. Rounding: whole shekels, down.
-/

namespace PsTax
open TaxKernel

/-- art. 16(1) as replaced by Decree-Law 5/2015. -/
def sched : Schedule := Schedule.ofList [(0, 500), (75000, 1000), (150000, 1500)]
/-- art. 12(1)(a) as replaced by Decree-Law 5/2015. -/
def exemption : Int := 36000

#guard sched.tax Rule.unitDown 75000 = 3750 ∧ sched.tax Rule.unitDown 150000 = 11250

def personTax (income : Int) : Int × Int :=
  let ti := pos (income - exemption)
  (sched.tax Rule.unitDown ti, ti)

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let incomes := (List.range c.adults.length).zip c.adults |>.map fun (i, a) => a.wages + a.selfEmployment + share c.rentalIncome i
  let res := incomes.map personTax
  let divTax := divR .down (1000 * pos c.dividends) BP
  Out.make c "PS" "ILS" (sumInts (res.map (·.1))) (surtaxes := [("dividendTaxAtSource", divTax)])
    (employeeSocial := 0)
    (detail := [Out.d "taxableIncome" (sumInts (res.map (·.2))),
      Out.dStr "note" "Decree-Law 8/2011 as amended by 4/2014, 5/2015, 14/2016: exemption 36,000 ILS, 5/10/15 % at 75,000/150,000; spouses separate (art. 14); dividends 10 % at source"])
    (unsupported := ["employee contributions to pension, health or social-security funds (exempt under art. 12(1)(d)) not modelled: employeeSocial = 0"] ++
      (if c.interest ≠ 0 then ["interest: the 5 % final tax on bank interest (art. 31(8)) was repealed in 2014; its current treatment was not established"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains (art. 7(16) exempts gains on securities from investment portfolios) not modelled"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions (art. 7 exemptions) not modelled"] else []) ++
      (if c.isCouple then ["optional joint assessment of spouses (art. 14(3)) not modelled"] else []))

def country : Country := { code := "PS", name := "Palestine (PA, West Bank)", currency := "ILS", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end PsTax
