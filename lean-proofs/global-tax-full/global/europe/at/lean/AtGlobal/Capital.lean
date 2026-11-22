import AtGlobal.Pit

/-!
# Austria 2025: gains of individuals (1100): Kapitalvermögen (§ 27 (3), 27,5 %) and private land sales (§§ 30, 30a)

Source: EStG 1988, RIS "Fassung vom 01.07.2025" (`at/law/estg_2025-07-01.html`, sha256 in `law/SHA256SUMS`).
* **§ 27a (1) Z 2**: capital income (including gains on shares and bonds, § 27 (3)) "in allen anderen Fällen einem
  besonderen Steuersatz von 27,5%".
* **§ 30a (1)**: "Einkünfte aus der Veräußerung von Grundstücken im Sinne des § 30 unterliegen einem besonderen
  Steuersatz von 30%". **§ 30 (2) Z 1**: exempt when the dwelling "ab der Anschaffung oder Herstellung (Fertigstellung)
  bis zur Veräußerung für mindestens zwei Jahre durchgehend als Hauptwohnsitz gedient haben" (lit. a) or "innerhalb der
  letzten zehn Jahre vor der Veräußerung mindestens fünf Jahre" (lit. b). **§ 30 (4)**: for land not taxable on 31
  March 2012 (acquired before 1 April 2002, "Altvermögen"), "In allen übrigen Fällen der Unterschiedsbetrag zwischen dem
  Veräußerungserlös und den mit 86% des Veräußerungserlöses anzusetzenden Anschaffungskosten" (14 % of the proceeds).
The disposals are extra events (the 1.x household's own `capitalGains` is taxed by the 1.x model); losses are netted
within each class (§ 27 (8), § 30 (7) read as structure only), never below zero.
-/

namespace AtGlobal.Capital
open TaxKernel TaxKernel.Global

def isKapital (d : Disposal) : Bool := d.kind.isShares || d.kind == .bonds

/-- § 30 (2) Z 1 lit. a: a main home used as such for at least two years since acquisition. -/
def hauptwohnsitzFrei (d : Disposal) : Bool := d.mainHome && decide (24 ≤ d.heldMonths)

/-- § 30 (4): land acquired before 1 April 2002 (taken as an acquisition year before 2002; 0 = unknown = new). -/
def altvermoegen (d : Disposal) : Bool := decide (0 < d.acquiredYear) && decide (d.acquiredYear < 2002)

def immoGain (d : Disposal) : Int :=
  if hauptwohnsitzFrei d then 0
  else if altvermoegen d then divR .down (1400 * pos d.proceeds) BP
  else d.gain

def kapitalGains (ds : List Disposal) : Int := pos (isum ((ds.filter isKapital).map (·.gain)))
def immoGains (ds : List Disposal) : Int := pos (isum ((ds.filter (·.kind.isRealEstate)).map immoGain))

def kest (x : Int) : Int := divR .down (2750 * pos x) BP
def immoESt (x : Int) : Int := divR .down (3000 * pos x) BP

def charges (g : CanonGlobal) : List Charge :=
  if g.entity == .company || g.disposals.isEmpty then [] else
  [charge .pit "Einkommensteuer auf Einkünfte aus Kapitalvermögen (§ 27 (3), 27,5 %)" (isum ((g.disposals.filter isKapital).map (·.gain)))
     (fun _ => kapitalGains g.disposals) kest (event := "shares and bonds") (statute := "EStG 1988 § 27 (3), § 27a (1) Z 2"),
   charge .pit "Immobilienertragsteuer (§ 30a, 30 %)" (isum ((g.disposals.filter (·.kind.isRealEstate)).map (·.gain)))
     (fun _ => immoGains g.disposals) immoESt (event := "land") (statute := "EStG 1988 § 30 (2) Z 1, (4), § 30a (1)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 Kapitalvermögen, private Grundstücksveräußerungen", covers := [],
     run := fun args g prev =>
       charges g }]

def absent : List Absent :=
  []

def notes : List String := ["AT 1100: special-rate gains (§ 27a, § 30a) on the entity's disposals"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (fun d => d.kind.isRealEstate && d.mainHome && decide (d.heldMonths < 24)) then ["§ 30 (2) Z 1 lit. b (five of the last ten years as main home) not checked: give heldMonths"] else [])
  ++ (if g.disposals.any (fun d => d.kind.isRealEstate) then ["§ 30 (3) costs and inflation, § 30 (4) Z 1 (Umwidmung, 40 %) and the § 30a (2) option for the tariff not modelled"] else [])
  ++ (if g.disposals.any (fun d => d.kind.isShares && decide (d.acquiredYear < 2011) && decide (0 < d.acquiredYear)) then ["shares acquired before 2011 (old law, tax-free after one year) not separated"] else [])

#guard kest 10000 == 2750
#guard immoESt 100000 == 30000
#guard immoGain { kind := .home, proceeds := 300000, cost := 200000, heldMonths := 36, mainHome := true } == 0
#guard immoGain { kind := .home, proceeds := 300000, cost := 200000, heldMonths := 12, mainHome := true } == 100000
-- Altvermögen: 14 % of the proceeds, 4,2 % in tax
#guard immoESt (immoGain { kind := .realEstate, proceeds := 100000, cost := 20000, acquiredYear := 1990 }) == 4200
#guard kapitalGains [{ kind := .listedShares, proceeds := 1000, cost := 3000 }, { kind := .bonds, proceeds := 5000, cost := 1000 }] == 2000

end AtGlobal.Capital
