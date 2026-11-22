import FrGlobal.Pit

/-!
# France 2025: impôt sur la fortune immobilière (4200)

Sources: CGI copies of the 1.x French model (`fr/law/y2025/`): art. 964 (version 2018-01-01), 973 (2023-12-31),
977 (2018-01-01).
* **art. 964**: the IFI is due by persons whose net real-estate wealth reaches "1 300 000 €" (entry threshold).
* **art. 973**: "un abattement de 30 % est effectué sur la valeur vénale réelle de l'immeuble lorsque celui-ci est
  occupé à titre de résidence principale par son propriétaire".
* **art. 977 1**: "N'excédant pas 800 000 € 0"; "Supérieure à 800 000 € et inférieure ou égale à 1 300 000 € 0,50";
  "... 2 570 000 € 0,70"; "... 5 000 000 € 1"; "... 10 000 000 € 1,25"; "Supérieure à 10 000 000 € 1,50".
  **977 2**: between 1 300 000 € and 1 400 000 € the tax is "réduit d'une somme égale à 17 500 €-1,25 % P, où P est la
  valeur nette taxable du patrimoine".
Only real estate is counted (the entity's `home`, `realEstate`, `land` assets), debts on it deducted (art. 974, read
in structure only).


FT review (2026-11-21):
* **art. 973** gives the 30 % to "l'immeuble ... occupé à titre de résidence principale par son propriétaire": one home.
  The entity's first `home` is read as the résidence principale; any further home counts in full (the model gave
  30 % to every home).
* **art. 979 I** (`fr/law/y2025/979.md`, version of the Loi n° 2018-1317 du 28 décembre 2018): the IFI "est réduit
  de la différence entre, d'une part, le total de cet impôt et des impôts dus en France ... au titre des revenus et
  produits de l'année précédente ... et, d'autre part, 75 % du total des revenus mondiaux nets de frais professionnels
  de l'année précédente"; **II**: incomes "sans considération des exonérations, seuils, réductions et abattements ... à
  l'exception de ceux représentatifs de frais professionnels". Read with the 1.x model's line for the entity's own year
  (the previous year's figures are not in the entity): income = its `rni` (wages net of contributions and of the 10 %
  for frais professionnels), taxes = its income tax + CSG/CRDS on wages.
-/

namespace FrGlobal.Wealth
open TaxKernel TaxKernel.Global

def ifi : WealthTax :=
  { name := "Impôt sur la fortune immobilière",
    valuation := fun k => if k == .home then 7000 else 10000, useAssessed := false,
    exemptKinds := [.listedShares, .unlistedShares, .bonds, .deposits, .business, .pensionFund, .vehicle, .other],
    entryThreshold := 1300000,
    sched := Schedule.ofList [(0, 0), (800000, 50), (1300000, 70), (2570000, 100), (5000000, 125), (10000000, 150)] }

/-- art. 977 2: décote between 1 300 000 and 1 400 000 €. -/
def decote (p : Int) : Int := if 1300000 ≤ p ∧ p < 1400000 then pos (17500 - divR .down (125 * p) BP) else 0

def ifiTax (as : List Asset) : Int := pos (ifi.gross as - decote (ifi.base as))

def charges (g : CanonGlobal) : List Charge :=
  if g.entity == .company || !(g.assets.any (·.kind.isRealEstate)) then [] else
  [charge .wealth ifi.name (ifi.netWealth g.assets) (fun _ => ifi.base g.assets) (fun _ => ifiTax g.assets)
     (event := "1 January 2025") (statute := "CGI art. 964, 973 (30 % résidence principale), 977 (tarif, décote)")]

/-- art. 973: the abatement for the résidence principale applies to one home, the entity's first `home`; any further
home counts as other real estate (in full). -/
def rpAssets (as : List Asset) : List Asset :=
  (as.foldl (fun (acc : List Asset × Bool) a =>
     if a.kind == .home then
       (if acc.2 then (acc.1 ++ [{ a with kind := .realEstate }], true) else (acc.1 ++ [a], true))
     else (acc.1 ++ [a], acc.2)) ([], false)).1

/-- art. 979 I: reduced by the excess of (IFI + taxes on the income) over 75 % of the income. -/
def ifiCap : WealthTax := { ifi with capBp := 7500 }

/-- The cap's inputs from the 1.x line: (income tax + CSG/CRDS on wages, rni). -/
def capInputs (args : List String) (g : CanonGlobal) : Int × Int :=
  let j := pitLine args g.household.raw
  let d := match j.getObjVal? "detail" with | .ok x => x | _ => Lean.Json.null
  (jsonIncomeTax j + intField d "csgCrdsWages", intField d "rni")

def ifiCapped (args : List String) (g : CanonGlobal) : Int :=
  let (t, inc) := capInputs args g
  ifiCap.capped (ifiTax (rpAssets g.assets)) t inc

def chargesCapped (args : List String) (g : CanonGlobal) : List Charge :=
  if g.entity == .company || !(g.assets.any (·.kind.isRealEstate)) then [] else
  [charge .wealth ifi.name (ifi.netWealth (rpAssets g.assets)) (fun _ => ifi.base (rpAssets g.assets)) (fun _ => ifiCapped args g)
     (event := "1 January 2025") (statute := "CGI art. 964, 973 (30 % résidence principale, one home), 977 (tarif, décote), 979 (plafonnement 75 %)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4200 IFI", covers := [.wealth],
     run := fun args g prev =>
       chargesCapped args g }]

def absent : List Absent :=
  []

def notes : List String := ["FR 4200: IFI on real estate"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (·.kind.isRealEstate) then ["IFI: the household is one foyer; shares of real-estate companies (art. 965 2°) and exempt business property (art. 975) not modelled; the first home is the résidence principale; the art. 979 cap reads the entity's own year (not the previous year), income tax + CSG/CRDS on wages"] else [])

#guard ifiTax [{ kind := .realEstate, value := 1299999 }] == 0
-- 1 350 000 €: 2 500 + 350 = 2 850 less the décote 17 500 - 16 875 = 625
#guard ifiTax [{ kind := .realEstate, value := 1350000 }] == 2225
#guard ifiTax [{ kind := .realEstate, value := 3000000 }] == 2500 + 8890 + 4300
#guard ifiTax [{ kind := .home, value := 1800000 }] == 0
#guard ifiTax [{ kind := .listedShares, value := 9000000 }] == 0
-- art. 973: one résidence principale (1 800 000 x 70 % + 1 000 000 = 2 260 000: 2 500 + 6 720)
#guard ifiTax (rpAssets [{ kind := .home, value := 1800000 }, { kind := .home, value := 1000000 }]) == 9220
-- art. 979: IFI 10 000, taxes 0, income 10 000: reduced by 10 000 - 7 500
#guard ifiCap.capped 10000 0 10000 == 7500
#guard ifiCap.capped 10000 5000 100000 == 10000
#guard ifiCap.capped 10000 9000 10000 == 0

end FrGlobal.Wealth
