import ChGlobal.Pit

/-!
# Switzerland 2025, Kanton and Stadt Zürich: Vermögenssteuer and Kapitalsteuer (4200), Erbschafts- und
Schenkungssteuer (4300)

There is no federal wealth or inheritance tax; the reference municipality is the City of Zürich.
Sources: Steuergesetz ZH (LS 631.1), zhlex Nachtrag 127 (pages "1. 1. 25 - 127", `ch/law/stgzh_127.pdf`);
Erbschafts- und Schenkungssteuergesetz ZH (LS 632.1), zhlex Nachtrag 71 (pages "1. 1. 11 - 71", the version still
in force: the zhlex version list shows no later Nachtrag; `ch/law/eschg_zh_071.pdf`); Steuerfüsse 2025 from the ESTV
Steuerrechner TaxRates (FortuneRateCanton 98, FortuneRateCity 119; `ch/law/estv_taxrates_2025_zh8001.json`).
* **StG ZH § 47 (1)** Grundtarif: 0 ‰ for the first Fr. 80 000, ½ ‰ the next 238 000, 1 ‰ 399 000, 1½ ‰ 636 000,
  2 ‰ 956 000, 2½ ‰ 953 000, 3 ‰ above 3 262 000; **(2)** Verheiratetentarif: 159 000, 239 000, 397 000, 637 000,
  955 000, 955 000, above 3 342 000.
* **StG ZH § 82 (1)**: "Die Kapitalsteuer beträgt 0,75 Promille des steuerbaren Eigenkapitals."
* **ESchG § 11**: "Der Ehegatte, der eingetragene Partner und die Nachkommen des Erblassers oder Schenkers sind von der
  Steuerpflicht befreit." **§ 21 (1)**: Fr. 200 000 for a parent, 15 000 for a sibling or grandparent. **§ 22 (1)**
  einfache Steuer 2 % on the first 30 000, 3 % the next 60 000, 4 % 90 000, 5 % 180 000, 6 % 480 000, 7 % 660 000;
  **(2)** above Fr. 1 500 000 "sechs Prozent des Gesamtbetrages". **§ 23 (1)**: parents once, grandparents and
  stepchildren twice, siblings three times, step-parents four times, uncles, aunts and descendants of siblings five
  times, other heirs and non-relatives six times the einfache Steuer.
-/

namespace ChGlobal.Wealth
open TaxKernel TaxKernel.Global

def vermGrund : WealthTax := { name := "Vermögenssteuer Zürich", sched := Schedule.ofList [(0, 0), (80000, 5), (318000, 10), (717000, 15), (1353000, 20), (2309000, 25), (3262000, 30)] }
def vermVerh : WealthTax := { vermGrund with sched := Schedule.ofList [(0, 0), (159000, 5), (398000, 10), (795000, 15), (1432000, 20), (2387000, 25), (3342000, 30)] }
/-- StG ZH § 47 (1) Grundtarif, (2) Verheiratetentarif. -/
def vermTarif (married : Bool) : WealthTax := if married then vermVerh else vermGrund
/-- einfache Steuer x Steuerfuss (percent). -/
def vermSteuer (married : Bool) (pct : Int) (as : List Asset) : Int := divR .down (pct * (vermTarif married).gross as) 100
/-- StG ZH § 82 (1): 0,75 ‰ of the equity, x Steuerfuss. -/
def kapitalsteuer (equity pct : Int) : Int := divR .down (pct * divR .down (75 * pos equity) 100000) 100

def wealthCharges (g : CanonGlobal) : List Charge :=
  if g.entity == .company then
    [charge .wealth "Kapitalsteuer Zürich (Staat)" g.company.equity id (fun e => kapitalsteuer e 98) (level := .state) (statute := "StG ZH § 82 (1) (0,75 ‰); Steuerfuss Kanton 98 % (2025)"),    charge .wealth "Kapitalsteuer Stadt Zürich (Gemeinde)" g.company.equity id (fun e => kapitalsteuer e 119) (level := .local) (statute := "StG ZH § 82 (1) (0,75 ‰); Steuerfuss Stadt Zürich 119 % (2025)")]
  else if g.assets.isEmpty then [] else
    let m := g.household.married
    [charge .wealth "Vermögenssteuer Zürich (Staat)" ((vermTarif m).netWealth g.assets) (fun _ => (vermTarif m).base g.assets) (fun _ => vermSteuer m 98 g.assets)
       (event := "31 December 2025") (level := .state) (statute := "StG ZH § 47 (1)/(2); Steuerfuss Kanton 98 % (2025)"),    charge .wealth "Vermögenssteuer Stadt Zürich (Gemeinde)" ((vermTarif m).netWealth g.assets) (fun _ => (vermTarif m).base g.assets) (fun _ => vermSteuer m 119 g.assets)
       (event := "31 December 2025") (level := .local) (statute := "StG ZH § 47 (1)/(2); Steuerfuss Stadt Zürich 119 % (2025)")]

