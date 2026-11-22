import ChGlobal.Pit

/-!
# CH 2025: employer social contributions (2200) and payroll taxes (3000)

Source: fedlex consolidations kept by the 1.x model (`cmp20/germanic/ch/law/ahvg_2025-01-01.html`, `avig_2025-05-01.html`).
* AHVG Art. 5 / 13: "ein Beitrag von 4,35 Prozent" (employee and employer each)
* AVIG Art. 3 (2): "Bis zum massgebenden, auf den Monat umgerechneten Höchstbetrag des versicherten Verdienstes der obligatorischen Unfallversicherung beträgt der Beitragssatz 2,2 Prozent" (half each; the UVV maximum, 148 200 Fr., not read here)
-/

namespace ChGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "AHV/IV/EO-Beitrag Arbeitgeber (AHV-Teil)", sched := Schedule.flat 435, ceiling := -1 }
def c1 : Contribution := { name := "ALV-Beitrag Arbeitgeber", sched := Schedule.flat 110, ceiling := 148200 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "AHVG Art. 13: 4,35 Prozent"),
   (c1, .sscEmployer, "AVIG Art. 3 (2), Art. 6: 2,2 Prozent je zur Hälfte bis zum Höchstbetrag des versicherten Verdienstes (148 200 Fr.)")]

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

def notes : List String := ["CH 2200/3000: fedlex 2025"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .household then ["IV (0,7 %) and EO (0,25 %) employer shares, FAK (cantonal), BVG and UVG premiums not modelled"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 2175
#guard c0.amount 200000 == 8700
#guard c1.amount 50000 == 550
#guard c1.amount 200000 == 1630

end ChGlobal.Social
