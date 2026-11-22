import FiGlobal.Pit

/-!
# FI 2025: employer social contributions (2200) and payroll taxes (3000)

Source: Eläketurvakeskus (Finnish Centre for Pensions, statutory body), "Lakisääteiset sosiaalivakuutusmaksut Suomessa 2025" (`cmp20/baltic/fi/refs/etk_sosiaalivakuutusmaksut_2025.pdf`, text `etk_2025.txt`, kept by the 1.x model).
* "Työeläkevakuutusmaksu kokonaisuudessaan on keskimäärin 24,85 % työntekijän palkasta. ... Työnantajan osuudeksi työeläkevakuutusmaksusta jää keskimäärin 17,38 %."
* "Vuonna 2025 työnantajan osuus on 0,20 % tai 0,80 % riippuen työantajan koko palkkasummasta."
* "Työnantajan sosiaaliturvamaksu (= sairausvakuutusmaksu) on 1,87 % palkasta."
-/

namespace FiGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Työeläkevakuutusmaksu (työnantajan osuus, keskimäärin)", sched := Schedule.flat 1738, ceiling := -1 }
def c1 : Contribution := { name := "Työnantajan sairausvakuutusmaksu", sched := Schedule.flat 187, ceiling := -1 }
def c2 : Contribution := { name := "Työttömyysvakuutusmaksu (työnantaja)", sched := Schedule.flat 20, ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "TyEL; Eläketurvakeskus 2025: työnantajan osuus keskimäärin 17,38 %"),
   (c1, .sscEmployer, "Sairausvakuutuslaki 18 luku; Eläketurvakeskus 2025: 1,87 % palkasta"),
   (c2, .sscEmployer, "Laki työttömyysetuuksien rahoituksesta; Eläketurvakeskus 2025: 0,20 % (pienempi palkkasumma)")]

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

def notes : List String := ["FI 2200/3000: ETK leaflet for 2025"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["TyEL employer share taken at the 2025 average (it varies by employer size, insurer and the employee's age band); accident and group life insurance (insurer tariffs) not modelled"] else [])
  ++ (if g.entity == .company && g.company.payroll > 2000000 then ["unemployment insurance 0,80 % on the payroll above the threshold (the threshold is not in the leaflet) not modelled: 0,20 % on the whole payroll"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 8690
#guard c0.amount 200000 == 34760
#guard c1.amount 50000 == 935
#guard c1.amount 200000 == 3740
#guard c2.amount 50000 == 100
#guard c2.amount 200000 == 400

end FiGlobal.Social
