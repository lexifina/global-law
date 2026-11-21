import MeTax.Params

/-!
# Montenegro 2025: monthly personal-income tax on gross pay, municipal surtax, employee contributions

Pay is taxed month by month on the gross amount (član 10, 15); 12 equal months; tax rounded half-up to the cent
(reading). The municipal surtax (prirez) is 13 % of the tax (Žabljak). Employee contributions: pension 10 % and
unemployment 0,5 % of gross pay; the minimum monthly base (lowest wage of the general collective agreement) and the
highest annual pension base (član 14) were not reached and are not applied.
Other incomes (član 12 stav 2 tač. 3-8: interest, dividends, capital gains, rent) at 15 % (rent: gross; the statutory
expense rules for rent not read, listed). Self-employment: the annual self-employment tariff on the amount given.
-/

namespace MeTax
open TaxKernel

def months : List Int := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
def monthOf (annual : Int) (m : Int) : Int := annual * m / 12 - annual * (m - 1) / 12

def taxMonthC (gC : Int) : Int := divR .halfUp (monthlySchedule.ticks (pos gC)) BP
def wageTaxC (w : Int) : Int := if w ≤ 0 then 0 else sumInts (months.map fun m => taxMonthC (monthOf (w * 100) m))
def contribC (w : Int) : Int :=
  if w ≤ 0 then 0 else
  sumInts (months.map fun m =>
    let g := monthOf (w * 100) m
    divR .halfUp (g * pensionEmployee) BP + divR .halfUp (g * unemploymentEmployee) BP)

def toEur (c : Int) : Int := divR .halfUp c 100

def out (c : Canon) : Out :=
  let ws := c.adults.map (·.wages)
  let wageT := sumInts (ws.map wageTaxC)
  let selfT := sumInts (c.adults.map fun a => divR .halfUp (annualSelfSchedule.ticks (pos a.selfEmployment * 100)) BP)
  let otherT := divR .halfUp ((pos c.interest + pos c.dividends + pos c.capitalGains + pos c.rentalIncome) * 100 * otherRate) BP
  let taxC := wageT + selfT + otherT
  let surC := divR .halfUp (taxC * surtaxRate) BP
  let unsup :=
    ["contributions: the minimum monthly base and the highest annual pension base (Zakon o doprinosima čl. 9, 14) were not reached; not applied"] ++
    (if c.rentalIncome != 0 then ["rentalIncome: taxed at 15 % of the gross rent; the expense rules for rent income were not read"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: annual tariff of član 10 (1) 2 on the amount given as taxable income; contributions of the self-employed not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pension: treatment of pensions not modelled"] else []) ++
    (if c.interest != 0 then ["interest: taxed at 15 %; interest on government securities is not capital income from 2025-11-19 (133/2025) and is not distinguished"] else [])
  Out.make c "ME" "EUR" (toEur taxC) (localIncomeTax := toEur surC) (employeeSocial := toEur (sumInts (ws.map contribC)))
    (detail := [Out.d "wageTax" (toEur wageT), Out.d "selfEmploymentTax" (toEur selfT), Out.d "otherIncomeTax" (toEur otherT),
                Out.d "taxableIncome" (sumInts ws),
                Out.dStr "note" "monthly 0 % to 700, 9 % to 1 000, 15 % above, on gross pay (čl. 10, 15); surtax 13 % of the tax (Žabljak default); employee pension 10 % + unemployment 0,5 %"])
    (unsupported := unsup)

def country : Country :=
  { code := "ME", name := "Montenegro (porez na dohodak fizičkih lica, prirez Žabljak, doprinosi)", currency := "EUR",
    year := "2025", compute := out }

end MeTax
