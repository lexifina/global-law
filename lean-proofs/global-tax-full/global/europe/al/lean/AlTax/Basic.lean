import AlTax.Params

/-!
# Albania 2025: employment income tax, investment income tax, employee contributions

Unit: the individual (Ligj 29/2023 neni 21: each person's annual tax base). Child deductions go to the parent with
the higher annual taxable income (neni 23 (1)). Investment income received jointly is the higher earner's (neni 15
(3)); with flat rates this changes nothing, so the household's investment income is taxed once.

Employment income (neni 12 (5)) is the gross pay: the law deducts no employee contribution from it. The annual tax is
computed on the year (neni 21-24); monthly withholding uses 1/12 of the same amounts (neni 23 (2)), which gives the same
tax for equal monthly pay.
-/

namespace AlTax
open TaxKernel

def months : List Int := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
def monthOf (annual : Int) (m : Int) : Int := annual * m / 12 - annual * (m - 1) / 12

/-- Employee contributions on one month's wage (Ligj 7703 neni 10: "brenda kufijve të pagës minimale ... dhe pagës
maksimale"; the minimum contribution is computed on the minimum wage). Rounded half-up to the lek (reading). -/
def contribMonth (g : Int) : Int :=
  if g ≤ 0 then 0 else
  let base := clamp minWage maxWage g
  divR .halfUp (base * (ssEmployee + healthEmployee)) BP

def contribYear (w : Int) : Int := sumInts (months.map fun m => contribMonth (monthOf w m))

/-- Employment income tax of one person with `kids` children allotted (neni 21, 22, 24). -/
def empTax (wage kids : Int) : Int :=
  if wage ≤ 0 then 0 else
  let ded := personalDeduction wage + kids * childDeduction
  divR .halfUp (empSchedule.ticks (pos (wage - ded))) BP

/-- Business income (net) of one person: 0 % if gross business income is at most 14 M (neni 69 (1) (dh); gross taken
as the net amount given: reading), else neni 24 (2). -/
def busTax (se : Int) : Int :=
  if se ≤ busZeroLimit then 0 else divR .halfUp (busSchedule.ticks se) BP

def out (c : Canon) : Out :=
  let ws := c.adults.map (·.wages)
  let kids : Int := c.childrenUnder childAgeLimit
  -- children to the higher earner (neni 23 (1))
  let top := ws.foldl max 0
  let idxTop := (ws.findIdx? (· == top)).getD 0
  let taxes := (ws.zipIdx).map fun (w, i) => empTax w (if i == idxTop then kids else 0)
  let empT := sumInts taxes
  let busT := sumInts (c.adults.map fun a => busTax a.selfEmployment)
  let divT := divR .halfUp (pos c.dividends * dividendRate) BP
  let invBase := pos c.interest + pos c.rentalIncome + pos c.capitalGains
  let invT := divR .halfUp (invBase * investmentRate) BP
  let soc := sumInts (ws.map contribYear)
  let unsup :=
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: taken as both gross and net business income; employment-like self-employment (neni 12 (1) (ç)) and the self-employed's contributions not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pension: social-insurance pensions are not subject to the tax (neni 11 (a)); private pensions (neni 20) not modelled"] else []) ++
    (if c.charitable != 0 || c.pensionContributions != 0 then ["charitable/pensionContributions: neni 20 (1) private pension deduction and education expenses (neni 22 (2)) not modelled"] else []) ++
    (if c.adults.any (fun a => a.wages > 0 && a.wages < 12 * minWage) then ["contributions on pay below the minimum wage are computed on the minimum wage (Ligj 7703 neni 10, reading for part-year/part-time pay)"] else [])
  Out.make c "AL" "ALL" (empT + busT + divT + invT) (employeeSocial := soc)
    (detail := [Out.d "employmentIncomeTax" empT, Out.d "businessIncomeTax" busT, Out.d "dividendTax" divT,
                Out.d "otherInvestmentTax" invT,
                Out.d "taxableIncome" (sumInts ((ws.zipIdx).map fun (w, i) =>
                  pos (w - personalDeduction w - (if i == idxTop then kids * childDeduction else 0)))),
                Out.dStr "note" "Ligj 29/2023: individual; personal deduction 600 000 / 420 000 / 360 000 by income (neni 22); 13 %/23 % (neni 24); dividends 8 %, other investment income 15 %"])
    (unsupported := unsup)

def country : Country :=
  { code := "AL", name := "Albania (tatimi mbi të ardhurat personale, sigurime)", currency := "ALL", year := "2025",
    compute := out }

end AlTax
