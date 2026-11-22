import MeGlobal.Pit

/-!
# ME 2025: Social family not reached (grade C)

* 2200 Employer social contributions and payroll taxes (Zakon o doprinosima za obavezno socijalno osiguranje (poslodavac)): tried not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts); would unlock: the act's 2025 employer rates and ceilings (official consolidation or the 1.x model's parameters with quotes)


## 2200 Doprinosi na teret poslodavca (nezaposlenost 0,5 %, Fond rada 0,2 %; PIO 0 %) (gap pass, grade A)
Source: Službeni list Crne Gore 94/2024, 145/2021, Zakon o doprinosima, Zakon o Fondu rada (sluzbenilist.me); read from lexifina/montenegro-law `zakon/2024/373700, zakon/2007/334167, zakon/2020/320379` (commit f0da158b4, b826866e0, 7739b2677, in force 1.10.2024 / 2007 / 2020).
* 94/2024 čl. 1: pension and disability insurance "na teret poslodavca 0% i na teret osiguranika 10,0%" (from 1.10.2024)
* Zakon o doprinosima čl. 18: unemployment insurance 0,5 % on the employer (and 0,5 % on the employee)
* Zakon o Fondu rada čl. 14: 0,2 % on the employer; health contribution abolished from 1.1.2022 (145/2021)
* Hand check: wages 24 000 EUR: 120 + 48 = 168
-/

namespace MeGlobal.Social
open TaxKernel TaxKernel.Global

def gxc0 : Contribution := { name := "Doprinos za osiguranje od nezaposlenosti (poslodavac)", sched := Schedule.flat 50 }
def gxc1 : Contribution := { name := "Doprinos za Fond rada (poslodavac)", sched := Schedule.flat 20 }

def gxContribs : List (Contribution × Oecd × String) :=
  [(gxc0, .sscEmployer, "Zakon o doprinosima za obavezno socijalno osiguranje čl. 18: 0,5 % na teret poslodavca"),  (gxc1, .sscEmployer, "Zakon o Fondu rada čl. 14: 0,2 % na teret poslodavca")]

/-- On the household's wages: each adult, each contribution (borne by the employer). -/
def gxHouseholdCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>
    gxContribs.map fun (c, o, st) =>
      charge o c.name a.wages id (fun x => c.amount x) (event := s!"adult {i + 1}") (level := .social)
        (bearer := .employer) (statute := st)

/-- On a company's payroll, spread evenly over its employees (ceilings per employee). -/
def gxCompanyCharges (g : CanonGlobal) : List Charge :=
  if g.entity != .company || g.company.payroll ≤ 0 then [] else
  let n : Int := max 1 (g.company.employees : Int)
  let avg := g.company.payroll / n
  gxContribs.map fun (c, o, st) =>
    charge o c.name g.company.payroll id (fun _ => n * c.amount avg) (event := "payroll") (level := .social)
      (statute := st)

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "2200 employer contributions (gap pass)", covers := [.sscEmployer],
     run := fun args g prev =>
       gxHouseholdCharges g ++ gxCompanyCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["ME 2200 gap pass: Doprinosi na teret poslodavca (nezaposlenost 0,5 %, Fond rada 0,2 %; PIO 0 %) (A, texts in force in 2025: PIO rate of 94/2024 from 1.10.2024; health contribution abolished from 1.1.2022 (145/2021); Sl. list CG via lexifina/montenegro-law)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.payroll > 0 then ["2200 (gap pass): company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard gxc0.amount 24000 == 120
#guard gxc0.amount 100000 == 500
#guard gxc1.amount 24000 == 48
#guard gxc1.amount 100000 == 200

end MeGlobal.Social
