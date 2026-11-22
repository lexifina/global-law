import HrGlobal.Pit

/-!
# HR 2025: employer social contributions (2200) and payroll taxes (3000)

Source: the dated statute quotes carried by the 1.x model's parameters (`lean/HrTax/Params.lean`, vendored, sha256 in VENDORED.sha256).
* HrTax.Params: "ZD čl. 14 st. 1 t. 1 (NN 106/18 čl. 8): health \"po stopi od 16,5%\" (employer side for employees)"
-/

namespace HrGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Doprinos za zdravstveno osiguranje", sched := Schedule.flat 1650, ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "Zakon o doprinosima čl. 14 st. 1 t. 1: 16,5 %")]

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

def notes : List String := ["HR 2200/3000: 2025 (via the 1.x model)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 8250
#guard c0.amount 200000 == 33000

end HrGlobal.Social
