import AdGlobal.Pit

/-!
# AD 2025: Social family not reached (grade C)

* 2200 Employer social contributions and payroll taxes (Llei 17/2008 de la seguretat social (CASS, empresa)): tried not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts); would unlock: the act's 2025 employer rates and ceilings (official consolidation or the 1.x model's parameters with quotes)


## 2200 Cotitzacions a la CASS a càrrec de l'empresa (6 % + 8,5 %) (gap pass, grade A)
Source: Butlletí Oficial del Principat d'Andorra (BOPA); read from lexifina/andorra-law `lleis/2008-017, lleis/2014-018, lleis/2025-004` (commit 8b4b564, b76bc83, e300169, in force 2008 / 26.8.2014 / 19.2.2025).
* art. 100: general branch, employer 6 %, employee 2 %
* art. 103: pension branch, employer 8,5 %, employee 3,5 %
* no contribution ceiling found; Llei 4/2025 DF3 amends Llei 17/2008 without changing these rates
* Hand check: wages 40 000 EUR: 2 400 + 3 400 = 5 800
-/

namespace AdGlobal.Social
open TaxKernel TaxKernel.Global

def gxc0 : Contribution := { name := "Cotització CASS, branca general (empresa)", sched := Schedule.flat 600 }
def gxc1 : Contribution := { name := "Cotització CASS, branca jubilació (empresa)", sched := Schedule.flat 850 }

def gxContribs : List (Contribution × Oecd × String) :=
  [(gxc0, .sscEmployer, "Llei 17/2008 art. 100 (redacció Llei 18/2014): 6 % a càrrec de l'empresa"),  (gxc1, .sscEmployer, "Llei 17/2008 art. 103 (redacció Llei 18/2014): 8,5 % a càrrec de l'empresa")]

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

def notes : List String := ["AD 2200 gap pass: Cotitzacions a la CASS a càrrec de l'empresa (6 % + 8,5 %) (A, laws as enacted with the amending laws in force in 2025 applied (BOPA via lexifina/andorra-law))"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.payroll > 0 then ["2200 (gap pass): company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard gxc0.amount 40000 == 2400
#guard gxc0.amount 200000 == 12000
#guard gxc1.amount 40000 == 3400
#guard gxc1.amount 200000 == 17000

end AdGlobal.Social