/-- ESchG § 11, § 21 (1), § 23 (1): (Freibetrag, Faktor); `none` = exempt. Other relatives are taken as "übrige". -/
def eschgClass (r : Relation) : Option (Int × Int) :=
  match r with
  | .spouse | .child | .grandchild | .charity => none
  | .parent => some (200000, 1)
  | .sibling => some (15000, 3)
  | .nieceNephew => some (0, 5)
  | _ => some (0, 6)

/-- ESchG § 22 (1) Grundtarif; (2) 6 % of the whole amount above Fr. 1 500 000. -/
def grundtarif : Schedule := Schedule.ofList [(0, 200), (30000, 300), (90000, 400), (180000, 500), (360000, 600), (840000, 700)]
def einfacheEsch (x : Int) : Int := if x > 1500000 then divR .down (600 * x) BP else grundtarif.tax {} x
def eschgBase (t : Transfer) : Int := match eschgClass t.relation with | none => 0 | some (fb, _) => pos (t.statutoryValue - fb)
def eschgTax (t : Transfer) : Int := match eschgClass t.relation with | none => 0 | some (_, f) => f * einfacheEsch (eschgBase t)

def eschgCharges (g : CanonGlobal) : List Charge :=
  g.transfers.zipIdx.map fun (t, i) =>
    charge .estate (if t.kind == .inheritance then "Erbschaftssteuer Zürich" else "Schenkungssteuer Zürich") t.statutoryValue
      (fun _ => eschgBase t) (fun _ => eschgTax t) (event := s!"{if t.kind == .gift then "gift" else "inheritance"} {i + 1}") (level := .state)
      (statute := "ESchG ZH §§ 11, 21, 22, 23")

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4200 Vermögenssteuer, Kapitalsteuer (Kanton, Stadt Zürich)", covers := [.wealth],
     run := fun args g prev =>
       wealthCharges g },
   { name := "4300 Erbschafts- und Schenkungssteuer (Kanton Zürich)", covers := [.estate],
     run := fun args g prev =>
       eschgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["CH 4200/4300: Kanton and Stadt Zürich (no federal wealth or inheritance tax)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.assets.isEmpty && g.entity != .company then ["Vermögenssteuer: single parents living with children take the Verheiratetentarif (§ 47 (2)): only married couples do here; Kirchensteuer not included; real estate at its Steuerwert only when given"] else [])
  ++ (if g.entity == .company then ["Kapitalsteuer: Kirchensteuer juristischer Personen not included; equity is the line's \"equity\""] else [])
  ++ (if !g.transfers.isEmpty then ["ESchG: aggregation of several transfers from the same donor (§ 21 (3), § 24) and the Lebenspartner/Patenkind Freibeträge not applied; other relatives taxed at the factor 6"] else [])

-- single, shares 1 000 000: ½ ‰ x 238 000 + 1 ‰ x 399 000 + 1½ ‰ x 283 000 = 942,5
#guard vermGrund.gross [{ kind := .listedShares, value := 1000000 }] == 942
#guard vermVerh.gross [{ kind := .listedShares, value := 1000000 }] == 824
#guard vermGrund.gross [{ kind := .listedShares, value := 80000 }] == 0
#guard vermSteuer false 98 [{ kind := .listedShares, value := 1000000 }] == 923
#guard kapitalsteuer 10000000 98 == 7350
#guard kapitalsteuer 10000000 119 == 8925
-- sibling inherits 100 000: (600 + 1 650) x 3
#guard eschgTax { kind := .inheritance, relation := .sibling, value := 100000 } == 6750
#guard eschgTax { kind := .inheritance, relation := .parent, value := 500000 } == 12000
#guard eschgTax { kind := .inheritance, relation := .unrelated, value := 2000000 } == 720000
#guard einfacheEsch 1500000 == 90000
#guard eschgTax { kind := .gift, relation := .child, value := 5000000 } == 0

end ChGlobal.Wealth
