import SkGlobal.Pit

/-!
# SK 2025: employer social contributions (2200) and payroll taxes (3000)

Source: Slov-Lex (official), versions effective 2025-01-01: zákon 461/2003 Z. z. o sociálnom poistení (`sk/law/z461_2003_20250101.html`), zákon 580/2004 Z. z. o zdravotnom poistení (`sk/law/z580_2004_20250101.html`).
* § 130: "Sadzba poistného na nemocenské poistenie je pre ... b) zamestnávateľa 1,4 % z vymeriavacieho základu"; § 131 (1): "b) zamestnávateľa za zamestnanca 14 %"; § 132: "b) zamestnávateľa 3 %"
* § 133: "Sadzba poistného na úrazové poistenie pre zamestnávateľa je 0,8 %"; § 135: garančné "0,25 %"; § 136 b) 1.: zamestnávateľ, ktorý platí poistné na financovanie podpory, "0,5 %"; § 136a: "0,5 %"; § 137 a): "zamestnávateľa 4,75 %"
* zákon 580/2004 § 12 (1): "d) zamestnávateľa 10 % z vymeriavacieho základu"
-/

namespace SkGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Nemocenské poistenie (zamestnávateľ)", sched := Schedule.flat 140, ceiling := -1 }
def c1 : Contribution := { name := "Starobné poistenie (zamestnávateľ)", sched := Schedule.flat 1400, ceiling := -1 }
def c2 : Contribution := { name := "Invalidné poistenie (zamestnávateľ)", sched := Schedule.flat 300, ceiling := -1 }
def c3 : Contribution := { name := "Úrazové poistenie", sched := Schedule.flat 80, ceiling := -1 }
def c4 : Contribution := { name := "Garančné poistenie", sched := Schedule.flat 25, ceiling := -1 }
def c5 : Contribution := { name := "Poistenie v nezamestnanosti (zamestnávateľ)", sched := Schedule.flat 50, ceiling := -1 }
def c6 : Contribution := { name := "Poistné na financovanie podpory", sched := Schedule.flat 50, ceiling := -1 }
def c7 : Contribution := { name := "Rezervný fond solidarity (zamestnávateľ)", sched := Schedule.flat 475, ceiling := -1 }
def c8 : Contribution := { name := "Zdravotné poistenie (zamestnávateľ)", sched := Schedule.flat 1000, ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "zákon 461/2003 Z. z. § 130 písm. b): 1,4 %"),
   (c1, .sscEmployer, "zákon 461/2003 Z. z. § 131 ods. 1 písm. b): 14 %"),
   (c2, .sscEmployer, "zákon 461/2003 Z. z. § 132 písm. b): 3 %"),
   (c3, .sscEmployer, "zákon 461/2003 Z. z. § 133: 0,8 %"),
   (c4, .sscEmployer, "zákon 461/2003 Z. z. § 135: 0,25 %"),
   (c5, .sscEmployer, "zákon 461/2003 Z. z. § 136 písm. b) bod 1: 0,5 %"),
   (c6, .sscEmployer, "zákon 461/2003 Z. z. § 136a: 0,5 %"),
   (c7, .sscEmployer, "zákon 461/2003 Z. z. § 137 písm. a): 4,75 %"),
   (c8, .sscEmployer, "zákon 580/2004 Z. z. § 12 ods. 1 písm. d): 10 %")]

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

def notes : List String := ["SK 2200/3000: Slov-Lex znenie účinné od 1.1.2025"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 150000 < a.wages) then ["maximum assessment base for social insurance (§ 138: a multiple of the všeobecný vymeriavací základ, the 2023 figure not read) not applied; úrazové and health have none"] else [])
  ++ (if g.household.adults.any (fun a => 0 < a.wages) then ["reduced health rate for employees with disabilities (5 %) not modelled"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 700
#guard c0.amount 200000 == 2800
#guard c1.amount 50000 == 7000
#guard c1.amount 200000 == 28000
#guard c2.amount 50000 == 1500
#guard c2.amount 200000 == 6000
#guard c3.amount 50000 == 400
#guard c3.amount 200000 == 1600
#guard c4.amount 50000 == 125
#guard c4.amount 200000 == 500
#guard c5.amount 50000 == 250
#guard c5.amount 200000 == 1000
#guard c6.amount 50000 == 250
#guard c6.amount 200000 == 1000
#guard c7.amount 50000 == 2375
#guard c7.amount 200000 == 9500
#guard c8.amount 50000 == 5000
#guard c8.amount 200000 == 20000

end SkGlobal.Social
