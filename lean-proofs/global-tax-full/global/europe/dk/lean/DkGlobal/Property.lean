import DkGlobal.Pit

/-!
# DK 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Tinglysningsafgiftsloven (0,6 % + fixed fee)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Ejendomsskatteloven (grundskyld, ejendomsværdiskat)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Tinglysningsafgift (pass 6)
Source: Lov om afgift af tinglysning af ejendomsret og pant m.v., LBK nr 307 af 13/03/2025, retsinformation.dk ELI XML (`dk/law/tinglysningsafgift_lbk2025_307.txt`).
* § 4 stk. 1: "For tinglysning af ejerskifte af fast ejendom eller andele heraf udgør afgiften 1.850 kr. og 0,6 pct. af ejerskiftesummen."


## 4100 Ejendomsværdiskat (pass 6)
Source: Ejendomsskatteloven, lov nr. 678 af 3. juni 2023, retsinformation.dk XML (`dk/law/ejendomsskattelov_lov2023_678.xml`).
* § 3 stk. 1: ejendomsværdiskat is paid on owner-occupied dwellings (one dwelling unit; two-unit owner dwellings; farm and forest dwellings)
* § 13 stk. 2: the base is 80 pct. of the ejendomsværdi assessed for the preceding income year
* § 22 stk. 2: 5,1 promille of the base up to 9 200 000 kr. (2024 level), 14,0 promille of the base above it
* § 22 stk. 3-4: the amount is adjusted every second year by an owner-dwelling value index first computed for income year 2026 (2025: 9 200 000 kr.)
* Not modelled: the reductions for dwellings acquired by 1 July 1998 (§§ 23-24: 1,0 and 2,1 promille), the transitional rebate (§ 40 stk. 2, owners under the old rules) and the pensioner reductions

* **4100 Grundskyld (pass 6 note, grade C)**: Ejendomsskatteloven § 1, kapitel 3 (grundskyld: the municipal rate, kommunal grundskyldspromille): grundskyld is charged at the rate each municipality sets on 80 pct. of the land value; the reference municipality's 2025 rate was not read (lov nr. 678 af 3.6.2023 (retsinformation.dk XML))


