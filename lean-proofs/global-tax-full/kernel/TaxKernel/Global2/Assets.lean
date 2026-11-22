import TaxKernel.Global

/-!
# TaxKernel.Global2.Assets (2.4.0, 2026-11-21): facts read from the asset record; rate tables on a quantity

As for basket lines (`Basket`), `Asset` is unchanged: facts a statute needs beyond it are read from the asset's own
record in the input line (`g.raw`, `"assets"`, the same order as `g.assets`).

* `assetJson g i`: the record of asset `i` (0-based); `Json.null` for an entity built in Lean without `raw`.
* **Floor area, the canonical field `"areaM2"`** (square metres, whole): the floor area of a `home` or `realEstate`
  asset, the plot area of `land`. `assetAreaM2 g i` reads it, 0 when not given: exactly the expression R5 AZ
  (`areaOf`), GE (`landAreaOf`) and DZ (`tfArea`) wrote by hand (`assetAreaM2_eq`, by `rfl`), so they may switch with no
  output change. `assetsArea g` pairs each asset with its area (`assetsArea_fst`).
* `QtyTable`: a rate table on a quantity (m², cm³, kW, CV, g CO2/km, kg, seats, years, a value), counted in started
  steps (`step`: DE KraftStG § 9 (1) Nr. 2 "je angefangene 100 cm³"):

      amount q = band (counted q) + ⌊ Σ_k num_k × |(from_k, from_{k+1}] ∩ (−∞, counted q]| / den ⌋

  `bands` `(from, amount)`: the amount of the highest band with `from ≤ q` (a fixed sum per band: UK VED, IE motor
  tax, R4 vignettes); `QtyTable.ofCeilings` writes "up to c: a" tables (`R4.VehTariff`). `steps` `(from, num)`:
  `num / den` money per unit above `from` up to the next step's `from` (marginal: DE CO2 2,00 to 4,00 € per g above
  95 g/km; AZ land per 100 m² up to and above 1 ha); a flat rate per unit is `steps := [(0, num)]`. Rounded down once.
* `AreaTax`: a tax per m² (OECD 4100 by default) on each asset of `kinds` that gives `"areaM2"` (> 0), its table by asset
  (`tableFor`: kind, region) else `table`; `unknown` lists the assets of those kinds without an area (grade C).

Theorems: `assetAreaM2_eq`, `assetsArea_fst`, `QtyTable.slice_mono`, `QtyTable.marginalNum_mono`,
`QtyTable.marginalNum_nonneg`, `QtyTable.marginal_mono` (non-negative rates: more of the quantity never costs less),
`QtyTable.amount_flat` (one step from 0: `⌊pos q × num / den⌋`, the R5 hand-written form), `AreaTax.charges_noArea`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-! ## The asset record -/

/-- The input record of asset `i` (0-based, the order of `g.assets`). -/
def assetJson (g : CanonGlobal) (i : Nat) : Json := (arrField g.raw "assets").toList.getD i Json.null

/-- Floor area (plot area for land) of asset `i` in m², from its `"areaM2"`; 0 when not given. -/
def assetAreaM2 (g : CanonGlobal) (i : Nat) : Int := intField (assetJson g i) "areaM2"

/-- The reading R5 AZ, GE and DZ wrote by hand. -/
theorem assetAreaM2_eq (g : CanonGlobal) (i : Nat) :
    assetAreaM2 g i = intField ((arrField g.raw "assets").toList.getD i Json.null) "areaM2" := rfl

/-- Each asset with its area (0: not given), in the order of `g.assets`. -/
def assetsArea (g : CanonGlobal) : List (Asset × Int) := g.assets.zipIdx.map fun (a, i) => (a, assetAreaM2 g i)

theorem assetsArea_fst (g : CanonGlobal) : (assetsArea g).map Prod.fst = g.assets := by
  simp [assetsArea, List.map_map, Function.comp_def]

/-! ## Rate tables on a quantity -/

