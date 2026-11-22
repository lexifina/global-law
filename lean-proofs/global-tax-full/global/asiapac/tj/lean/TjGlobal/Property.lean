import TjGlobal.Pit

/-!
# Tajikistan 2025: tax on real estate of individuals (4100), per m²

Tax Code of the Republic of Tajikistan (2021), edition of 14 May 2025, Tajik original and the Tax Committee's English text
(`cmp20/world/B05-former-ussr/tj/law/tc_tj_20250514.txt`, `tc_en_20250514.txt`), ch. 48 §1:
* **art. 344**: payers are individuals and legal entities owning or using immovable property; **art. 346 (1)**: base = the
  area occupied (each floor separately); (2) auxiliary premises of individuals 50 %;
* **art. 348 (1) 1)**: residential buildings and their auxiliary buildings, as % of the indicator for calculations per m²
  with the regional coefficient: up to 90 m² 3 %, 90-200 m² 4 %, above 200 m² 6 % (read here as the part of the area in
  each band: the Code does not say whether the whole area takes the band's rate); (2) coefficients 1.0 (Dushanbe) to 0.1;
* State Budget Law 2025 art. 23 (1): indicator for calculations 75 somoni (`budget2025_tj.txt`).
Input: asset `"areaM2"` (floor area) on `home` assets, `region` as in `coef10`; assets without `areaM2` are not computed
(flagged). Non-residential use (art. 348 (1) 2)-4)), land tax (art. 352) and the art. 347 exemptions are not applied.
-/

namespace TjGlobal.Property
open TaxKernel TaxKernel.Global

/-- Budget Law 2025 art. 23 (1): the indicator for calculations, 75 somoni from 1 January 2025. -/
def indicator : Int := 75

/-- art. 348 (2) regional coefficient in tenths, from the asset `region`: `dushanbe` (default) 1.0; `khujand`, `bokhtar`,
`kulob` 0.8; `group3` 0.6; `group4` 0.4; `group5` 0.3; `group6` 0.2; `group7` 0.1. -/
def coef10 (r : String) : Int :=
  if r == "khujand" || r == "bokhtar" || r == "kulob" then 8
  else if r == "group3" then 6 else if r == "group4" then 4 else if r == "group5" then 3
  else if r == "group6" then 2 else if r == "group7" then 1 else 10

/-- art. 348 (1) 1): residential buildings, % of the indicator per m²: 3 % to 90 m², 4 % from 90 to 200 m², 6 % above
(read as the part of the area in each band), in basis points times m². -/
def resTicks (area : Int) : Int :=
  min (pos area) 90 * 300 + min (pos (area - 90)) 110 * 400 + pos (area - 200) * 600

/-- Annual tax in somoni (down): area bands × indicator × regional coefficient. -/
def realTax (r : String) (area : Int) : Int := divR .down (resTicks area * indicator * coef10 r) 100000

/-- The asset's floor area from the line's raw JSON (`"areaM2"`; 0 when absent), as R5 AZ/GE/DZ. -/
def areaOf (g : CanonGlobal) (i : Nat) : Int := intField ((arrField g.raw "assets").toList.getD i Lean.Json.null) "areaM2"

def realF : Family :=
  { name := "4100 tax on real estate (Tax Code art. 348)", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      g.assets.zipIdx.filterMap fun (a, i) =>
        let ar := areaOf g i
        if ar ≤ 0 || a.kind != .home then none
        else some (charge .propertyRecurrent "Tax on real estate (residential)" ar pos (realTax a.region)
          (event := s!"property {i + 1}") (level := .local)
          (statute := s!"Tax Code 2021 arts. 344-346, 348 (1) 1), (2) (coefficient {coef10 a.region}/10); Budget Law 2025 art. 23 (1)")) }

#guard realTax "" 100 == 232
#guard realTax "kulob" 250 == 606
#guard realTax "group7" 50 == 11

def families : List Family := [realF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.entity != .company && g.assets.any (fun a => a.kind == .home || a.kind == .realEstate) then ["tax on real estate needs asset areaM2 (assets without it not computed); band reading (part of the area in each band) is this model's; region default Dushanbe 1.0; art. 347 exemptions not applied"] else [])
  ++ (if g.assets.any (fun a => a.kind == .realEstate || a.kind == .land) then ["non-residential real estate (art. 348 (1) 2)-4)) and land tax (arts. 349-352) not computed"] else [])
  ++ (if g.entity == .company then ["real estate and land tax of legal entities not computed"] else [])

#guard absent.length == 0

end TjGlobal.Property
