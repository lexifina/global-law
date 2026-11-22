import TaxKernel.Global
import R5Common

/-!
# Tunisia 2025: taxe sur les immeubles bâtis (TIB) and taxe sur les terrains non bâtis (TNB) (4100, local)

Code de la fiscalité locale (Law 97-11 of 3 February 1997 as amended), DGELF edition 2025 (jibaya.tn, uploaded
06/11/2025, `law/tn_cfl_2025.pdf` + `.txt`):
* art. 2: the TIB is due by the owner (or usufructuary; failing them, the possessor or occupier) of the building.
* art. 4-I: base = **2 %** of the reference price per m² of covered area fixed for the building's category × the covered
  area; 4-II categories by covered area: 1 up to 100 m², 2 above 100 up to 200 m², 3 above 200 up to 400 m², 4 above
  400 m²; 4-IV: a decree fixes every three years the minimum and maximum reference price; the local authority sets the
  price within those limits by reasoned order.
* art. 5-I: rate by the services the building enjoys: 8 % (one or two), 10 % (three or four), 12 % (more than four),
  14 % (more than four and other services).
* Décret gouvernemental n° 2017-397 du 28 mars 2017 (reproduced in the same edition), art. 1: reference price per m² of
  covered area, dinars: category 1 100-178, 2 163-238, 3 217-297, 4 271-356 (from 1 January 2017).
* art. 33: the TNB is due at **0,3 %** of the real market value of the land (per-m² zone tariff by decree only failing
  a market value).
Model: the municipality's order is not read, so the reference price is taken at the decree **maximum** and the rate at
**12 %** (an urban building with more than four services) unless the asset gives `"services"` (count 1-6, or 7 for
"more than four and other services"). Inputs: asset `"areaM2"` (covered area) for `home`/`realEstate`; `land` uses its
value. Owners are households here (company property not computed). **Grade A** (statute text read; municipal price
assumed as stated).
-/

namespace TnGlobal
open TaxKernel TaxKernel.Global R5Common

/-- Décret 2017-397 art. 1: maximum reference price per m² of covered area (dinars) for the art. 4-II category. -/
def refPriceMax (area : Int) : Int :=
  if area ≤ 100 then 178 else if area ≤ 200 then 238 else if area ≤ 400 then 297 else 356

/-- art. 5-I rate, bp, from the number of services (0 = not given: 12 %). -/
def tibRateBp (services : Int) : Int :=
  if services ≤ 0 then 1200 else if services ≤ 2 then 800 else if services ≤ 4 then 1000 else if services ≤ 6 then 1200 else 1400

/-- TIB in dinars (down): 2 % × reference price × covered area × rate. -/
def tib (area services : Int) : Int :=
  divR .down (200 * refPriceMax area * pos area * tibRateBp services) (BP * BP)

def tnAssetJson (g : CanonGlobal) (i : Nat) : Lean.Json := (arrField g.raw "assets").toList.getD i Lean.Json.null

def property : Family :=
  { name := "4100 TIB, TNB", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      g.assets.zipIdx.filterMap fun (a, i) =>
        let ar := intField (tnAssetJson g i) "areaM2"
        let sv := intField (tnAssetJson g i) "services"
        if (a.kind == .home || a.kind == .realEstate) && ar > 0 then
          some (charge .propertyRecurrent "Taxe sur les immeubles bâtis" ar pos (fun x => tib x sv)
            (event := s!"property {i + 1}") (level := .local)
            (statute := s!"Code de la fiscalité locale art. 2, 4, 5 (2 % of {refPriceMax ar} dinars/m², décret 2017-397 maximum; rate {tibRateBp sv / 100} %)"))
        else if a.kind == .land then
          some (charge .propertyRecurrent "Taxe sur les terrains non bâtis" a.statutoryValue pos (fun b => divR .down (30 * b) BP)
            (event := s!"land {i + 1}") (level := .local) (statute := "Code de la fiscalité locale art. 33 (0,3 % of market value)"))
        else none }

def propertyUnsupported (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["TIB/TNB on company property not computed"] else [])
  ++ (if g.entity != .company && g.assets.any (fun a => a.kind == .home || a.kind == .realEstate) then
    ["TIB needs asset areaM2 (assets without it not computed); municipal reference price taken at the décret 2017-397 maximum and the rate at 12 % unless `services` is given; low-income relief (art. 6-II) and the rent cap (art. 4-V) not applied"] else [])

#guard refPriceMax 120 == 238
#guard tib 120 0 == 68      -- 2 % × 238 × 120 × 12 % = 68,544
#guard tib 90 2 == 25       -- 2 % × 178 × 90 × 8 % = 25,632
#guard tib 500 7 == 498     -- 2 % × 356 × 500 × 14 % = 498,4

end TnGlobal
