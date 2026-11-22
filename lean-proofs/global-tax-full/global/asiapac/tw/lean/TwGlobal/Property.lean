import TwGlobal.Pit

/-!
# Taiwan 2025: house tax and deed tax (4100, 4400); land value tax not computed

Sources (session 10, law.moj.gov.tw, `tw/law/moj/`): 房屋稅條例 (G0340102, last amended 2024-01-03), 契稅條例 (G0340105,
last amended 2010-05-05), 土地稅法 (G0340096, last amended 2025-01-24).
* **房屋稅條例 art. 3, 5 (1) 1 (1)**: house tax on the house's current value (房屋現值); a residential house used as the
  owner's own home: 1.2 % (1 % for the only house nationwide of the owner, spouse and minor children below a local value:
  the local threshold is not read, so 1.2 % is used and the case is flagged). Other residential houses: local rates within
  1.5-2.4 % (rented at the standard rent), 2-3.6 % (builders' unsold stock), 2-4.8 % (others), set by each city by the
  number of houses held nationwide (art. 5 (2)): not read (C). **art. 5 (1) 2**: business use 3-5 % (local; the
  statutory minimum 3 % is used, flagged). Base: the asset's `assessed` value read as the house's current value
  (房屋現值, buildings only); an asset without it is not computed (C).
* **契稅條例 art. 2, 3 (1), 13**: deed tax on a purchase of a building, 6 % of the 契價 = the standard value set by the local
  real estate valuation committee (評定標準價格); land in areas where land value increment tax is levied is exempt (art.
  2). Base: the purchase's `assessed` value read as the building's standard value; without it (a price including land)
  not computed (C).
* **土地稅法 art. 16-17**: 地價稅 10 per mille up to the local progressive start value (the average value of 7 ares of land
  of the city or county), 15-55 per mille above it; self-use residential land 2 per mille (art. 17, urban land up to 3
  ares, one site per owner, spouse and dependent minors). The land value and the local start value are not in the entity:
  not computed (C).
-/

namespace TwGlobal.Property
open TaxKernel TaxKernel.Global

/-- 房屋稅條例 art. 5 (1) 1 (1): the first home (taken as the owner's own home) 1.2 %; art. 5 (1) 2: business use 3 %
(statutory minimum of the local 3-5 %). Base: `assessed` (房屋現值); other homes and assets without it: not computed. -/
def twHouseTax (g : CanonGlobal) : List Charge :=
  let firstHome := (g.assets.zipIdx.find? (fun (a, _) => a.kind == .home)).map (·.2)
  g.assets.zipIdx.filterMap fun (a, i) =>
    if a.assessed < 0 then none
    else if a.kind == .home && firstHome == some i then
      some (charge .propertyRecurrent "房屋稅 (自住 1.2 %)" a.assessed id (fun x => divR .down (x * 120) BP)
        (event := s!"asset {i + 1}") (level := .local) (statute := "房屋稅條例 第5條第1項第1款第1目 (自住 百分之一點二)"))
    else if a.kind == .realEstate then
      some (charge .propertyRecurrent "房屋稅 (非住家用 3 %)" a.assessed id (fun x => divR .down (x * 300) BP)
        (event := s!"asset {i + 1}") (level := .local) (statute := "房屋稅條例 第5條第1項第2款 (營業用 最低百分之三)"))
    else none

def houseF : Family :=
  { name := "4100 房屋稅", covers := [.propertyRecurrent], run := fun _ g _ => twHouseTax g }

/-- Homes and buildings the house tax does not compute: later homes (local rates) or no `assessed` value. -/
def twHouseUnread (g : CanonGlobal) : Nat :=
  (g.assets.filter (fun a => (a.kind == .home || a.kind == .realEstate) && a.assessed < 0)).length
  + ((g.assets.filter (fun a => a.kind == .home && 0 ≤ a.assessed)).length - 1)

/-- 契稅條例 art. 3 (1), 13: 6 % of the building's standard value (`assessed`). -/
def twDeedTax (g : CanonGlobal) : List Charge :=
  g.purchases.zipIdx.filterMap fun (p, i) =>
    if (p.kind == .home || p.kind == .realEstate) && 0 ≤ p.assessed then
      some (charge .transactions "契稅 (買賣 6 %)" p.assessed id (fun x => divR .down (x * 600) BP)
        (event := s!"purchase {i + 1}") (level := .local) (statute := "契稅條例 第2條, 第3條第1款 (契價百分之六), 第13條 (評定標準價格)"))
    else none

def deedF : Family :=
  { name := "4400 契稅", covers := [.transactions], run := fun _ g _ => twDeedTax g }

def families : List Family := [houseF, deedF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if twHouseUnread g > 0 then ["房屋稅: homes after the first (local rates 1.5-4.8 % by houses held nationwide, art. 5 (2)) and buildings without an assessed current value (房屋現值) not computed: grade C"] else [])
  ++ (if g.assets.any (fun a => a.kind == .home) then ["房屋稅: the first home is taken as the owner's own home at 1.2 % (the 1 % rate for a single nationwide home below the local value threshold not applied); 地價稅 (土地稅法 art. 16-17) needs the land value and the local progressive start value: not computed"] else [])
  ++ (if g.assets.any (fun a => a.kind == .realEstate) then ["房屋稅 on business-use buildings at the statutory minimum 3 % (local rate 3-5 %)"] else [])
  ++ (if g.purchases.any (fun p => (p.kind == .home || p.kind == .realEstate) && p.assessed < 0) then ["契稅: a purchase without the building's standard value (assessed) not computed (the price includes land, which is exempt under art. 2): grade C"] else [])
  ++ (if g.assets.any (fun a => a.kind == .land) then ["地價稅 on land (土地稅法 art. 16: 10-55 per mille by the local progressive start value) not computed"] else [])

#guard (twHouseTax { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 9000000, assessed := 1000000 }] }).map (·.due) == [12000]
#guard (twHouseTax { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 9000000, assessed := 1000000 }, { kind := .home, value := 5000000, assessed := 500000 }] }).map (·.due) == [12000]
#guard (twDeedTax { id := "t", household := { id := "t" }, purchases := [{ kind := .home, price := 12000000, assessed := 1000000 }] }).map (·.due) == [60000]
#guard (twDeedTax { id := "t", household := { id := "t" }, purchases := [{ kind := .home, price := 12000000 }] }).length == 0

end TwGlobal.Property
