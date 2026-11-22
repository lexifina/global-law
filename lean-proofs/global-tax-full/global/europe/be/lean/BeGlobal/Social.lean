import BeGlobal.Pit

/-!
# BE 2025: employer social contributions (2200) and payroll taxes (3000)

Source: ONSS (Office national de sécurité sociale), instructions administratives DmfA 2025/1, "Les cotisations ordinaires" (official administrative instructions, socialsecurity.be, `be/law/onss_ordinarycontributions_2025-1.html`).
* "Le pourcentage de cotisation applicable est diminué pour ces travailleurs de 22,65 % à 19,88 % à partir du 1 er trimestre 2018." (catégories 1 et 3 de la réduction structurelle)
* "La cotisation de modération salariale ... s'élève à 5,67 % de la rémunération du travailleur, augmentée de 5,67 % des cotisations patronales dues."; "Le pourcentage de modération salariale applicable pour ces travailleurs est diminué de 5,67 % à 4,27 % à partir du 1 er trimestre 2018."
-/

namespace BeGlobal.Social
open TaxKernel TaxKernel.Global

/-- ONSS, private sector, structural-reduction category 1 (employés, 100 % pay): basic employer contribution 19,88 %
of the gross pay; wage moderation "5,67 % de la rémunération du travailleur, augmentée de 5,67 % des cotisations
patronales dues", lowered to 4,27 % for categories 1 and 3 from 2018: 4,27 % × (pay + 19,88 % of pay). -/
def onssBase (w : Int) : Int := w * 1988 / 10000
def onssModeration (w : Int) : Int := w * 11988 * 427 / 100000000

def contribs : List (String × (Int → Int) × Oecd × String) :=
  [("Cotisation patronale de base (secteur privé, catégorie 1)", onssBase, .sscEmployer, "ONSS instructions 2025/1: cotisation patronale de base 19,88 % (catégories 1 et 3 de la réduction structurelle, from 2018: loi 26.12.2015, loi 16.5.2016)"),
   ("Cotisation de modération salariale", onssModeration, .sscEmployer, "ONSS instructions 2025/1: 4,27 % de la rémunération augmentée de 4,27 % des cotisations patronales dues (catégorie 1)")]

/-- On the household's wages: each adult, each contribution (borne by the employer). -/
def householdCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>
    contribs.map fun (nm, f, o, st) =>
      charge o nm a.wages id (fun x => f x) (event := s!"adult {i + 1}") (level := .social)
        (bearer := .employer) (statute := st)

/-- On a company's payroll, spread evenly over its employees. -/
def companyCharges (g : CanonGlobal) : List Charge :=
  if g.entity != .company || g.company.payroll ≤ 0 then [] else
  let n : Int := max 1 (g.company.employees : Int)
  let avg := g.company.payroll / n
  contribs.map fun (nm, f, o, st) =>
    charge o nm g.company.payroll id (fun _ => n * f avg) (event := "payroll") (level := .social)
      (statute := st)

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "2200/3000 employer contributions", covers := [.sscEmployer],
     run := fun args g prev =>
       householdCharges g ++ companyCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["BE 2200/3000: ONSS instructions, quarter 2025/1"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["employés (pay at 100 %) taken: manual workers' 108 % base and holiday-pay contributions (5,57 % + 10,27 %), the réduction structurelle on low pay, the fonds amiante (0,01 %), accidents du travail (0,02 %), Fonds de fermeture and the 1,60 % sector contributions not modelled"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees"] else [])

#guard onssBase 50000 == 9940
#guard onssBase 200000 == 39760
#guard onssModeration 50000 == 2559
#guard onssModeration 200000 == 10237

end BeGlobal.Social
