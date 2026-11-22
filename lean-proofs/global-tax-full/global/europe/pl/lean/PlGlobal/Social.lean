import PlGlobal.Pit

/-!
# PL 2025: employer social contributions (2200) and payroll taxes (3000)

Source: Dz.U. 2025 poz. 350 (tekst jednolity ustawy z 13.10.1998 o systemie ubezpieczeń społecznych, api.sejm.gov.pl ELI PDF, `pl/law/sus_tj2025.pdf`) and M.P. 2024 poz. 1051 (`pl/law/mp2024_1051_ograniczenie.pdf`).
* art. 22 ust. 1: "1) 19,52 % podstawy wymiaru – na ubezpieczenie emerytalne ...; 2) 8,00 % podstawy wymiaru – na ubezpieczenia rentowe; 3) 2,45 % podstawy wymiaru – na ubezpieczenie chorobowe; 4) od 0,40 % do 8,12 % podstawy wymiaru – na ubezpieczenie wypadkowe"
* art. 16 ust. 1: emerytalne "finansują z własnych środków, w równych częściach, ubezpieczeni i płatnicy składek"; ust. 1b: rentowe "w wysokości 1,5 % podstawy wymiaru ubezpieczeni i w wysokości 6,5 % podstawy wymiaru płatnicy składek"
* M.P. 2024 poz. 1051: "kwota ograniczenia rocznej podstawy wymiaru składek na ubezpieczenia emerytalne i rentowe w roku 2025 wynosi 260 190 zł"
-/

namespace PlGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Składka na ubezpieczenie emerytalne (płatnik)", sched := Schedule.flat 976, ceiling := 260190 }
def c1 : Contribution := { name := "Składka na ubezpieczenia rentowe (płatnik)", sched := Schedule.flat 650, ceiling := 260190 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "ustawa o systemie ubezpieczeń społecznych art. 22 ust. 1 pkt 1 (19,52 %), art. 16 ust. 1 (w równych częściach), art. 19 ust. 1; M.P. 2024 poz. 1051: 260 190 zł"),
   (c1, .sscEmployer, "ustawa o systemie ubezpieczeń społecznych art. 22 ust. 1 pkt 2 (8,00 %), art. 16 ust. 1b (6,5 % płatnicy), art. 19 ust. 1; M.P. 2024 poz. 1051")]

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

def notes : List String := ["PL 2200/3000: Dz.U. 2025 poz. 350 (tekst jednolity of 14.2.2025); M.P. 2024 poz. 1051"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["ubezpieczenie wypadkowe (0,40-8,12 %, by the payer's risk category), Fundusz Pracy (2,45 %), FGŚP (0,10 %) and FEP not modelled (their acts not read)"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 4880
#guard c0.amount 200000 == 19520
#guard c1.amount 50000 == 3250
#guard c1.amount 200000 == 13000

end PlGlobal.Social
