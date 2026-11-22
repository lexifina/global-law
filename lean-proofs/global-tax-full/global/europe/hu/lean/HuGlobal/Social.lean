import HuGlobal.Pit

/-!
# HU 2025: employer social contributions (2200) and payroll taxes (3000)

Source: 2018. évi LII. törvény a szociális hozzájárulási adóról, net.jogtar.hu (Wolters Kluwer, private publisher of the consolidated text; the same route as the VAT act), `hu/law/szocho.html`.
* 2. § (1): "Az adó mértéke az adóalap 13 százaléka, az 1. § (4) bekezdésben foglalt esetekben a juttatások adóalapként meghatározott összegének 13 százaléka."
-/

namespace HuGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Szociális hozzájárulási adó", sched := Schedule.flat 1300, ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "2018. évi LII. törvény 2. § (1): az adóalap 13 százaléka")]

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

def notes : List String := ["HU 2200/3000: consolidated text (jogtar), current at fetch (2026-11); the 2025 wording not separately dated"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["the employer's allowances (szocho kedvezmények) not modelled"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 6500
#guard c0.amount 200000 == 26000

end HuGlobal.Social
