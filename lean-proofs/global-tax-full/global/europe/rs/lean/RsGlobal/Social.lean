import RsGlobal.Pit

/-!
# RS 2025: Social family not reached (grade C)

* 2200 Employer social contributions and payroll taxes (Zakon o doprinosima za obavezno socijalno osiguranje (poslodavac)): tried not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts); would unlock: the act's 2025 employer rates and ceilings (official consolidation or the 1.x model's parameters with quotes)


## 2200 Доприноси за обавезно социјално осигурање на терет послодавца (ПИО 10 %, здравство 5,15 %) (gap pass, grade A)
Source: Закон о доприносима за обавезно социјално осигурање ("Службени гласник РС" 84/2004 и измене), official text pravno-informacioni-sistem.rs/reg/viewAct/04455352-c6cf-4ce5-9a7a-2d75505518f5, read in its 2025 versions from the team's git history of Serbian law (lexifina/serbia-law `zakon/2004/84-37/`, commits 604f311423 (version of 1.1.2023, СГ РС 138/2022) and fb33dbb333 (1.2.2025)).
* чл. 44 ст. 2: when contributions are paid both from and on the base: pension and disability 14 % for the insured and "10% за послодавца"; health 5,15 % (each side); unemployment 0,75 % is paid from the base only (employee)
* чл. 13 ст. 1: the base for employees and employers is the wage (зарада)
* чл. 42: the maximum monthly base is five times the average monthly wage, published each year by the minister of finance (the 2025 amount is not in the repository: not applied)
* Hand check: wage 1 200 000 RSD a year: 120 000 + 61 800 = 181 800 RSD (15,15 %)
-/

namespace RsGlobal.Social
open TaxKernel TaxKernel.Global

def gxc0 : Contribution := { name := "Допринос за ПИО на терет послодавца", sched := Schedule.flat 1000 }
def gxc1 : Contribution := { name := "Допринос за здравствено осигурање на терет послодавца", sched := Schedule.flat 515 }

def gxContribs : List (Contribution × Oecd × String) :=
  [(gxc0, .sscEmployer, "Закон о доприносима чл. 44 ст. 2 т. 1 (ред. СГ РС 138/2022): 10 % за послодавца"),  (gxc1, .sscEmployer, "Закон о доприносима чл. 44 ст. 2 т. 2: 5,15 %")]

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

def notes : List String := ["RS 2200 gap pass: Доприноси за обавезно социјално осигурање на терет послодавца (ПИО 10 %, здравство 5,15 %) (A, versions in force in 2025: чл. 44 of 1.1.2023 (unchanged until 2026), чл. 13 of 1.2.2025 (official consolidation, pravno-informacioni-sistem.rs, via lexifina/serbia-law))"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) || (g.entity == .company && g.company.payroll > 0) then ["2200 RS employer contributions: the maximum monthly base (чл. 42, five times the average monthly wage; the 2025 amount was not read) is not applied, so very high wages are overcharged"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["2200 (gap pass): company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard gxc0.amount 100000 == 10000
#guard gxc0.amount 10000000 == 1000000
#guard gxc1.amount 100000 == 5150
#guard gxc1.amount 10000000 == 515000

end RsGlobal.Social
