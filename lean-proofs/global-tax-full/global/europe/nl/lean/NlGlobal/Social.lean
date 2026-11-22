import NlGlobal.Pit

/-!
# NL 2025: employer social contributions (2200) and payroll taxes (3000)

Source: the dated statute quotes carried by the 1.x model's parameters (`lean/NLTax/Params.lean`, vendored, sha256 in VENDORED.sha256) (Belastingdienst rate table for 2025, an official secondary source).
* NLTax.Params: "Zvw inkomensafhankelijke bijdrage 2025: 5,26 % (aanslag / inhouding), werkgeversheffing 6,51 %, maximum" `zvwMax` = € 75.864


FT review (2026-11-21): **Regeling van de Minister van SZW van 19 november 2024** (Stcrt. 2024, 38722; in force
1 January 2025; `nl/law/stcrt-2024-38722.html`): Artikel III "Het bedrag, bedoeld in artikel 17, eerste lid ... van de
Wet financiering sociale verzekeringen, bedraagt voor het jaar 2025 ... € 75.864"; Artikel IV "Het lage
premiepercentage, bedoeld in artikel 27 ... is voor het jaar 2025 2,74%. Het hoge premiepercentage ... 7,74%";
Artikel VI "Het hoge premiepercentage, bedoeld in artikel 36, eerste lid ... 7,64%. Het lage premiepercentage ...
6,28%"; Artikel VII "De premieopslag, bedoeld in artikel 1.10, eerste lid, van de Wet kinderopvang, is voor het jaar
2025 0,50%" ("een opslag op de premie voor het Aof", toelichting). The household's employee is taken on a written
permanent contract (AWf low rate, Wfsv art. 27 (3)) and its employer as not small (Aof high rate, art. 36 (1)); the
sector-differentiated Whk premium and the Ufo (government employers) are not modelled.
-/

namespace NlGlobal.Social
open TaxKernel TaxKernel.Global

def c0 : Contribution := { name := "Werkgeversheffing Zvw", sched := Schedule.flat 651, ceiling := 75864 }

/-- Wfsv art. 27 AWf, low rate (written permanent contract), 2025: 2,74 % (Stcrt. 2024, 38722 art. IV); maximum
premieloon € 75.864 (art. III, Wfsv art. 17 (1)). -/
def c1 : Contribution := { name := "Premie Algemeen Werkloosheidsfonds (laag)", sched := Schedule.flat 274, ceiling := 75864 }
/-- Wfsv art. 36 (1) Aof, high rate, 2025: 7,64 % (art. VI). -/
def c2 : Contribution := { name := "Premie Arbeidsongeschiktheidsfonds (hoog)", sched := Schedule.flat 764, ceiling := 75864 }
/-- Wet kinderopvang art. 1.10 (1): opslag on the Aof premium, 2025: 0,50 % (art. VII). -/
def c3 : Contribution := { name := "Opslag kinderopvangtoeslag (Aof)", sched := Schedule.flat 50, ceiling := 75864 }

def contribs : List (Contribution × Oecd × String) :=
  [(c0, .sscEmployer, "Zvw art. 42-43; 2025: 6,51 %, maximum bijdrage-inkomen € 75.864"),
   (c1, .sscEmployer, "Wfsv art. 27 (1), (3); Stcrt. 2024, 38722 art. IV (2,74 %), art. III (max € 75.864)"),
   (c2, .sscEmployer, "Wfsv art. 36 (1); Stcrt. 2024, 38722 art. VI (7,64 %), art. III"),
   (c3, .sscEmployer, "Wet kinderopvang art. 1.10 (1); Stcrt. 2024, 38722 art. VII (0,50 %), art. III")]

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

def notes : List String := ["NL 2200/3000: 2025 (Belastingdienst table via the 1.x model)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .household then ["werknemersverzekeringen: AWf at the low rate (written permanent contract), Aof at the high rate (employer not small); Whk (sector-differentiated) and Ufo not modelled"] else [])
  ++ (if g.entity == .company && g.company.payroll > 0 then ["company payroll spread evenly over its employees (per-employee ceilings applied to the average wage)"] else [])

#guard c0.amount 50000 == 3255
#guard c0.amount 200000 == 4938
-- Stcrt. 2024, 38722 arts. III, IV, VI, VII
#guard c1.amount 100000 == 2078
#guard c2.amount 100000 == 5796
#guard c3.amount 100000 == 379
#guard c1.amount 50000 == 1370

end NlGlobal.Social
