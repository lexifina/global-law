import EeGlobal.Pit

/-!
# EE 2025: employer social contributions (2200) and payroll taxes (3000)

Source: the dated statute quotes carried by the 1.x model's parameters (`lean/EeTax/Params.lean`, vendored, sha256 in VENDORED.sha256).
* EeTax.Params `socialTax`: SMS § 7(1) "Sotsiaalmaksu määr on 33 protsenti maksustatavalt summalt"
* `uiEmployer`: "Tööandja töötuskindlustusmakse määr … on 0,8 protsenti"
-/

namespace EeGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Sotsiaalmaks", sched := Schedule.flat 3300, ceiling := -1 }
def c1 : Contribution := { name := "Töötuskindlustusmakse (tööandja)", sched := Schedule.flat 80, ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "Sotsiaalmaksuseadus § 7 (1): 33 %"),
   (c1, .sscEmployer, "TKindlS § 41; RT I 24.09.2024, 4 § 1 (2): 0,8 %")]

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

def notes : List String := ["EE 2200/3000: 2025 (via the 1.x model)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["social tax minimum monthly obligation (SMS § 2^1) not modelled"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 16500
#guard c0.amount 200000 == 66000
#guard c1.amount 50000 == 400
#guard c1.amount 200000 == 1600

end EeGlobal.Social
