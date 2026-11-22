import PtGlobal.Pit

/-!
# PT 2025: employer social contributions (2200) and payroll taxes (3000)

Source: the dated statute quotes carried by the 1.x model's parameters (`lean/PTTax/Params.lean`, vendored, sha256 in VENDORED.sha256) (`cmp20/continental/pt/lean/PTTax/Params.lean`, Segurança Social section).
* PTTax.Params `tsuEmployee`: Código dos Regimes Contributivos art. 53.º: "cabendo 23,75 % à entidade empregadora e 11 % ao trabalhador"
-/

namespace PtGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Taxa social única (entidade empregadora)", sched := Schedule.flat 2375, ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "Código dos Regimes Contributivos do Sistema Previdencial de Segurança Social (Lei 110/2009) art. 53.º: 23,75 % entidade empregadora")]

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

def notes : List String := ["PT 2200/3000: Código dos Regimes Contributivos as in force in 2025 (via the 1.x model)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["reduced employer rates (art. 55 ff.: non-profit entities, first-job and long-term-unemployed exemptions) and the Fundo de Compensação do Trabalho not modelled"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 11875
#guard c0.amount 200000 == 47500

end PtGlobal.Social
