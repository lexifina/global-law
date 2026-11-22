import CrTax.Params

/-!
# Costa Rica 2025: schedular income tax of an individual

Costa Rica taxes by category (Ley 7092 Título I utilidades, Título II salarios, Capítulo XI rentas y ganancias de
capital) with no annual global return for the categories modelled here (kernel `Cedula`, no overlay), on a territorial
basis (art. 1: "rentas ... de fuente costarricense"; optional input `foreignIncome` is excluded, kernel `sourceBase`).

* Salary tax (art. 32-35), monthly, on each of 12 monthly salaries `s`; the year's pay is taken to include the
  statutory aguinaldo (Ley 2412), `wages = 13 s`, the 13th payment exempt (art. 35 b). Option `--no-aguinaldo`:
  `wages = 12 s` (convention; see conventions.json). Credits per child (minors) and for the spouse, monthly,
  non-refundable, each claimed by one spouse (art. 34: "cada hijo sólo podrá ser deducido por uno de ellos"; the
  spouse credit "sólo podrá ser deducido, en su totalidad, por uno de ellos"): the model gives them to the spouse with
  the larger salary.
* Pensions (art. 32 ch): the same monthly scale, applied by the paying entity separately (reading: no aggregation
  with a salary from another payer; the statute has no annual reconciliation for the salary tax).
* Self-employment (art. 15 c): annual scale with the art. 15 c credits, which are not available to someone who used
  the art. 34 credits (art. 34 last paragraph).
* Capital (art. 29, 29 bis, 31 ter): 15 % on interest and dividends (gross), on capital gains, and on 85 % of rent.
* Employee contributions (CCSS): health 5,50 %, IVM 4,17 %, Banco Popular 1 % on the 12 salaries (the aguinaldo is
  "un aguinaldo y no ... un salario", Ley 2412 considerando 7°); pensioners 5 % health.
-/

namespace CrTax
open TaxKernel

/-- Monthly salary from the annual wage. -/
def monthlySalary (aguinaldo : Bool) (w : Int) : Int := if aguinaldo then w / paymentsWithAguinaldo else w / 12

/-- Salary tax for a month, before credits (colones, half-up: reading). -/
def salaryTaxMonth (s : Int) : Int := salaryScale.tax Rule.unitHalfUp s

structure Person where
  salary : Int := 0          -- monthly salary
  salaryTax : Int := 0       -- year, after credits
  pensionTax : Int := 0
  profitTax : Int := 0
  capitalTax : Int := 0
  social : Int := 0
  creditsUsed : Int := 0
  deriving Repr

def ivm (x : Int) : Int := divR .halfUp (x * rateIVMcBp) (BP * 100)

def person (aguinaldo : Bool) (wage pension se interest dividends gains rent : Int) (kids : Nat) (spouse : Bool) :
    Person :=
  let s := monthlySalary aguinaldo (pos wage)
  let credM := (kids : Int) * creditChildMonth + (if spouse then creditSpouseMonth else 0)
  let tM := salaryTaxMonth s
  let usesArt34 := wage > 0 && credM > 0
  let salaryTax := 12 * pos (tM - credM)
  let used := 12 * min tM credM
  let pm := pos pension / 12
  let pensionTax := 12 * salaryTaxMonth pm
  let profit0 := profitScale.tax Rule.unitHalfUp (pos se)
  let credY := if usesArt34 || se ≤ 0 then 0 else (kids : Int) * creditChildYear + (if spouse then creditSpouseYear else 0)
  let profitTax := pos (profit0 - credY)
  let capBase := pos interest + pos dividends + pos gains + (pos rent - divR .down (pos rent * rentLumpRate) BP)
  let capitalTax := divR .halfUp (capBase * capitalRate) BP
  let sal12 := 12 * s
  let social := divR .halfUp (sal12 * rateSEM) BP + ivm sal12 + divR .halfUp (sal12 * rateBP) BP +
    divR .halfUp (pos pension * rateSEMPension) BP
  { salary := s, salaryTax, pensionTax, profitTax, capitalTax, social, creditsUsed := used + min profit0 credY }

def out (args : List String) (c : Canon) : Out :=
  let aguinaldo := !(args.contains "--no-aguinaldo" || (c.bool? "noAguinaldo").getD false)
  let n := c.adults.length
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  let kids := c.childrenUnder 18
  let claimant : Nat := match c.adults with
    | [a, b] => if b.wages > a.wages then 1 else 0
    | _ => 0
  let rows := ((((c.adults.zip (sh c.interest)).zip (sh c.dividends)).zip (sh c.capitalGains)).zip (sh c.rentalIncome))
  let ps := rows.zipIdx.map fun (((((a, i), d), g), r), k) =>
    person aguinaldo a.wages a.pension a.selfEmployment i d g r (if k == claimant then kids else 0)
      (k == claimant && c.married && n == 2)
  let cedulas : List Cedula :=
    [⟨"salary", 0, fun _ => sumInts (ps.map (·.salaryTax))⟩, ⟨"pension", 0, fun _ => sumInts (ps.map (·.pensionTax))⟩,
     ⟨"profits", 0, fun _ => sumInts (ps.map (·.profitTax))⟩, ⟨"capital", 0, fun _ => sumInts (ps.map (·.capitalTax))⟩]
  let unsup :=
    (if c.foreignIncome != 0 then ["foreignIncome: not taxed (territorial source, Ley 7092 art. 1); excluded"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: taken as renta imponible (art. 15 c); CCSS contributions of independents (scale set by the Junta Directiva) not modelled"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: 15 % on the gain (art. 31 ter); the 2,25 % option on assets held before the chapter took effect and the art. 28 bis exemptions not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pension: each payer applies the monthly scale separately (reading); special-regime pension contributions not modelled"] else []) ++
    (if c.charitable != 0 || c.pensionContributions != 0 then ["charitable/pensionContributions: not modelled"] else [])
  Out.make c "CR" "CRC" (cedularTotal cedulas) (employeeSocial := sumInts (ps.map (·.social)))
    (detail := (cedularDetail cedulas).map (fun (k, v) => Out.d (k ++ "Tax") v) ++
               [Out.d "monthlySalary" (sumInts (ps.map (·.salary))), Out.d "creditsUsed" (sumInts (ps.map (·.creditsUsed))),
                Out.dBool "aguinaldoIncluded" aguinaldo,
                Out.d "taxableIncome" (sumInts (ps.map fun p => 12 * p.salary)) ])
    (unsupported := unsup)

def country : Country :=
  { code := "CR", name := "Costa Rica (impuesto al salario, utilidades, rentas de capital)", currency := "CRC",
    year := "2025", compute := out [], computeWith := out }

end CrTax
