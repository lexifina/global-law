import SiGlobal.Pit

/-!
# SI 2025: employer social contributions (2200) and payroll taxes (3000)

Source: Finančna uprava RS (FURS), brochure "Prispevki za socialno varnost" (2025 edition, with the long-term-care contribution from 1 July 2025), `cmp20/central/si/refs/fu_Brosura_prispevki.doc` (kept by the 1.x model), section 2.2 table.
* 2.2 Vrste in stopnje prispevkov (delavci v delovnem razmerju), Stopnja prispevka delodajalca: "za pokojninsko in invalidsko zavarovanje 8,85 %; za zdravstveno zavarovanje 6,56 %; za dolgotrajno oskrbo** 1,00 %; za starševsko varstvo 0,10 %; za primer brezposelnosti 0,06 %; za poškodbe pri delu in poklicne bolezni 0,53 %; Skupaj 17,10 %"
* "**Prispevek se plačuje za obdobje od 1. julija 2025 dalje."
-/

namespace SiGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Prispevek za pokojninsko in invalidsko zavarovanje (delodajalec)", sched := Schedule.flat 885, ceiling := -1 }
def c1 : Contribution := { name := "Prispevek za zdravstveno zavarovanje (delodajalec)", sched := Schedule.flat 656, ceiling := -1 }
def c2 : Contribution := { name := "Prispevek za poškodbe pri delu in poklicne bolezni", sched := Schedule.flat 53, ceiling := -1 }
def c3 : Contribution := { name := "Prispevek za starševsko varstvo (delodajalec)", sched := Schedule.flat 10, ceiling := -1 }
def c4 : Contribution := { name := "Prispevek za primer brezposelnosti (delodajalec)", sched := Schedule.flat 6, ceiling := -1 }
def c5 : Contribution := { name := "Prispevek za dolgotrajno oskrbo (delodajalec, od 1. 7. 2025)", sched := Schedule.flat 50, ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "FURS 2025: 8,85 % (ZPIZ-2)"),
   (c1, .sscEmployer, "FURS 2025: 6,56 % (ZZVZZ)"),
   (c2, .sscEmployer, "FURS 2025: 0,53 % (ZZVZZ)"),
   (c3, .sscEmployer, "FURS 2025: 0,10 %"),
   (c4, .sscEmployer, "FURS 2025: 0,06 %"),
   (c5, .sscEmployer, "ZDOsk-1; FURS 2025: 1,00 % od 1. julija 2025 (6 of 12 months: 0,50 % of the year's pay)")]

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

def notes : List String := ["SI 2200/3000: FURS brochure, 2025 (long-term care from 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["the minimum contribution base (60 % of the average wage) not applied; long-term care taken as 1 % on half the year's pay (evenly paid)"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 4425
#guard c0.amount 200000 == 17700
#guard c1.amount 50000 == 3280
#guard c1.amount 200000 == 13120
#guard c2.amount 50000 == 265
#guard c2.amount 200000 == 1060
#guard c3.amount 50000 == 50
#guard c3.amount 200000 == 200
#guard c4.amount 50000 == 30
#guard c4.amount 200000 == 120
#guard c5.amount 50000 == 250
#guard c5.amount 200000 == 1000

end SiGlobal.Social
