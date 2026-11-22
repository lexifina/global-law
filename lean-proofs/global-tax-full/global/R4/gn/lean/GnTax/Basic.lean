import GnTax.Params

/-!
# Guinea 2025: impôt sur les traitements et salaires (ITS), impôt sur les pensions, IRCM

The 2021 code levies the ITS by a final monthly withholding (arts. 61-64) on gross pay less the employee's compulsory
social-insurance and pension contributions (art. 58); pensions bear the same monthly rates (arts. 66-69). There is no
family allowance of any kind and no zero-rated amount besides the first band. W5 pattern A (2026-11-20): the employee CNSS
contribution is 5 % of the monthly wage up to the plafond, deducted under art. 58. Source: the CNSS page "Cotisations
sociales employeurs" (cnss.gov.gn, fetched 2026-11-20; official secondary: the décrets fixing the rates and the
plafond under the Code de sécurité sociale 1994 arts. 32-33, which the CNSS also publishes, were not reached): "Le
plafond est de 2 500 000 GNF Le plancher est de 550 000 GNF ... Il représente 23% du salaire soumis à cotisation ...
Employeur 18% Salarié 5%". The plancher (a positive wage below 550 000 assessed on 550 000) is not applied (the
model's annual wage need not be 12 full months). `"w5Contrib": false` restores the pre-W5 model. The year is twelve
equal months.
-/

namespace GnTax
open TaxKernel

def months : List Int := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
def monthOf (annual : Int) (m : Int) : Int := annual * m / 12 - annual * (m - 1) / 12

def monthTax (g : Int) : Int := divR .down (monthly.ticks (pos g)) BP
def yearTax (x : Int) : Int := sumInts (months.map fun m => monthTax (monthOf x m))

/-- W5 pattern A: CNSS employee 5 % of the month's wage up to the plafond 2 500 000 GNF (CNSS page). -/
def cnssEmpBp : Int := 500
def cnssPlafond : Int := 2500000
def cnssMonth (g : Int) : Int := divR .down (min (pos g) cnssPlafond * cnssEmpBp) BP
def cnssYear (x : Int) : Int := sumInts (months.map fun m => cnssMonth (monthOf x m))
/-- Art. 58: the ITS base is the month's pay less the employee's compulsory contributions. -/
def yearTaxNet (x : Int) : Int := sumInts (months.map fun m => monthTax (monthOf x m - cnssMonth (monthOf x m)))
/- CNSS page: 23 % = 18 % + 5 %; at or above the plafond the employee pays 125 000 a month. -/
#guard 1800 + cnssEmpBp = 2300 ∧ cnssMonth 2500000 = 125000 ∧ cnssMonth 9000000 = 125000 ∧ cnssMonth 1000000 = 50000

def out (c : Canon) : Out :=
  let w5 := (c.bool? "w5Contrib").getD true
  let its := sumInts (c.adults.map fun a => if w5 then yearTaxNet a.wages else yearTax a.wages)
  let es := if w5 then sumInts (c.adults.map fun a => cnssYear a.wages) else 0
  let ipr := sumInts (c.adults.map fun a => yearTax a.pension)
  let ircm := divR .down (pos c.dividends * dividendRate + pos c.interest * interestRate) BP
  let unsup :=
    ["lois de finances 2022-2024 not read for CGI amendments (LF 2025 has none): ITS rates in their 2021 wording",
     (if w5 then "employeeSocial: CNSS employee 5 % up to the 2 500 000 plafond (CNSS page, official secondary), deducted (art. 58); the 550 000 plancher not applied" else "employeeSocial: CNSS employee contributions not modelled (rate not read); the art. 58 deduction is therefore not taken"),
     "interest: taxed at 15 %; interest on savings accounts and term deposits over 3 months is exempt (art. 190 II), not distinguishable"] ++
    (if c.rentalIncome != 0 then ["rentalIncome: impôt sur les revenus fonciers not modelled"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: impôt sur les bénéfices not modelled"] else [])
  Out.make c "GN" "GNF" (its + ipr + ircm) (employeeSocial := es)
    (detail := [Out.d "cnssEmployee" es, Out.d "its" its, Out.d "pensionTax" ipr, Out.d "ircm" ircm,
                Out.d "taxableIncome" (sumInts (c.adults.map fun a => pos a.wages + pos a.pension)),
                Out.dStr "note" "CGI L/2021/032/AN arts. 57-69: final monthly ITS 0/5/8/10/15/20 % (also pensions); IRCM 15 % final (arts. 189-191)"])
    (unsupported := unsup)

def country : Country :=
  { code := "GN", name := "Guinea (ITS, pensions tax, IRCM)", currency := "GNF", year := "2025", compute := out }

end GnTax
