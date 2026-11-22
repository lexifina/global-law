import UkGlobal.Pit

/-!
# UK 2025: employer social contributions (2200) and payroll taxes (3000)

Source: legislation.gov.uk point in time 2025-07-01: SSCBA 1992 s. 9 (`uk/law/sscba_s9_2025-07-01.html`), Social Security (Contributions) Regulations 2001 reg. 10 (`uk/law/ssc2001_reg10_2025-07-01.html`).
* SSCBA s. 9 (2): "the secondary percentage is [15%]"
* reg. 10 (d): "the secondary threshold (for secondary Class 1 contributions) shall be [£96]" a week: 52 × £96 = £4 992 a year for evenly paid weekly earnings
-/

namespace UkGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Secondary Class 1 NICs", sched := Schedule.ofList [(0, 0), (4992, 1500)], ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "SSCBA 1992 s. 9 (2): secondary percentage 15%; SI 2001/1004 reg. 10 (d): secondary threshold £96 a week")]

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

def notes : List String := ["UK 2200/3000: legislation.gov.uk 2025-07-01"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .household then ["employment allowance, under-21 and apprentice zero rates not modelled; annual threshold taken as 52 weeks"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 4000 == 0
#guard c0.amount 50000 == 6751

end UkGlobal.Social