structure QtyTable where
  /-- count the quantity in started steps of `step` (rounded up to a multiple; ≤ 1: as given) -/
  step : Int := 1
  /-- `(from, amount)`: the amount of the highest band with `from ≤ quantity` (0 below the first) -/
  bands : List (Int × Int) := []
  /-- `(from, num)`: `num / den` money per unit of the quantity above `from`, up to the next `from` (increasing) -/
  steps : List (Int × Int) := []
  den : Int := 1
  deriving Repr, Inhabited, BEq

namespace QtyTable

/-- The quantity as the statute counts it: in started steps. -/
def counted (t : QtyTable) (q : Int) : Int := if t.step ≤ 1 then q else divR .up q t.step * t.step

/-- The fixed amount of the band the quantity reaches. -/
def band (t : QtyTable) (q : Int) : Int := t.bands.foldl (fun acc (f, a) => if f ≤ q then a else acc) 0

/-- Units of `q` above `lo`, up to `hi` (none: no ceiling). -/
def slice (q lo : Int) : Option Int → Int
  | some hi => pos (min q hi - lo)
  | none => pos (q - lo)

/-- The marginal parts, in `1/den` of money. -/
def marginalNum : List (Int × Int) → Int → Int
  | [], _ => 0
  | (f, n) :: rest, q => slice q f (rest.head?.map Prod.fst) * n + marginalNum rest q

def marginal (t : QtyTable) (q : Int) : Int := divR .down (marginalNum t.steps q) t.den

/-- **The amount of the table for a quantity**: the band reached plus the marginal parts (rounded down once). -/
def amount (t : QtyTable) (q : Int) : Int := t.band (t.counted q) + t.marginal (t.counted q)

/-- "Up to `c`: `a`" tables: `[(c₁, a₁), (c₂, a₂), …]` (ceilings inclusive, increasing) and the amount above the last
(R4 `VehTariff`: the first band whose ceiling is at least the quantity, else `top`). For quantities ≥ 0. -/
def ofCeilings (bands : List (Int × Int)) (top : Int) : QtyTable :=
  { bands := (0 :: bands.map (·.1 + 1)).zip (bands.map (·.2) ++ [top]) }

/-- A flat amount per unit: `num / den` money per unit from the first. -/
def perUnit (num den : Int) (step : Int := 1) : QtyTable := { step, steps := [(0, num)], den }

theorem slice_mono (lo : Int) (hi : Option Int) {x y : Int} (h : x ≤ y) : slice x lo hi ≤ slice y lo hi := by
  cases hi <;> simp only [slice, pos] <;> omega

theorem slice_nonneg (q lo : Int) (hi : Option Int) : 0 ≤ slice q lo hi := by
  cases hi <;> simp only [slice] <;> exact pos_nonneg _

theorem marginalNum_nonneg (l : List (Int × Int)) (q : Int) (h : ∀ p ∈ l, 0 ≤ p.2) : 0 ≤ marginalNum l q := by
  induction l with
  | nil => simp [marginalNum]
  | cons p rest ih =>
    obtain ⟨f, n⟩ := p
    simp only [marginalNum]
    have hn : 0 ≤ n := h (f, n) (by simp)
    have h1 := Int.mul_nonneg (slice_nonneg q f (rest.head?.map Prod.fst)) hn
    have h2 := ih (fun p hp => h p (by simp [hp]))
    omega

/-- With non-negative rates the marginal parts never fall as the quantity rises. -/
theorem marginalNum_mono (l : List (Int × Int)) (h : ∀ p ∈ l, 0 ≤ p.2) {x y : Int} (hxy : x ≤ y) :
    marginalNum l x ≤ marginalNum l y := by
  induction l with
  | nil => simp [marginalNum]
  | cons p rest ih =>
    obtain ⟨f, n⟩ := p
    simp only [marginalNum]
    have hn : 0 ≤ n := h (f, n) (by simp)
    have h1 := Int.mul_le_mul_of_nonneg_right (slice_mono f (rest.head?.map Prod.fst) hxy) hn
    have h2 := ih (fun p hp => h p (by simp [hp]))
    omega

