import EsGlobal.Pit

/-!
# ES 2025: employer social contributions (2200) and payroll taxes (3000)

Source: the dated statute quotes carried by the 1.x model's parameters (`lean/ESTax/Params.lean`, vendored, sha256 in VENDORED.sha256): Orden PJC/178/2025 (cotización 2025).
* ESTax.Params `ssEmployer`: "Employer shares ...: CC 23,60 %, desempleo 5,50 %, FP 0,60 %, MEI 0,67 % (same Orden)"
* `baseMaxima`: Orden PJC/178/2025 arts. 1-2 "tope máximo 4.909,50 euros mensuales" (annual 58 914 €)
-/

namespace EsGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Contingencias comunes (empresa)", sched := Schedule.flat 2360, ceiling := 58914 }
def c1 : Contribution := { name := "Desempleo (empresa)", sched := Schedule.flat 550, ceiling := 58914 }
def c2 : Contribution := { name := "Formación profesional (empresa)", sched := Schedule.flat 60, ceiling := 58914 }
def c3 : Contribution := { name := "MEI (empresa)", sched := Schedule.flat 67, ceiling := 58914 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "Orden PJC/178/2025: CC 23,60 % empresa; tope 4.909,50 €/mes"),
   (c1, .sscEmployer, "Orden PJC/178/2025: desempleo 5,50 % empresa"),
   (c2, .sscEmployer, "Orden PJC/178/2025: FP 0,60 % empresa"),
   (c3, .sscEmployer, "Orden PJC/178/2025 art. 17 bis: MEI 0,67 % empresa")]

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

def notes : List String := ["ES 2200/3000: Orden PJC/178/2025 (2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .household then ["accidentes de trabajo (tarifa by activity), FOGASA 0,20 % and the base mínima not modelled; monthly tope taken as 12 × 4 909,50 €"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 11800
#guard c0.amount 200000 == 13903
#guard c1.amount 50000 == 2750
#guard c1.amount 200000 == 3240
#guard c2.amount 50000 == 300
#guard c2.amount 200000 == 353
#guard c3.amount 50000 == 335
#guard c3.amount 200000 == 394

end EsGlobal.Social
