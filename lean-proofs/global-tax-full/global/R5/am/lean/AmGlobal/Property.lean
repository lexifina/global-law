import TaxKernel.Global
import R5Common

/-!
# Armenia 2025: immovable property tax (4100, local)

Tax Code HO-165-N, official English translation on arlis.am (acts/229632, with changes to HO-487-N of 17/12/2025;
`law/am_tc_en_arlis229632.txt`), Section 11:
* art. 224-225: a local tax paid by the owners (organisations and natural persons) of immovable property.
* art. 228(1): base = the cadastral value approximated to the market value (valued every three years, art. 228(3)).
* art. 229(1)(3): apartments of multi-apartment buildings (and non-residential spaces in them), marginal: 0,05 % up to
  AMD 10 million; 0,1 % to 25 million; 0,2 % to 47 million; 0,4 % to 75 million; 0,6 % to 100 million; 1 % to 200
  million; 1,5 % above (the statute's cumulative amounts 5 000 / 20 000 / 64 000 / 176 000 / 326 000 / 1 326 000 check).
  (1)(4): individual houses and garden cottages 0,05 % to 7 million, then 0,1 / 0,2 / 0,4 / 0,6 / 1 / 1,5 % with limits
  23 / 50 / 85 / 120 / 200 million. (1)(2)(a): land without improvements intended for residential development 0,6 %.
* art. 230: exemptions (state reserves, historic property, fallen soldiers' families, conscripts, …) not relevant to the
  model's households; art. 230(3) community benefits not applied.
Model: `home` = an apartment (table (3); a house is table (4): asset `"house": true`), `land` = residential building land
(0,6 %); base = the asset's assessed (cadastral) value, else its value. Households only. **Grade A** (official
translation read).
* art. 233(7) (HO-332-N, read in pass 3l): the tax (except agricultural land) is a share of the product of the cadastral
  value and the art. 229(1)(2)-(7) rates: 2021 25 %, 2022 30 %, 2023 35 %, 2024 50 %, **2025 75 %**, 2026 on 100 %.
-/

namespace AmGlobal
open TaxKernel TaxKernel.Global R5Common

/-- Marginal bands (upper limit, rate in hundredths of a percent). -/
def apartmentBands : List (Int × Int) :=
  [(10000000, 5), (25000000, 10), (47000000, 20), (75000000, 40), (100000000, 60), (200000000, 100)]
def houseBands : List (Int × Int) :=
  [(7000000, 5), (23000000, 10), (50000000, 20), (85000000, 40), (120000000, 60), (200000000, 100)]

/-- Tax (hundredths of a percent = 1/10000) on base `b` over marginal bands, 150 (1,5 %) above the last limit. -/
def bandTax (bands : List (Int × Int)) (b : Int) : Int :=
  let rec go : List (Int × Int) → Int → Int
    | [], lo => pos (b - lo) * 150
    | (hi, r) :: t, lo => (max 0 (min b hi - lo)) * r + (if b > hi then go t hi else 0)
  divR .down (go bands 0) BP

/-- art. 233(7): share (percent) of the full tax charged in the reporting year -/
def phasePct (y : Nat) : Int :=
  if y ≤ 2020 then 100 else if y == 2021 then 25 else if y == 2022 then 30 else if y == 2023 then 35
  else if y == 2024 then 50 else if y == 2025 then 75 else 100

def phaseIn (y : Nat) (t : Int) : Int := divR .down (t * phasePct y) 100

def amAssetJson (g : CanonGlobal) (i : Nat) : Lean.Json := (arrField g.raw "assets").toList.getD i Lean.Json.null

def isHouse (j : Lean.Json) : Bool := match j.getObjValAs? Bool "house" with | .ok b => b | .error _ => false

def property : Family :=
  { name := "4100 Immovable property tax", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      g.assets.zipIdx.filterMap fun (a, i) =>
        if a.kind == .home then
          let h := isHouse (amAssetJson g i)
          some (charge .propertyRecurrent "Immovable property tax" a.statutoryValue pos (fun b => phaseIn g.year (bandTax (if h then houseBands else apartmentBands) b))
            (event := s!"property {i + 1}") (level := .local)
            (statute := if h then "Tax Code art. 228, 229(1)(4) (individual house, marginal 0,05-1,5 %), 233(7) (2025: 75 %)" else "Tax Code art. 228, 229(1)(3) (apartment, marginal 0,05-1,5 %), 233(7) (2025: 75 %)"))
        else if a.kind == .land then
          some (charge .propertyRecurrent "Immovable property tax (land)" a.statutoryValue pos (fun b => phaseIn g.year (divR .down (60 * b) BP))
            (event := s!"land {i + 1}") (level := .local) (statute := "Tax Code art. 229(1)(2)(a) (residential building land 0,6 %), 233(7) (2025: 75 %)"))
        else none }

def propertyUnsupported (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["immovable property tax of organisations (quarterly, art. 229(2)) not computed"] else [])
  ++ (if g.entity != .company && g.assets.any (fun a => a.kind == .realEstate) then ["immovable property tax on other buildings (public 0,3 %, industrial 0,25 %, garages 0,2 %) not computed: building type not an input"] else [])
  ++ (if g.entity != .company && g.assets.any (fun a => a.kind == .home || a.kind == .land) then ["immovable property tax: base taken as the asset's assessed (cadastral) value, else its value; community benefits (art. 230(3)) not applied"] else [])

#guard bandTax apartmentBands 10000000 == 5000
#guard bandTax apartmentBands 25000000 == 20000
#guard bandTax apartmentBands 47000000 == 64000
#guard bandTax apartmentBands 100000000 == 326000
#guard bandTax apartmentBands 200000000 == 1326000
#guard bandTax apartmentBands 300000000 == 2826000
#guard bandTax houseBands 23000000 == 19500
#guard bandTax houseBands 200000000 == 1223500
#guard phaseIn 2025 50000 == 37500
#guard phaseIn 2026 50000 == 50000

end AmGlobal
