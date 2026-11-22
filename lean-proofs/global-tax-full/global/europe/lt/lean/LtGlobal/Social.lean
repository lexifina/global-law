import LtGlobal.Pit

/-!
# LT 2025: employer social contributions (2200) and payroll taxes (3000)

Source: VSDFV (Sodra), "Įmokų tarifai, taikomi už samdomus darbuotojus", sodra.lt as captured by the Internet Archive on 2026-10-09 (`cmp20/baltic/lt/refs/sodra_samdomi_wb.html`, kept by the 1.x model): section "Kokios yra socialinio draudimo rūšys ir kokie tarifai yra taikomi 2025 m.?".
* "Darbdavio įmokos Nedarbo socialinis draudimas: Neterminuota darbo sutartis – 1,31 proc. Terminuota darbo sutartis – 2,03 proc."
* "Nelaimingų atsitikimų ir profesinių ligų socialinis draudimas 2025 m.: ... Įprastai įmonė priklauso pirmajai draudėjų grupei. I grupė – 0,14 proc."
* "Įmoka į Garantinį fondą 0,16 proc. nuo asmeniui priskaičiuoto darbo užmokesčio." "Įmokas į Ilgalaikio darbo išmokų fondą 0,16 proc. nuo asmeniui priskaičiuoto darbo užmokesčio"
-/

namespace LtGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Nedarbo socialinis draudimas (darbdavys)", sched := Schedule.flat 131, ceiling := -1 }
def c1 : Contribution := { name := "Nelaimingų atsitikimų ir profesinių ligų socialinis draudimas", sched := Schedule.flat 14, ceiling := -1 }
def c2 : Contribution := { name := "Įmoka į Garantinį fondą", sched := Schedule.flat 16, ceiling := -1 }
def c3 : Contribution := { name := "Įmoka į Ilgalaikio darbo išmokų fondą", sched := Schedule.flat 16, ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "Sodra įmokų tarifai 2025: neterminuota darbo sutartis 1,31 proc."),
   (c1, .sscEmployer, "Sodra įmokų tarifai 2025: I grupė 0,14 proc. (NAPLSDĮ 29 str. 3 d.)"),
   (c2, .sscEmployer, "Sodra įmokų tarifai 2025: 0,16 proc."),
   (c3, .sscEmployer, "Sodra įmokų tarifai 2025: 0,16 proc.")]

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

def notes : List String := ["LT 2200/3000: Sodra page, 2025 section (Internet Archive 2026-10-09)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["fixed-term contracts (2,03 %), accident groups II-IV, the 60-average-wage ceiling and the minimum-wage floor of the long-term fund not modelled; indefinite contract and group I taken"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 655
#guard c0.amount 200000 == 2620
#guard c1.amount 50000 == 70
#guard c1.amount 200000 == 280
#guard c2.amount 50000 == 80
#guard c2.amount 200000 == 320
#guard c3.amount 50000 == 80
#guard c3.amount 200000 == 320

end LtGlobal.Social
