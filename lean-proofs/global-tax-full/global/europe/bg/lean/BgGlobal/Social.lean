import BgGlobal.Pit

/-!
# BG 2025: employer social contributions (2200) and payroll taxes (3000)

Source: the dated statute quotes carried by the 1.x model's parameters (`lean/BgTax/Params.lean`, vendored, sha256 in VENDORED.sha256).
* BgTax.Params `erTotal`: "pension 7.1 + 2 × 0.56 = 8.22 % (КСО чл. 6, ал. 3, т. 9, б. \"б\"), GIM 2.1 %, unemployment 0.6 %, universal fund 2.8 %, work accident 0.4 % ..., health 4.8 % ... → 18.92 %"
* `maxInsurable`: ЗБДОО 2025 чл. 9 "максимален месечен размер на осигурителния доход - 3 750 лв." (Jan-Mar), "4 130 лв." (Apr-Dec): annual 3 × 3 750 + 9 × 4 130 = 48 420
-/

namespace BgGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Осигурителни вноски (работодател)", sched := Schedule.flat 1892, ceiling := 48420 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "КСО чл. 6, ал. 3; ЗБДОО 2025 чл. 9, 14, 15: 18,92 % (lowest work-accident group); max 3 750 / 4 130 лв. a month")]

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

def notes : List String := ["BG 2200/3000: ЗБДОО 2025 (via the 1.x model)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 0 < a.wages) then ["monthly ceilings taken as one annual ceiling (even monthly pay); work-accident rate of the lowest group"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 9161
#guard c0.amount 200000 == 9161

end BgGlobal.Social
