import AlGlobal.Pit

/-!
# AL 2025: Social family not reached (grade C)

* 2200 Employer social contributions and payroll taxes (Ligji nr. 7703 për sigurimet shoqërore (punëdhënësi)): tried not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts); would unlock: the act's 2025 employer rates and ceilings (official consolidation or the 1.x model's parameters with quotes)


## 2200 Kontributet e punëdhënësit (sigurime shoqërore 15 %, shëndetësore 1,7 %) (gap pass, grade A)
Source: Fletorja Zyrtare / QBZ consolidated text (qbz.gov.al); read from lexifina/albania-law `udhezim/2014/1209-23/pika-010.md` (commit 8c6902f57c, e74b696411, in force 30.12.2024, 2.5.2025).
* pika 10.3: employer social insurance 15 % (sickness 0,18 %, maternity 0,83 %, pension 12,79 %, work accident 0,30 %, unemployment 0,90 %) and employer health insurance 1,7 % without ceiling
* Ligji 7703 neni 10: the base runs from the minimum wage to a maximum set by VKM (the 2025 maximum is not in the repository: not applied)
* Hand check: wages 1 200 000 lekë: 180 000 + 20 400 = 200 400
-/

namespace AlGlobal.Social
open TaxKernel TaxKernel.Global

def gxc0 : Contribution := { name := "Kontributi i sigurimeve shoqërore (punëdhënësi)", sched := Schedule.flat 1500 }
def gxc1 : Contribution := { name := "Kontributi i sigurimit të detyrueshëm të kujdesit shëndetësor (punëdhënësi)", sched := Schedule.flat 170 }

def gxContribs : List (Contribution × Oecd × String) :=
  [(gxc0, .sscEmployer, "Ligji 7703/1993 neni 10; Udhëzimi 23/2014 pika 10.3: punëdhënësi 15 % (sëmundje 0,18, barrë 0,83, pension 12,79, aksident 0,30, papunësi 0,90)"),  (gxc1, .sscEmployer, "Udhëzimi 23/2014 pika 10.3: punëdhënësi 1,7 % (pa tavan)")]

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

def notes : List String := ["AL 2200 gap pass: Kontributet e punëdhënësit (sigurime shoqërore 15 %, shëndetësore 1,7 %) (A, QBZ consolidated versions in force in 2025 (via lexifina/albania-law))"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) || (g.entity == .company && g.company.payroll > 0) then ["2200 AL: the maximum base for the 15 % social insurance contribution (set by VKM; the 2025 amount was not read) is not applied, so high wages are overcharged"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["2200 (gap pass): company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard gxc0.amount 1200000 == 180000
#guard gxc0.amount 10000000 == 1500000
#guard gxc1.amount 1200000 == 20400
#guard gxc1.amount 10000000 == 170000

end AlGlobal.Social
