import TaxKernel.World

/-!
# Georgia: personal income tax (Tax Code of Georgia 2010, Part V) and the funded-pension contribution, tax year 2025

Statutes read (Global law `georgia/national/acts`, official text matsne.gov.ge; files in `ge/law/`), as in force on
2025-07-01:
* Tax Code art. 81 (last changed by Law №134-Iმს-XIმპ of 13.12.2024, in force 2025-01-01;
  official https://matsne.gov.ge/ka/document/view/4595604): (1) "ფიზიკური პირის დასაბეგრი შემოსავალი იბეგრება
  20 პროცენტით"; (2) residential letting by a person who claims no deductions "5 პროცენტით იბეგრება"; (3) gains on a
  dwelling or a car 5 %.
* art. 80(1): the taxable income is gross income of the calendar year less the deductions of the Code.
* art. 82(1)(ბ): state pensions exempt; (ბ³) "დაგროვებითი საპენსიო სქემის მონაწილის ინდივიდუალურ საპენსიო ანგარიშზე
  განხორციელებული საპენსიო შენატანი" (the funded-pension contribution) exempt.
* art. 130(1): dividends paid by a resident enterprise to a natural person "იბეგრება გადახდის წყაროსთან ... 5-პროცენტიანი
  განაკვეთით"; (3) not included in gross income afterwards (final).
* art. 131(1): interest 5 % at source, (3) final; (5) interest from a licensed financial institution "გადახდის წყაროსთან
  არ იბეგრება" and is not included in gross income.
* Law on Funded Pensions (№3303-რს, 2018) art. 3 (last changed by Law №4313 of 27.06.2024, in force 2024-07-12): (2)
  participation compulsory for every employee except one who was 60 (man) / 55 (woman) before the law took effect
  (2019-01-01); (6)(ბ) employee contribution "დასაბეგრი ხელფასის 2 პროცენტის ოდენობით"; (6)(გ) self-employed 4 %.
Unit: individual (art. 80). No personal allowance and no child relief in the Code.
-/

namespace GeTax
open TaxKernel

/-- Rounding of a percentage to whole lari, half up (the Code's rounding rule, art. 37, was not read: flagged). -/
def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

/-- art. 81(1): the general rate, 20 %. -/
def rate : Int := 2000
def sched : Schedule := Schedule.flat rate
/-- art. 81(2): residential letting without deductions, 5 %. -/
def rentRate : Int := 500
/-- art. 130(1): dividends, 5 % at source, final (130(3)). -/
def divRate : Int := 500
/-- art. 131(1): interest, 5 % at source (not for interest from a licensed financial institution, 131(5)). -/
def intRate : Int := 500
/-- Law №3303 art. 3(6)(ბ): employee contribution 2 % of taxable salary. -/
def penEmployee : Int := 200
/-- art. 3(6)(გ): self-employed 4 % of income. -/
def penSelf : Int := 400

/-- art. 3(2): a participant unless 60 (men) / 55 (women) before 2019-01-01. A person aged `age` at the end of 2025
was at least `age - 7` on 2018-12-31; the canonical household has no sex, so ages 62-66 are ambiguous (a woman is
excluded, a man is not): the model treats them as participants and says so. -/
def participant (age : Nat) : Bool := age ≤ 66

def taxOn (x : Int) : Int := sched.tax Rule.unitHalfUp (pos x)

def out (c : Canon) : Out :=
  let rows := c.adults.map fun a =>
    let part := participant a.age
    let penW := if part then pct penEmployee (pos a.wages) else 0
    let penS := if part then pct penSelf (pos a.selfEmployment) else 0
    -- art. 82(1)(ბ³): the contribution is exempt, so it leaves the taxable salary
    let base := pos (a.wages - penW) + pos (a.selfEmployment - penS)
    (taxOn base, penW + penS, base)
  let earnTax := sumInts (rows.map (·.1))
  let pension := sumInts (rows.map (·.2.1))
  let otherInterest := (c.str? "interestSource") == some "other"
  let intTax := if otherInterest then pct intRate (pos c.interest) else 0
  let divTax := pct divRate (pos c.dividends)
  let rentTax := pct rentRate (pos c.rentalIncome)
  let cgTax := taxOn c.capitalGains
  let ambiguous := c.adults.any fun a => 62 ≤ a.age && a.age ≤ 66
  Out.make c "GE" "GEL" (earnTax + intTax + divTax + rentTax + cgTax)
    (employeeSocial := pension)
    (detail := [Out.d "taxableIncome" (sumInts (rows.map (·.2.2))), Out.d "earningsTax" earnTax,
      Out.d "dividendTax" divTax, Out.d "interestTax" intTax, Out.d "rentTax" rentTax, Out.d "capitalGainsTax" cgTax,
      Out.d "fundedPension" pension,
      Out.dStr "note" "20 % flat (TC art. 81(1)); 2 % funded-pension contribution exempt (art. 82(1)(b3)); dividends 5 % final (art. 130); bank interest exempt (art. 131(5)); residential rent 5 % (art. 81(2))"])
    (unsupported := (if ambiguous then ["funded pension: participation at ages 62-66 depends on sex (Law 3303 art. 3(2)); treated as participant"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains taxed at 20 %; dwellings and cars 5 % (art. 81(3)) and the art. 82 exemptions (holding periods) not modelled"] else []) ++
      (if c.interest ≠ 0 && !otherInterest then ["interest assumed paid by a licensed financial institution: not taxed (art. 131(5)); pass interestSource=other for 5 %"] else []) ++
      (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions assumed state pensions: exempt (art. 82(1)(b)); private pensions not modelled"] else []) ++
      ["employees aged 40+ in 2019 could leave the funded scheme (Law 3303 art. 3(5), 22): not modelled (default participant)",
       "rounding to whole lari half up (TC rounding rule not read)"])

def country : Country := { code := "GE", name := "Georgia (PIT + funded pension)", currency := "GEL", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Worked check: 1 000 lari of salary: contribution 20, tax 20 % of 980 = 196. -/
#guard (out { id := "g", adults := [{ age := 35, wages := 1000 }] }).incomeTax = 196
#guard (out { id := "g", adults := [{ age := 35, wages := 1000 }] }).employeeSocial = 20

end GeTax