## 4100 Grundskyld (Københavns Kommune) (pass 6)
Source: Ejendomsskatteloven § 17, § 28, bilag 1 (retsinformation XML); ISM tables of the municipal rates (official): København 0 change against the bilag 1 ceiling for 2024 (the table's note: the change is shown against the ceiling of lov nr. 678) and 0 change for 2025.
* § 17 stk. 2: the grundskyld base is 80 pct. of the grundværdi assessed for the preceding year (stk. 3: production land at the whole value)
* § 28 stk. 1: the municipal council sets the rate, at most 30 promille; for 2024-2028 not above the municipality's figure in bilag 1
* bilag 1 (kommunespecifikke lofter for grundskyldspromiller 2024-2028): København 5,1
* ISM, Ændring i de kommunale skattesatser 2023-2024: København 0 promille point on øvrige ejendomme, measured against the bilag 1 ceiling; 2024-2025: 0 promille point; so the 2025 rate is 5,1 promille (grade B: the council's budget decision is not read itself)
* Not modelled: the transitional rebate (§ 40) and the cap on increases (§ 45), the deduction for grundforbedringer, production land (1,2-7,2 promille) and dækningsafgift
-/

namespace DkGlobal.Property
open TaxKernel TaxKernel.Global

/-- Tinglysningsafgiftsloven (LBK nr 307 af 13/03/2025) § 4 stk. 1 (1.850 kr. og 0,6 pct. af ejerskiftesummen) -/
def p7tgl (p : Purchase) : Int :=
  if [AssetKind.home, .realEstate, .land].contains p.kind then 1850 + divR .down (60 * pos p.price) 10000 else 0
def p7tglCharges (ps : List Purchase) : List Charge :=
  (ps.zipIdx.filter fun (p, _) => [AssetKind.home, .realEstate, .land].contains p.kind).map fun (p, i) =>
    charge .transactions "Tinglysningsafgift (ejerskifte)" p.price (fun v => v) (fun _ => p7tgl p) (event := s!"purchase {i + 1}") (statute := "Tinglysningsafgiftsloven (LBK nr 307 af 13/03/2025) § 4 stk. 1 (1.850 kr. og 0,6 pct. af ejerskiftesummen)")

/-- Ejendomsskatteloven (lov nr. 678 af 3. juni 2023) § 3, § 13 stk. 2, § 22 stk. 2-4 -/
def p6dkEvs : PropertyTax := { name := "Ejendomsværdiskat", sched := Schedule.ofList [(0, 51), (9200000, 140)], kinds := [.home], ratioNum := 4, ratioDen := 5 }

/-- Ejendomsskatteloven (lov nr. 678 af 3. juni 2023) § 17 stk. 1-2 (base 80 pct. of the grundværdi), § 28 stk. 1 and bilag 1 (Københavns Kommune: 5,1 promille for 2024-2028) -/
def p6dkGrundskyld : PropertyTax := { name := "Grundskyld (Københavns Kommune)", sched := Schedule.flat 51, kinds := [.land], ratioNum := 4, ratioDen := 5 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Tinglysningsafgift (ejerskifte)", covers := [.transactions],
     run := fun args g prev =>
       p7tglCharges g.purchases },
   { name := "4100 Ejendomsværdiskat", covers := [.propertyRecurrent],
     run := fun args g prev =>
       p6dkEvs.charges g.assets "Ejendomsskatteloven (lov nr. 678 af 3. juni 2023) § 3, § 13 stk. 2, § 22 stk. 2-4" (level := .central) },
   { name := "4100 Grundskyld (Københavns Kommune)", covers := [.propertyRecurrent],
     run := fun args g prev =>
       p6dkGrundskyld.charges g.assets "Ejendomsskatteloven (lov nr. 678 af 3. juni 2023) § 17 stk. 1-2 (base 80 pct. of the grundværdi), § 28 stk. 1 and bilag 1 (Københavns Kommune: 5,1 promille for 2024-2028)" (level := .local) }]

def absent : List Absent :=
  []

def notes : List String := ["DK 4400: tinglysningsafgiftsloven § 4, LBK 307/2025 (A)", "DK 4100 Ejendomsværdiskat: retsinformation.dk, lov nr. 678 af 3.6.2023 (XML fetched 2026-11-21, `dk/law/ejendomsskattelov_lov2023_678.xml`); § 22 stk. 4: the index that adjusts the 9 200 000 kr. amount is first computed for income year 2026, so 2025 keeps the 2024 level (grade A)", "DK 4100 Grundskyld (Københavns Kommune): retsinformation.dk, lov nr. 678 af 3.6.2023 (`dk/law/ejendomsskattelov_lov2023_678.xml`); Indenrigs- og Sundhedsministeriet, Ændring i de kommunale skattesatser 2023-2024 and 2024-2025 (`dk/law/ism_skattesatser_aendring_2023_2024.pdf`, `..._2024_2025.pdf`) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty then ["4400 tinglysningsafgift: the price is taken as the ejerskiftesum (§ 4 stk. 2-3: the public property value where the sale is not at arm's length); the pantebrev fee (§ 5: 1.825 kr. + 1,45 pct.) is not modelled"] else [])
  ++ (if g.assets.any (fun a => a.kind == .home || a.kind == .realEstate) then ["4100 grundskyld on a built property: only the land's grundværdi is taxed and it is not in the input (a home's value is the ejendomsværdi), so no grundskyld is charged on homes or other real estate (grade C there)"] else [])
  ++ (if g.assets.any (fun a => a.kind == .land) then ["4100 grundskyld: the land's value is taken as the grundværdi assessed for 2024; the § 40 rebate and the § 45 cap on increases are not applied"] else [])
  ++ (if g.assets.any (fun a => a.kind == .home) then ["4100 ejendomsværdiskat: the asset's value is taken as the assessed ejendomsværdi of the preceding year; the 1998 reductions (§§ 23-24) and the § 40 rebate are not applied"] else [])

#guard p7tgl { kind := .home, price := 2000000 } == 13850
#guard p7tgl { kind := .land, price := 100 } == 1850
#guard p7tgl { kind := .vehicle, price := 100000 } == 0
#guard p6dkEvs.amount { kind := .home, value := 300000 } == 1224
#guard p6dkEvs.amount { kind := .home, value := 3000000 } == 12240
#guard p6dkEvs.amount { kind := .deposits, value := 100000 } == 0
#guard p6dkEvs.amount { kind := .home, value := 15000000 } == 86120
#guard p6dkGrundskyld.amount { kind := .land, value := 300000 } == 1224
#guard p6dkGrundskyld.amount { kind := .land, value := 3000000 } == 12240
#guard p6dkGrundskyld.amount { kind := .deposits, value := 100000 } == 0

end DkGlobal.Property
