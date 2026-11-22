import SeGlobal.Pit

/-!
# SE 2025: employer social contributions (2200) and payroll taxes (3000)

Source: riksdagen.se (official) as captured by the Internet Archive: socialavgiftslagen 2025-07-10 (`se/law/sal_wb2025b.html`), lag om allmän löneavgift 2024-12-11 (`se/law/alf_wb20241211.html`; the live text, `alf_riksdagen`, shows 12,62 procent from Lag 2025:1360, for 2026).
* 2 kap. 26 §: "Arbetsgivaravgifterna är 19,80 procent av avgiftsunderlaget och utgörs av 1. sjukförsäkringsavgift 3,55 % 2. föräldraförsäkringsavgift 2,60 % 3. ålderspensionsavgift 10,21 % 4. efterlevandepensionsavgift 0,60 % 5. arbetsmarknadsavgift 2,64 % 6. arbetsskadeavgift 0,20 % Lag (2018:2085)"
* Lag om allmän löneavgift 3 §: "Allmän löneavgift tas ut med 11,62 procent av underlaget och tillfaller staten. Lag (2023:749)"
-/

namespace SeGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Arbetsgivaravgifter", sched := Schedule.flat 1980, ceiling := -1 }
def c1 : Contribution := { name := "Allmän löneavgift", sched := Schedule.flat 1162, ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "Socialavgiftslagen (2000:980) 2 kap. 26 §: 19,80 procent (Lag 2018:2085)"),
   (c1, .payroll, "Lag (1994:1920) om allmän löneavgift 3 §: 11,62 procent (Lag 2023:749)")]

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
  [{ name := "2200/3000 employer contributions", covers := [.payroll, .sscEmployer],
     run := fun args g prev =>
       householdCharges g ++ companyCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["SE 2200/3000: riksdagen.se via Internet Archive 2024-12-11 / 2025-07-10"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["persons over 66/67 (only ålderspensionsavgift, 2 kap. 27 §) and the young-person reductions not modelled; adults' ages not used"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 9900
#guard c0.amount 200000 == 39600
#guard c1.amount 50000 == 5810
#guard c1.amount 200000 == 23240

end SeGlobal.Social