theorem marginal_mono (t : QtyTable) (h : ∀ p ∈ t.steps, 0 ≤ p.2) (hd : 0 < t.den) {x y : Int} (hxy : x ≤ y) :
    t.marginal x ≤ t.marginal y :=
  divR_mono .down t.den hd (Or.inl rfl) (marginalNum_mono t.steps h hxy)

/-- One step from 0, no band, no started steps: `⌊pos q × num / den⌋` (R5 GE land tax, DZ taxe foncière). -/
theorem amount_flat (num den q : Int) : ({ steps := [(0, num)], den } : QtyTable).amount q = divR .down (pos q * num) den := by
  simp [amount, counted, band, marginal, marginalNum, slice]

end QtyTable

/-! ## A tax per square metre -/

def AssetKind.name : AssetKind → String
  | .home => "home" | .realEstate => "realEstate" | .land => "land" | .listedShares => "listedShares"
  | .unlistedShares => "unlistedShares" | .bonds => "bonds" | .deposits => "deposits" | .business => "business"
  | .pensionFund => "pensionFund" | .vehicle => "vehicle" | .other => "other"

theorem AssetKind.ofString_name (k : AssetKind) : AssetKind.ofString k.name = k := by cases k <;> rfl

structure AreaTax where
  name : String := "property tax"
  /-- the asset kinds taxed -/
  kinds : List AssetKind := [.home, .realEstate, .land]
  /-- the table on the area (m²) -/
  table : QtyTable := {}
  /-- a table by asset (kind, region, …), where it gives one -/
  tableFor : Asset → Option QtyTable := fun _ => none
  oecd : Oecd := .propertyRecurrent
  level : Level := .local
  /-- the charge's event is `"<event> <i>"`, `i` the asset's position (1-based) -/
  event : String := "asset"
  statute : String := ""
  deriving Inhabited

namespace AreaTax

def tableOf (t : AreaTax) (a : Asset) : QtyTable := (t.tableFor a).getD t.table

/-- One charge per asset of `kinds` with an area > 0: base = relieved = the area, due = the table's amount. -/
def charges (t : AreaTax) (g : CanonGlobal) : List Charge :=
  ((assetsArea g).zipIdx.filter fun ((a, ar), _) => t.kinds.contains a.kind && decide (0 < ar)).map fun ((a, ar), i) =>
    charge t.oecd t.name ar pos (t.tableOf a).amount (event := s!"{t.event} {i + 1}") (level := t.level)
      (statute := t.statute)

/-- The assets of `kinds` without an area, for the model's `unsupported` (the scorer's grade-C form). -/
def unknown (t : AreaTax) (g : CanonGlobal) : List String :=
  ((assetsArea g).zipIdx.filter fun ((a, ar), _) => t.kinds.contains a.kind && decide (ar ≤ 0)).map fun ((a, _), i) =>
    s!"{t.oecd.code} {t.name}: asset {i + 1} ({a.kind.name}) has no areaM2 (grade C)"

def family (t : AreaTax) : Family :=
  { name := s!"{t.oecd.code} {t.name}", covers := [t.oecd], run := fun _ g _ => t.charges g }

/-- No asset with an area: no charge. -/
theorem charges_noArea (t : AreaTax) (g : CanonGlobal) (h : ∀ p ∈ assetsArea g, p.2 ≤ 0) : t.charges g = [] := by
  unfold charges
  rw [List.map_eq_nil_iff, List.filter_eq_nil_iff]
  intro ⟨⟨a, ar⟩, i⟩ hm
  have := h (a, ar) (List.fst_mem_of_mem_zipIdx hm)
  simp only [Bool.and_eq_true, decide_eq_true_eq, not_and]
  intro _; omega

end AreaTax

end TaxKernel.Global
