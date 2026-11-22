import CzGlobal.Pit

/-!
# CZ 2025: employer social contributions (2200) and payroll taxes (3000)

Source: the dated statute quotes carried by the 1.x model's parameters (`lean/CzTax/Params.lean`, vendored, sha256 in VENDORED.sha256) (e-Sbírka citations of zákon 589/1992 and 592/1992 as at 2025-07-01).
* CzTax.Params `erSocialRate`: "§ 7 odst. 1 písm. a): employer 24,8 %"
* `healthRate`: ZPVZP § 2 odst. 1 "13,5 % z vyměřovacího základu" (the employer's two thirds, § 9, not quoted)


FT review (2026-11-21): zákon 589/1992 Sb. in the version of July 2025 (zakonyprolidi.cz, Wayback 2025-07-11,
`cz/law/zpsz589_wb.html`): **§ 15a (1)** "Maximálním vyměřovacím základem zaměstnance pro placení pojistného je částka ve
výši čtyřicetiosminásobku průměrné mzdy" (CzTax.Params: 48 x 46 557 = 2 234 736 Kč, ZDP § 21g); **§ 15a (4)** "Do
vyměřovacího základu zaměstnavatele se nezahrnuje částka, která přesahuje maximální vyměřovací základ zaměstnance".
The health premium (zákon 592/1992) has no maximum base.
-/

namespace CzGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Pojistné na sociální zabezpečení (zaměstnavatel)", sched := Schedule.flat 2480, ceiling := 2234736 }
def c1 : Contribution := { name := "Pojistné na zdravotní pojištění (zaměstnavatel, 2/3 z 13,5 %)", sched := Schedule.flat 900, ceiling := -1 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "zákon 589/1992 Sb. § 7 odst. 1 písm. a): 24,8 %"),
   (c1, .sscEmployer, "zákon 592/1992 Sb. § 2 odst. 1 (13,5 %), § 9 (zaměstnavatel 2/3)")]

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

def notes : List String := ["CZ 2200/3000: 2025 (via the 1.x model)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.household.adults.any (fun a => 2000000 < a.wages) then ["maximum assessment base for social insurance (48 × average wage) not applied"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 12400
#guard c0.amount 200000 == 49600
#guard c1.amount 50000 == 4500
#guard c1.amount 200000 == 18000
-- § 15a (1), (4): the employer's premium stops at 48 x 46 557 = 2 234 736 Kč
#guard c0.amount 2234736 == 554214
#guard c0.amount 3000000 == 554214
#guard c1.amount 3000000 == 270000

end CzGlobal.Social
