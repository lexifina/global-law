import MhGlobal.Pit

/-!
# Marshall Islands 2025: import duties (5120); consumption tax and excise tax not yet applicable

Sources (rmiparliament.org consolidations, Internet Archive captures; `mh/law/`):
* **Import Duties Act 1989** (48 MIRC Ch. 2), consolidation `1989-0049_9` (captured 2024-11-26) and `1989-0049_10`
  (captured 2026-02-27, adds P.L. 2025-31, which amends § 227 only): Schedule 1 is the same in both, so it is the 2025 text.
  **§ 204**: import duty at the rates of Schedule 1. **Schedule 1 (5)**: a uniform tax on all imports at 8 % of the
  C.I.F. value except: foodstuffs 5 %; gasoline "0.25 cents per gallon", diesel "0.08 cents per gallon"; tobacco and
  cigarettes $1.00 per pack of 20; cigars 151 %; other tobacco $2.75 per 34.2 g; beer $0.35 per can or 12 oz unit; wine
  $2.75 per gallon; spirits $15.00 per gallon; mixed drinks 26 %; carbonated soft drinks 0.01666 per oz; non-carbonated
  flavoured beverages 10 %. **(2) (b)**: milk, soy milk, rice, flour, vegetables, fruit, baby food, poultry and canned fish
  exempt.
  Modelled: the specific duties on cigarettes, beer, wine, spirits, petrol and diesel (per unit, as if every taxed good were
  imported, FM pattern). The fuel rates are read as printed (US$ 0.0025 and 0.0008 per gallon). Not modelled: the 8 % and
  5 % ad valorem duties (C.I.F. value, not in the basket) and the per-ounce soft-drink duty (the basket's non-alcoholic
  class mixes carbonated and other drinks).
* **Consumption Tax Act 2025** (P.L. 2025-47, 48 MIRC Ch. 9, commenced 7 October 2025) **§ 959 (2)**: "This Chapter
  applies to supplies and imports made on or after October 1, 2026" (12 %, threshold $300,000: not 2025).
* **Excise Tax Act 2025** (P.L. 2025-46, 11 MIRC Ch. 20) **§ 2043**: applies to supplies and imports made on or after
  1 October 2026.
-/

namespace MhGlobal.Consumption
open TaxKernel TaxKernel.Global

/-- Specific import duty per canonical unit as a fraction (num, den) of dollars: Import Duties Act 1989 Schedule 1 (5).
Cigarettes $1.00 per pack of 20 (per stick 5/100); beer $0.35 per 12 US fl oz (354.882 ml); wine $2.75 and spirits $15.00 per
US gallon (3.785412 l); gasoline 0.25 and diesel 0.08 cents per gallon as printed. -/
def dutySpecific (g : Good) : Int × Int :=
  match g with
  | .cigarettes => (5, 100)
  | .beer => (350000, 354882)
  | .wine => (2750000, 3785412)
  | .spirits => (15000000, 3785412)
  | .petrol => (2500, 3785412)
  | .diesel => (800, 3785412)
  | _ => (0, 1)

def dutyIn (s : Spend) : Int :=
  let (n, d) := dutySpecific s.good
  divR .down (s.quantity * n) (d * 1000)

def basketCharges (xs : List Spend) : List Charge :=
  (xs.filter fun s => (dutySpecific s.good).1 > 0).map fun s =>
    charge .goodsOther "RMI import duty (specific)" s.amount id (fun _ => dutyIn s) (event := s.good.name) (bearer := .consumer)
      (statute := "Import Duties Act 1989 (48 MIRC Ch. 2) § 204, Schedule 1 (5) items 2, 4, 8, 11-13")

def families : List Family :=
  [{ name := "5120 import duties (specific)", covers := [.goodsOther],
     run := fun _ g _ => basketCharges g.consumption }]

def absent : List Absent :=
  [{ oecd := .vat, why := "no VAT or general consumption tax in 2025: Consumption Tax Act 2025 (P.L. 2025-47, 48 MIRC Ch. 9) § 959 (2) applies it to supplies and imports made on or after 1 October 2026" },
   { oecd := .excise, why := "no excise tax in 2025: Excise Tax Act 2025 (P.L. 2025-46, 11 MIRC Ch. 20) § 2043 applies it to supplies and imports made on or after 1 October 2026; the 2025 duties on tobacco, alcohol and fuel are import duties (5120, modelled)" }]

def notes : List String := ["MH 5120: Import Duties Act 1989 Schedule 1 (consolidations 1989-0049_9 and _10, same schedule); 5111/5121 cited absent for 2025 (P.L. 2025-47 \u00a7 959 (2), P.L. 2025-46 \u00a7 2043)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if !g.consumption.isEmpty then ["import duty: the uniform 8 % and the 5 % on foodstuffs are levied on the C.I.F. value (Schedule 1 (4)-(5)): not in the basket, not modelled; specific duties applied as if every taxed good were imported"] else [])
  ++ (if g.consumption.any (fun s => s.good == .nonAlcoholic || s.good == .tobaccoOther) then ["carbonated soft drinks 0.01666 per oz and other tobacco $2.75 per 34.2 g (Schedule 1 items 10, 15): the basket's classes mix taxed and other goods: not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel) then ["fuel duties read as printed (gasoline 0.25 and diesel 0.08 cents per gallon)"] else [])

-- 20 sticks: $1.00
#guard dutyIn { good := .cigarettes, amount := 10, quantity := 20000 } == 1
-- 10 US gallons of spirits: $150
#guard dutyIn { good := .spirits, amount := 400, quantity := 37854 } == 149
#guard dutyIn { good := .clothing, amount := 100 } == 0
#guard absent.length == 2

end MhGlobal.Consumption
