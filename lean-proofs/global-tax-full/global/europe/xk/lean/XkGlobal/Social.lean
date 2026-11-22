import XkGlobal.Pit

/-!
# XK 2025: Social family not reached (grade C)

* 2200 Employer social contributions and payroll taxes (Ligji për skemat pensionale (kontributi i punëdhënësit 5 %)): tried not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts); would unlock: the act's 2025 employer rates and ceilings (official consolidation or the 1.x model's parameters with quotes)


## 2200 Kontributet pensionale të punëdhënësit (5 %) (gap pass, grade A)
Source: Gazeta Zyrtare e Republikës së Kosovës; read from lexifina/kosovo-law `ligje/04-l-101/neni-006.md` (commit 4ec6ba550c, in force 30.3.2012).
* neni 6.2: the employer pays 5 % of gross wages and the employee 5 %; no ceiling
* health insurance (Ligji 04/L-249 neni 37: 3,5 % employer) applies only from a start act of the Ministry of Health that is not in the repository: not modelled (flagged)
* Hand check: wages 12 000 EUR: 600
-/

namespace XkGlobal.Social
open TaxKernel TaxKernel.Global

def gxc0 : Contribution := { name := "Kontributi pensional i punëdhënësit", sched := Schedule.flat 500 }

def gxContribs : List (Contribution × Oecd × String) :=
  [(gxc0, .sscEmployer, "Ligji nr. 04/L-101 për fondet pensionale neni 6.2: punëdhënësi 5 % (punëmarrësi 5 %)")]

/-- On the household's wages: each adult, each contribution (borne by the employer). -/
def gxHouseholdCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company then [] else
  (g.household.adults.zipIdx.filter (fun (a, _) => 0 < a.wages)).flatMap fun (a, i) =>
    gxContribs.map fun (c, o, st) =>
      charge o c.name a.wages id (fun x => c.amount x) (event := s!"adult {i + 1}") (level := .social)
        (bearer := .employer) (statute := st)

/-- On a company's payroll, spread evenly over its employees (ceilings per employee). -/
def gxCompanyCharges (g : CanonGlobal) : List Charge :=
  if g.entity != .company || g.company.payroll ≤ 0 then [] else
  let n : Int := max 1 (g.company.employees : Int)
  let avg := g.company.payroll / n
  gxContribs.map fun (c, o, st) =>
    charge o c.name g.company.payroll id (fun _ => n * c.amount avg) (event := "payroll") (level := .social)
      (statute := st)

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "2200 employer contributions (gap pass)", covers := [.sscEmployer],
     run := fun args g prev =>
       gxHouseholdCharges g ++ gxCompanyCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["XK 2200 gap pass: Kontributet pensionale të punëdhënësit (5 %) (A, law as enacted, in force 30.3.2012, no amendment of neni 6 in the repository by 2025 (via lexifina/kosovo-law))"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["2200 XK: health insurance contribution of 04/L-249 (3,5 % employer) not modelled (start of collection not read)"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["2200 (gap pass): company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard gxc0.amount 12000 == 600
#guard gxc0.amount 100000 == 5000

end XkGlobal.Social
