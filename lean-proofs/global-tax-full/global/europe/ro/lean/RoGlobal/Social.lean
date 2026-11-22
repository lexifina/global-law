import RoGlobal.Pit

/-!
# RO 2025: employer social contributions (2200) and payroll taxes (3000)

Source: Legea 227/2015 privind Codul fiscal, legislatie.just.ro (official) as captured by the Internet Archive on 2025-05-02 (`ro/law/cf_wb20250502.html`).
* art. 220^3 (1): "Cota contribuției asiguratorii pentru muncă este de 2,25%."; art. 220^2 (1): due on "veniturile din salarii și asimilate salariilor" paid by the employers of art. 220^1 lit. a)
* CAM is the only employer contribution on wages in the Code's Titlul V; CAS and CASS (Capitolele II, III) are employee contributions (2100), outside this family
-/

namespace RoGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Contribuția asiguratorie pentru muncă", sched := Schedule.flat 225, ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "Codul fiscal art. 220^3 (1): 2,25 %")]

/-- On the household's wages: each adult, each contribution (borne by the employer). -/
def householdCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>
    contribs.map fun (c, o, st) =>
      charge o c.name a.wages id (fun x => c.amount x) (event := s!"adult {i + 1}") (level := .social)
        (bearer := .employer) (statute := st)

/-- On a company's payroll, spread evenly over its employees (ceilings per employee). -/
def companyCharges (g : CanonGlobal) : List Charge :=
  if g.entity != .company || g.company.payroll ≤ 0 then [] else
  let n : Int := max 1 (g.company.employees : Int)
  let avg := g.company.payroll / n
  contribs.map fun (c, o, st) =>
    charge o c.name g.company.payroll id (fun _ => n * c.amount avg) (event := "payroll") (level := .social)
      (statute := st)

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "2200/3000 employer contributions", covers := [.sscEmployer],
     run := fun args g prev =>
       householdCharges g ++ companyCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["RO 2200/3000: legislatie.just.ro via Internet Archive 2025-05-02"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 1125
#guard c0.amount 200000 == 4500

end RoGlobal.Social
