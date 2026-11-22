import GrGlobal.Pit

/-!
# GR 2025: employer social contributions (2200) and payroll taxes (3000)

Source: PwC Worldwide Tax Summaries, Greece, Individual - Other taxes (Wayback capture 2025-06-17; `gr/law/pwc_indother_wb2025.txt`), facts only; e-ΕΦΚΑ εγκύκλιος 38/2024 of 24.12.2024 (health branch from 1.1.2025, ν. 5162/2024 art. 12 amending ν. 4387/2016 art. 41 par. 1; read in the reproduction on taxheaven.gr, the e-efka.gov.gr PDF path 404) and εγκύκλιος 40/2024 (`gr/law/efka_egk40_2024.pdf`, the same cut for public-sector staff).
* PwC (facts): from 1 January 2025 employee 13,37 % and employer 21,79 %, total 35,16 %; for 2025 the e-ΕΦΚΑ main-fund contributions stop at a monthly pay of 7 572,62 EUR
* Εγκύκλιος 38/2024 (κοινές επιχειρήσεις, from 1.1.2025): sickness in kind 3,80 % employer / 1,65 % employee, in cash 0,25 % / 0,40 % (a cut of 0,50 point each side, ν. 5162/2024 art. 12)
* Convention (declared): an ordinary private-sector employee (κοινές επιχειρήσεις, not heavy and unhealthy work, not construction); annual pay in 14 instalments (12 months plus the Christmas, Easter and holiday allowances), so the yearly ceiling is 14 x 7 572,62 = 106 016 EUR
-/

namespace GrGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Εισφορές εργοδότη μισθωτών ιδιωτικού τομέα (e-ΕΦΚΑ, ΔΥΠΑ)", sched := Schedule.flat 2179, ceiling := 106016 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "ν. 4387/2016 as amended by ν. 5162/2024 (ΦΕΚ Α' 198/05.12.2024) art. 12: employer 21,79 % from 1.1.2025 (PwC, facts); health branch 3,80 % + 0,25 % employer (e-ΕΦΚΑ εγκύκλιος 38/2024); monthly ceiling 7 572,62 EUR")]

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

def notes : List String := ["GR 2200/3000: PwC capture 2025-06-17 (rates from 1.1.2025); e-ΕΦΚΑ εγκύκλιος 38/2024"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["2200 GR: the employer rate is the 2025 total for ordinary employees (heavy and unhealthy work +3,60 %, construction and other packages not modelled); the ceiling taken over 14 instalments"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 10895
#guard c0.amount 200000 == 23100

end GrGlobal.Social
