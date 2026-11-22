import HrTax.Params

/-!
# Croatia 2025: contributions and income tax of one person (cents)

Employees: pension contributions from pay (ZD čl. 13, 17, 21, 21.a) computed each month on one twelfth of the annual
pay (`perPeriod 12`, the payroll month is ZD's "mjesečna osnovica"), rounded to the cent; the dohodak from
employment is pay less those contributions (ZPD čl. 23); the annual base is the year's dohodak from employment,
pensions and self-employment less the personal allowance (ZPD čl. 13, 14, 18); the annual tax is the local lower
rate up to 60.000 € and the higher rate above (ZPD čl. 19, 19.a); young workers' relief (ZPD čl. 46 st. 2).

Rounding: the statutes state amounts in euros and cents and give no rounding rule for the tax; the model rounds each
contribution (per month) and each tax amount to the cent, half up (payroll practice; Zakon o uvođenju eura
čl. 13: "zaokružuje na najbliži cent"), and the output to whole euros, half up.
-/

namespace HrTax
open TaxKernel

/-- bp × cents to cents, half up. -/
def rnd (ticks : Int) : Int := divR .halfUp ticks BP

/-! ## Employee contributions (monthly) -/

/-- ZD čl. 21, 204-205: the month's pension base, capped at the najviša mjesečna osnovica ("obveza je obračuna i
plaćanja doprinosa za mirovinsko osiguranje na temelju generacijske solidarnosti i ... individualne kapitalizirane
štednje do iznosa najviše mjesečne osnovice", čl. 204 st. 1; the cap is for pension contributions only). Not modelled:
the najniža mjesečna osnovica for full-time work (čl. 200, 683,24 € in 2025; below the 2025 minimum wage) and the
annual cap of čl. 206 (it binds only with uneven pay). -/
def monthBase (m : Int) : Int := min (pos m) maxMonthlyBase

/-- ZD čl. 21.a: the reduced pillar-I base (kernel `reducedBase`; the reduction is computed on the month's gross
pay, which is below the cap wherever the reduction is positive). -/
def pillar1Base (m : Int) : Int := reducedBase baseReduction (monthBase m)

/-- Pillar I contribution for a month's pay `m` (cents). -/
def p1Month (pillar2 : Bool) (m : Int) : Int := rnd (pillar1Rate pillar2 * pillar1Base m)
/-- Pillar II contribution for a month's pay (cents); ZD čl. 21.a reduces only the pillar-I base. -/
def p2Month (pillar2 : Bool) (m : Int) : Int := rnd (pillar2Rate pillar2 * monthBase m)
/-- Employer health contribution (ZD čl. 14 st. 1 t. 1, "na osnovicu"): detail only, not the employee's. -/
def healthMonth (m : Int) : Int := rnd (healthRate * pos m)

/-! ## Uneven monthly pay (for FINDINGS: the monthly rules of ZD čl. 21.a and 204 have no annual equalisation) -/

/-- Employee pension contributions for an explicit list of monthly gross pays (cents). -/
def eeContribMonths (p2 : Bool) (ms : List Int) : Int :=
  ms.foldl (fun acc m => acc + p1Month p2 m + p2Month p2 m) 0

/-- Annual pillar I / II / employer health on annual pay `w` paid evenly over 12 months (cents). -/
def p1Year (p2 : Bool) (w : Int) : Int := perPeriod 12 (p1Month p2) w
def p2Year (p2 : Bool) (w : Int) : Int := perPeriod 12 (p2Month p2) w
def healthYear (w : Int) : Int := perPeriod 12 healthMonth w
def eeContribYear (p2 : Bool) (w : Int) : Int := p1Year p2 w + p2Year p2 w

/-! ## Self-employed contributions (ZD čl. 64-70; Naredba NN 137/24 čl. 6, 7) -/

/-- Obrt with books (dohodak): pension 20 % (15 + 5) and health 16,5 % on the fixed monthly base 1.168,70 €,
whatever the profit (ZD čl. 65, 66 st. 1 t. 1). Annual, cents. -/
def seContribMonth (p2 : Bool) (base : Int) : Int :=
  rnd (pillar1Rate p2 * base) + rnd (pillar2Rate p2 * base) + rnd (healthRate * base)
def seContribYear (p2 : Bool) : Int := 12 * seContribMonth p2 seMonthlyBase
/-- Paušalist obrt: the same contributions on the monthly base 719,20 € (ZD čl. 69, 70). -/
def pausalContribYear (p2 : Bool) : Int := 12 * seContribMonth p2 pausalMonthlyBase

/-- Paušalni dohodak for annual receipts `r` (cents): the class table (Pravilnik čl. 3 st. 1), as a kernel `Table`. -/
def pausalTable : Table :=
  (pausalClasses.zip ((0, 0) :: pausalClasses)).map fun ((hi, v), (lo, _)) => ⟨lo + (if lo = 0 then 0 else 1), hi, v⟩
def pausalIncome (r : Int) : Int := Table.lookup pausalTable (pos r) 0
/-- Paušalni porez (ZPD čl. 82 st. 5: 12 %), cents. -/
def pausalTax (r : Int) : Int := rnd (pausalRate * pausalIncome r)

/-! ## Personal allowance (ZPD čl. 14) -/

/-- Sum of the child coefficients (tenths) for `n` dependent children (r.br. 2-11). -/
def childCoefTotal (n : Nat) : Int :=
  perChildByRank childCoefs (min n 9)
    + (List.range (n - 9)).foldl (fun (acc : Int) (k : Nat) => acc + (49 + childCoefStep * ((k : Int) + 1))) 0

/-- The monthly allowance for `n` children (cents): coefficient × 600 €. -/
def childAllowanceMonthly (n : Nat) : Int := childCoefTotal n * basicPA / 10

/-! ## Annual income tax of one person -/

structure Person where
  age : Nat := 40
  /-- dohodak from employment (pay less pension contributions), cents -/
  wageDoh : Int := 0
  /-- pensions, cents (no contributions) -/
  pensDoh : Int := 0
  /-- dohodak from self-employment with books (profit less own contributions), cents -/
  seDoh : Int := 0
  /-- monthly allowance increments on top of the basic 600 € (children's share, dependants), cents -/
  paExtraMonthly : Int := 0
  /-- donations claimed and the receipts that cap them (ZPD čl. 15 st. 2), cents -/
  donations : Int := 0
  receipts : Int := 0
  deriving Repr

/-- Dohodak entering the annual base (ZPD čl. 13). -/
def Person.dohodak (p : Person) : Int := pos p.wageDoh + pos p.pensDoh + pos p.seDoh

/-- Personal allowance for the year (ZPD čl. 14 st. 1, 3; čl. 15 st. 2), cents. -/
def Person.allowance (p : Person) : Int :=
  12 * (basicPA + p.paExtraMonthly) + min (pos p.donations) (donationCapBp * pos p.receipts / BP)

/-- Annual tax base (ZPD čl. 18 st. 1), cents. -/
def Person.base (p : Person) : Int := taxableAfter p.allowance p.dohodak

/-- Tax before the young workers' relief (ZPD čl. 19), cents. -/
def Person.taxBefore (r : Rates) (p : Person) : Int := rnd ((annualSched r).ticks p.base)

/-- The tax at the lower rate on the base up to 60.000 € (cents). -/
def Person.taxLower (r : Rates) (p : Person) : Int := rnd (r.lower * min p.base bandLimitAnnual)

/-- ZPD čl. 46 st. 2: the relief = pct × the lower-rate tax × the share of employment dohodak in the dohodak. -/
def Person.youngRelief (r : Rates) (p : Person) : Int :=
  if p.dohodak ≤ 0 then 0
  else divR .halfUp (youngReliefBp p.age * p.taxLower r * pos p.wageDoh) (p.dohodak * BP)

/-- Annual income tax (cents). -/
def Person.tax (r : Rates) (p : Person) : Int := p.taxBefore r - p.youngRelief r

/-! ## Final taxes on capital and rent (one person's share, cents) -/

def interestTax (x : Int) : Int := rnd (capitalRate * pos x)
def dividendTax (x : Int) : Int := rnd (capitalRate * pos x)
/-- ZPD čl. 57 st. 1, 62 st. 1: 12 % of rent less 30 % flat expenses. -/
def rentTax (x : Int) : Int := rnd (capitalRate * (pos x - rnd (rentExpenseBp * pos x)))

/-! ## Monthly withholding (ZPD čl. 24): for the over-withholding of 2025 -/

/-- The month's advance on pay `m` with monthly allowance `pa` at rates `r` (no young relief: annual only). -/
def whMonth (r : Rates) (p2 : Bool) (pa m : Int) : Int :=
  rnd ((monthlySched r).ticks (taxableAfter pa (m - p1Month p2 m - p2Month p2 m)))

/-- Zagreb 2025: January and February at the 2024 decision's rates (NN 152/24 čl. 14 st. 4), March to December at
the 2025 decision's (NN 28/2025 čl. 3); an even monthly pay `w/12` (cents, `w` divisible by 12 for exactness). -/
def whYearZagreb (p2 : Bool) (pa w : Int) : Int :=
  let m := w / 12
  2 * whMonth zagreb2024 p2 pa m + 10 * whMonth zagreb2025 p2 pa m

/-! ## Any modelled tax year (`YP`): the same rules with the year's parameters (round 2)

For `yp2025` every function below gives the 2025 function above (checked on named households in `Walls`/`Tests`
through `computeCents`, which now runs on `ypFor c.year`). -/

def monthBaseY (y : YP) (m : Int) : Int := min (pos m) y.maxMonthly
def pillar1BaseY (y : YP) (m : Int) : Int :=
  if y.reduction then reducedBase baseReduction (monthBaseY y m) else monthBaseY y m
def p1MonthY (y : YP) (pillar2 : Bool) (m : Int) : Int := rnd (pillar1Rate pillar2 * pillar1BaseY y m)
def p2MonthY (y : YP) (pillar2 : Bool) (m : Int) : Int := rnd (pillar2Rate pillar2 * monthBaseY y m)
def eeContribYearY (y : YP) (p2 : Bool) (w : Int) : Int :=
  perPeriod 12 (p1MonthY y p2) w + perPeriod 12 (p2MonthY y p2) w
def seContribYearY (y : YP) (p2 : Bool) : Int := 12 * seContribMonth p2 y.seBase
def pausalContribYearY (y : YP) (p2 : Bool) : Int := 12 * seContribMonth p2 y.pausalBase

def pausalTableY (y : YP) : Table :=
  (y.pausalClasses.zip ((0, 0) :: y.pausalClasses)).map fun ((hi, v), (lo, _)) => ⟨lo + (if lo = 0 then 0 else 1), hi, v⟩
def pausalTaxY (y : YP) (r : Int) : Int := rnd (y.pausalRate * Table.lookup (pausalTableY y) (pos r) 0)

/-- The coefficient (tenths) of the child of rank `k` (0-based): the table, then +1,1 per further child. -/
def childCoefAt (y : YP) (k : Nat) : Int :=
  let n := y.childCoefs.length
  if k < n then y.childCoefs.getD k 0 else y.childCoefs.getLastD 0 + childCoefStep * ((k + 1 - n : Nat) : Int)

/-- Monthly child allowance (cents): each rank's coefficient × the base, rounded to the cent (the table's
"Mjesečni iznos" column; exact for 2024-25). -/
def childAllowanceMonthlyY (y : YP) (n : Nat) : Int :=
  (List.range n).foldl (fun acc k => acc + divR .halfUp (childCoefAt y k * y.coefBase) 10) 0

def dependantAmountY (y : YP) : Int := divR .halfUp (y.coefDependant * y.coefBase) 10
/-- ZPD čl. 17 st. 1: a dependant's receipts at most six times the basic allowance (a year). -/
def dependantLimitY (y : YP) : Int := 6 * y.basicPA

def Person.allowanceY (y : YP) (p : Person) : Int :=
  12 * (y.basicPA + p.paExtraMonthly) + min (pos p.donations) (donationCapBp * pos p.receipts / BP)
def Person.baseY (y : YP) (p : Person) : Int := taxableAfter (p.allowanceY y) p.dohodak
def annualSchedY (y : YP) (r : Rates) : Schedule := Schedule.ofList [(0, r.lower), (y.bandAnnual, r.higher)]
def Person.taxBeforeY (y : YP) (r : Rates) (p : Person) : Int := rnd ((annualSchedY y r).ticks (p.baseY y))
def Person.taxLowerY (y : YP) (r : Rates) (p : Person) : Int := rnd (r.lower * min (p.baseY y) y.bandAnnual)
def Person.youngReliefY (y : YP) (r : Rates) (p : Person) : Int :=
  if p.dohodak ≤ 0 then 0
  else divR .halfUp (youngReliefBp p.age * p.taxLowerY y r * pos p.wageDoh) (p.dohodak * BP)
/-- Income tax after the young relief (cents). -/
def Person.taxY (y : YP) (r : Rates) (p : Person) : Int := p.taxBeforeY y r - p.youngReliefY y r
/-- Prirez on a tax amount (2023: Zagreb 18 %; 0 from 2024). -/
def surtaxY (y : YP) (t : Int) : Int := rnd (y.surtaxBp * t)

def capTaxY (y : YP) (x : Int) : Int := rnd (y.capitalRate * pos x)
def rentTaxY (y : YP) (x : Int) : Int := rnd (y.capitalRate * (pos x - rnd (rentExpenseBp * pos x)))

theorem childAllowanceMonthlyY_2025 : (List.range 11).map (childAllowanceMonthlyY yp2025) =
    (List.range 11).map childAllowanceMonthly := by decide
/-- The 2023 table's monthly amounts (NN 151/22 čl. 5): 232,27 / 331,81 / 464,53 / 630,44 / 829,53 / 1061,79 /
1327,24 / 1625,87 / 1957,68 for the 1st to 9th child; dependant 232,27. -/
theorem table2023 : (List.range 9).map (fun k => divR .halfUp (childCoefAt yp2023 k * yp2023.coefBase) 10) =
    [23227, 33181, 46453, 63044, 82953, 106179, 132724, 162587, 195768] ∧ dependantAmountY yp2023 = 23227 := by decide
/-- The 2024 table (NN 114/23): 280 / 392 / 560 / 784 / 1064 / 1400 / 1792 / 2240 / 2744 €. -/
theorem table2024 : (List.range 9).map (fun k => divR .halfUp (childCoefAt yp2024 k * yp2024.coefBase) 10) =
    [28000, 39200, 56000, 78400, 106400, 140000, 179200, 224000, 274400] := by decide

end HrTax
