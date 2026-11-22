import BaGlobal.Pit

/-!
# BA 2025: Social family not reached (grade C)

* 2200 Employer social contributions and payroll taxes (Zakon o doprinosima FBiH / RS (poslodavac)): tried not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts); would unlock: the act's 2025 employer rates and ceilings (official consolidation or the 1.x model's parameters with quotes)


## 2200 Doprinosi na teret poslodavca (Federacija BiH) (gap pass, grade A)
Source: Službene novine Federacije BiH; read from lexifina/bosnia-federation-law `Zakon o doprinosima 14/08, 33/25` (commit 64b2b89d1f, 1cddf7481e, in force 2008 / 1.7.2025).
* čl. 10 (14/08): employer contributions on wages 6 % pension and disability, 4 % health, 0,5 % unemployment
* 33/25 čl. 4, 7: 2,5 % pension, 2 % health, 0,5 % unemployment; "počet će se primjenjivati od 1. jula 2025"
* Model: wages taken as earned evenly over 2025: (10,5 % + 5 %) / 2 = 7,75 %
* Hand check: wages 24 000 KM: 1 260 (Jan-Jun) + 600 (Jul-Dec) = 1 860
-/

namespace BaGlobal.Social
open TaxKernel TaxKernel.Global

def gxc0 : Contribution := { name := "Doprinosi na plaću (poslodavac, FBiH)", sched := Schedule.flat 775 }

def gxContribs : List (Contribution × Oecd × String) :=
  [(gxc0, .sscEmployer, "Zakon o doprinosima FBiH čl. 10: 10,5 % (PIO 6 + zdravstvo 4 + nezaposlenost 0,5) do 30.6.2025, 5 % (2,5 + 2 + 0,5) od 1.7.2025 (Sl. novine FBiH 33/25 čl. 4, 7): 7,75 % for wages earned evenly over 2025")]

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

def notes : List String := ["BA 2200 gap pass: Doprinosi na teret poslodavca (Federacija BiH) (A, two periods in 2025: to 30.6.2025 (14/08 text) and from 1.7.2025 (33/25); acts as published via lexifina/bosnia-federation-law)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) || (g.entity == .company && g.company.payroll > 0) then ["2200 BA (FBiH): the employer rate fell from 10,5 % to 5 % on 1.7.2025; wages are taken as earned evenly (7,75 % on the year's wages)"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["2200 (gap pass): company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard gxc0.amount 24000 == 1860
#guard gxc0.amount 100000 == 7750

end BaGlobal.Social
