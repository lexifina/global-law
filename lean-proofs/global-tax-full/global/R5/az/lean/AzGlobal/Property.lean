import TaxKernel.Global
import R5Common

/-!
# Azerbaijan 2025: property tax and land tax of natural persons (4100)

Tax Code of the Republic of Azerbaijan (Vergi Məcəlləsi), e-qanun.az framework 46948, read from the Wayback captures of
`e-qanun.az/frameworks/46/f_46948.html` of 04/12/2024 and 24/08/2026 (art. 198 and 206 identical apart from footnote
numbers; extract `law/eqanun_46948_art198-206.txt`):
* art. 198.1.1: natural persons pay property tax per m² of the buildings they own ("yaşayış sahələrinə münasibətdə -
  onların 30 kvadratmetrdən artıq olan hissəsinin": for dwellings, the part above 30 m²), manat per m²: Baku 0.4
  (times a coefficient of 0.7 to 1.5 set by the executive authority); Ganja, Sumgait and Absheron district 0.3; other
  cities and district centres 0.2; towns under districts, settlements and villages 0.1.
* art. 198.2: enterprises 1 % of the value of fixed assets (art. 202) (not computed: fixed-asset value not an input).
* art. 206.3: land other than agricultural, per 100 m², for land under housing, household plots and garden plots
  (manat): Baku and its settlements 0.6 up to 10,000 m², 1.2 for the part above; Ganja, Sumgait, Khirdalan and Absheron
  settlements 0.5 / 1.0; other cities and district centres 0.3 / 0.6; towns, settlements and villages 0.1 / 0.2.
  art. 206.1: agricultural land 2 manat per 100 m² (206.1-1: 0.06 manat per conditional point; not computed).
* art. 199.3: the property tax on buildings of listed persons (pensioners, art. 102.1-1 and 102.2 persons, conscripts'
  families) is reduced by 30 manat (not applied).
Inputs: asset `"areaM2"` (floor area for `home`/`realEstate`, plot area for `land`); `region`: `baku` (default),
`ganja`/`sumgait`/`absheron`/`xirdalan`, `city`, `village`. Baku coefficient taken as 1.0. **Grade A** (statute read).
-/

namespace AzGlobal
open TaxKernel TaxKernel.Global R5Common

/-- 1 = Baku, 2 = Ganja/Sumgait/Absheron/Khirdalan, 3 = other cities and district centres, 4 = villages. -/
def zone (r : String) : Nat :=
  if r == "ganja" || r == "sumgait" || r == "absheron" || r == "xirdalan" then 2
  else if r == "city" then 3 else if r == "village" then 4 else 1

/-- art. 198.1.1, qəpik per m². -/
def bldRate : Nat → Int | 1 => 40 | 2 => 30 | 3 => 20 | _ => 10

/-- art. 206.3 housing/household/garden land, qəpik per 100 m² up to 10,000 m² and above. -/
def landRates : Nat → Int × Int | 1 => (60, 120) | 2 => (50, 100) | 3 => (30, 60) | _ => (10, 20)

def bldTax (z : Nat) (dwelling : Bool) (area : Int) : Int :=
  divR .down (pos (if dwelling then area - 30 else area) * bldRate z) 100

def landTax (z : Nat) (area : Int) : Int :=
  let (r1, r2) := landRates z
  divR .down (min (pos area) 10000 * r1 + pos (area - 10000) * r2) 10000

def areaOf (g : CanonGlobal) (i : Nat) : Int := intField ((arrField g.raw "assets").toList.getD i Lean.Json.null) "areaM2"

def property : Family :=
  { name := "4100 Əmlak vergisi, torpaq vergisi", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      g.assets.zipIdx.filterMap fun (a, i) =>
        let ar := areaOf g i
        if ar ≤ 0 then none
        else if a.kind == .home || a.kind == .realEstate then
          some (charge .propertyRecurrent "Əmlak vergisi" ar pos (bldTax (zone a.region) (a.kind == .home))
            (event := s!"property {i + 1}") (level := .local)
            (statute := s!"Tax Code art. 198.1.1 ({bldRate (zone a.region)} qəpik per m²{if a.kind == .home then " above 30 m²" else ""})"))
        else if a.kind == .land then
          some (charge .propertyRecurrent "Torpaq vergisi" ar pos (landTax (zone a.region))
            (event := s!"land {i + 1}") (level := .local) (statute := "Tax Code art. 206.3 (housing, household and garden plots, per 100 m²)"))
        else none }

def propertyUnsupported (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["enterprise property tax (art. 198.2: 1 % of fixed assets) and enterprise land tax not computed"] else [])
  ++ (if g.entity != .company && g.assets.any (fun a => a.kind.isRealEstate) then
    ["property and land tax need asset areaM2 (assets without it not computed); Baku coefficient (0.7-1.5) taken as 1.0; region default baku; 30-manat reduction (art. 199.3) and agricultural land not applied"] else [])

#guard bldTax 1 true 100 == 28
#guard bldTax 4 false 100 == 10
#guard landTax 1 600 == 3
#guard landTax 1 20000 == 180

end AzGlobal
