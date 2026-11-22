import LvGlobal.Pit

/-!
# LV 2025: employer social contributions (2200) and payroll taxes (3000)

Source: the dated statute quotes carried by the 1.x model's parameters (`lean/LvTax/Params.lean`, vendored, sha256 in VENDORED.sha256).
* LvTax.Params: VSAOI 18. panta 1. daļa "34,09 procenti, no kuriem 23,59 procentus maksā darba devējs un 10,50 procentus — darba ņēmējs"
* `maxObject`: "105 300 euro"
-/

namespace LvGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "VSAOI (darba devējs)", sched := Schedule.flat 2359, ceiling := 105300 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "VSAOI likums 18. pants 1. daļa: 23,59 % darba devējs; maksimālais objekts 105 300 euro")]

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

def notes : List String := ["LV 2200/3000: VSAOI likums (2025 redaction, via the 1.x model)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 105300 < a.wages) then ["solidarity tax on wages above 105 300 euro (Solidaritātes nodokļa likums) not modelled"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 11795
#guard c0.amount 200000 == 24840

end LvGlobal.Social
