import KzGlobal.Pit

/-!
# Kazakhstan 2025: property tax of individuals on dwellings (4100)

Source: Tax Code of 25 December 2017 No. 120-VI (K1700000120), adilet text archived 2025-06-11 (Wayback), copied by the
1.x KZ builder (`cmp20/world/B05-former-ussr/kz/law/tc_wb20250611.txt`, sha256 in `kz/law/SOURCES.tsv`), ch. 65.
* **art. 528 (1)**: dwellings, buildings, dacha buildings, garages and other structures owned by individuals; (2) land.
* **art. 529**: base = the value set each 1 January by the State Corporation (C = Cb × S × K...): the asset's
  statutory (assessed) value, else its market value.
* **art. 531 (1)**: 16 bands on the value: up to 2 000 000 tenge 0.05 %; 1 000 + 0.08 % above 2 m; ... 46 600 + 0.5 %
  above 20 m; 321 600 + 0.6 % above 75 m; 471 600 + 0.65 % above 100 m; 796 600 + 0.7 % above 150 m; 2 196 600 + 0.75 %
  above 350 m; 2 946 600 + 2 % above 450 m (the fixed amounts are the sums of the lower bands: a marginal schedule).
* Land of individuals (art. 531 (2): tenge per m² by settlement) and the exemptions of art. 526 (2) (veterans, large
  families, pensioners up to 1 000-1 500 MRP) are not modelled.
-/

namespace KzGlobal.Property
open TaxKernel TaxKernel.Global

def prop0 : PropertyTax :=
  { name := "Property tax of individuals (Tax Code art. 531 (1))", sched := (Schedule.ofList [(0, 5), (2000000, 8), (4000000, 10), (6000000, 15), (8000000, 20), (10000000, 25), (12000000, 30), (14000000, 35), (16000000, 40), (18000000, 45), (20000000, 50), (75000000, 60), (100000000, 65), (150000000, 70), (350000000, 75), (450000000, 200)]), ratioNum := 1, ratioDen := 1, exempt := 0, kinds := [.home, .realEstate] }

def fam0 : Family :=
  { name := "4100 recurrent taxes on immovable property", covers := [.propertyRecurrent],
    run := fun _ g _ => 
      prop0.charges g.assets "Tax Code 2017 arts. 528, 529, 531 (1)" (level := .local) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => a.kind == .land) then ["land of individuals is taxed per m² by settlement category (Tax Code art. 531 (2)-(4)): not modelled"] else [])
  ++ (if !g.assets.isEmpty then ["exemptions of art. 526 (2) (veterans, orphans, large families, separately living pensioners) not applied"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 2000000 }] } []).map (·.due) == [1000]
#guard (fam0.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 30000000 }] } []).map (·.due) == [96600]

end KzGlobal.Property
