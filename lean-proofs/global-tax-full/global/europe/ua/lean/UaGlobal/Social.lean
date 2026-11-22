import UaGlobal.Pit

/-!
# UA 2025: employer social contributions (2200) and payroll taxes (3000)

Source: the dated statute quotes carried by the 1.x model's parameters (`lean/UaTax/Params.lean`, vendored, sha256 in VENDORED.sha256) (Law 2464-VI archived 2025-03-14).
* UaTax.Basic: "Law 2464-VI on the single contribution (archived 2025-03-14): art. 4(1)(1) payers are the employers; art. 8(5) 22 відсотки of the art. 7 base"
-/

namespace UaGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Єдиний соціальний внесок", sched := Schedule.flat 2200, ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "Закон 2464-VI ст. 8 ч. 5: 22 відсотки")]

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

def notes : List String := ["UA 2200/3000: Law 2464-VI (archived 2025-03-14, via the 1.x model)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["maximum base (art. 7: 20 minimum wages a month) and the minimum contribution not modelled"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 11000
#guard c0.amount 200000 == 44000

end UaGlobal.Social
