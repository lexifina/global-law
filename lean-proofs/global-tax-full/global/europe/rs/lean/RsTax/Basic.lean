import RsTax.Params

/-!
# Serbia 2025: salary tax (schedular, monthly), capital income tax, employee contributions; the annual tax as a
function of the average annual salary

Serbia taxes each kind of income on its own (ЗПДГ чл. 3-4: by withholding, assessment or self-assessment) and then
levies an annual tax (чл. 87-89) on the sum of some kinds above three average annual salaries: a schedular system with
an overlay **without credit** (kernel `overlayTax`, World). The overlay needs the 2025 average annual salary, which
the model could not cite; it is computed only when the household line gives `"rs_avgAnnualSalary"` (an input field,
default absent) and is otherwise listed in `unsupported`.

Salary tax: 12 equal monthly wages; each month 10 % of (wage − 28 423) (чл. 15а, 16), not below 0. Contributions:
19,9 % of the wage (чл. 44); the minimum and maximum monthly bases (чл. 37-42: 35 % and 5 × the average monthly wage,
published by the minister) were not reached and are not applied (unsupported).
-/

namespace RsTax
open TaxKernel

def months : List Int := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
def monthOf (annual : Int) (m : Int) : Int := annual * m / 12 - annual * (m - 1) / 12

def salaryTaxMonth (g : Int) : Int := divR .halfUp (pos (g - monthlyNonTaxable) * wageRate) BP
def salaryTax (w : Int) : Int := if w ≤ 0 then 0 else sumInts (months.map fun m => salaryTaxMonth (monthOf w m))

def contribMonth (g : Int) : Int :=
  divR .halfUp (g * pioEmployee) BP + divR .halfUp (g * healthEmployee) BP + divR .halfUp (g * unemploymentEmployee) BP
def contrib (w : Int) : Int := if w ≤ 0 then 0 else sumInts (months.map fun m => contribMonth (monthOf w m))

/-- The annual tax (чл. 87-89) for one person given the average annual salary `A`, the person's yearly net salary
and self-employment income (after tax and contributions, чл. 87 ст. 3), age under 40 (чл. 87 ст. 4) and number of
dependants. -/
def annualTax (A netInc : Int) (under40 : Bool) (deps : Int) : Int :=
  let afterYoung := if under40 then pos (netInc - min netInc (3 * A)) else netInc
  let forTax := pos (afterYoung - 3 * A)
  let ded := min (divR .halfUp (forTax * 5000) BP) (divR .halfUp (A * 4000) BP + deps * divR .halfUp (A * 1500) BP)
  let base := pos (forTax - ded)
  let s := Schedule.ofList [(0, 1000), (6 * A, 1500)]
  divR .halfUp (s.ticks base) BP

def out (c : Canon) : Out :=
  let ws := c.adults.map (·.wages)
  let sal := sumInts (ws.map salaryTax)
  let soc := sumInts (ws.map contrib)
  let selfT := sumInts (c.adults.map fun a => divR .halfUp (pos a.selfEmployment * selfRate) BP)
  let capT := divR .halfUp ((pos c.interest + pos c.dividends + pos c.capitalGains) * capitalRate) BP
  let rentT := divR .halfUp (pos c.rentalIncome * (BP - rentCosts) * rentRate) (BP * BP)
  let deps : Int := c.nChildren
  let annual := match c.int? "rs_avgAnnualSalary" with
    | some A => sumInts ((c.adults.zipIdx).map fun (a, i) =>
        annualTax A (a.wages - salaryTax a.wages - contrib a.wages + pos a.selfEmployment)
          (a.age < 40) (if i == 0 then deps else 0))
    | none => 0
  let unsup :=
    (if (c.int? "rs_avgAnnualSalary").isNone then ["annual citizens' income tax (ZPDG art. 87-89): the 2025 average annual salary is not cited; not computed (supply rs_avgAnnualSalary to compute it)"] else []) ++
    ["contributions: the 2025 minimum and maximum monthly bases (Zakon o doprinosima art. 37-42) were not reached; not applied"] ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: taxed at 10 % on the amount given as taxable income (art. 33, 38); lump-sum regime and contributions not modelled"] else []) ++
    (if c.interest != 0 then ["interest: taxed at 15 %; interest on dinar deposits and state bonds is exempt (art. 65): not distinguished"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pension: compulsory-insurance pensions are exempt (art. 9 (1) 17); others not modelled"] else [])
  Out.make c "RS" "RSD" (sal + selfT + capT + rentT) (surtaxes := [("annualCitizensIncomeTax", annual)])
    (employeeSocial := soc)
    (detail := [Out.d "salaryTax" sal, Out.d "selfEmploymentTax" selfT, Out.d "capitalIncomeTax" capT, Out.d "rentTax" rentT,
                Out.d "taxableIncome" (sumInts (ws.map fun w => pos (w - 12 * monthlyNonTaxable))),
                Out.dStr "note" "schedular: 10 % salary tax on pay less 28 423 a month; capital income 15 %; rent 20 % of 75 %; the annual tax is an overlay without credit"])
    (unsupported := unsup)

def country : Country :=
  { code := "RS", name := "Serbia (porez na zarade, porez na prihode od kapitala, doprinosi; godišnji porez)",
    currency := "RSD", year := "2025", compute := out }

end RsTax
