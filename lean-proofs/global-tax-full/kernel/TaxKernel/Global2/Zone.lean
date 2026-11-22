import TaxKernel.Global2.Fx

/-!
# TaxKernel.Global2.Zone (2.7.0, 2026-11-21; 2.8.0): zone value ("objective value") and coefficients on real estate (R1 Europe pass 15)

GR ν. 4223/2013 art. 4 (ENFIA): the principal tax on a building is its floor area × the basic tax per m² of the band of
the property's zone price (τιμή ζώνης, euros per m²) × coefficients for age, floor, frontage and use; land likewise by
zone value. Many cadastral systems value property as area × an official price per m² × coefficients ("objective
value") and tax that value on a schedule. 2.4.0 gave `"areaM2"`; the band needs the zone price, the coefficients more
facts.

**Asset facts** (optional fields on the asset record, read like `"areaM2"`; `AssetFact`):

| JSON field | `AssetFact` | meaning (not given: absent, or as shown) |
|---|---|---|
| `"areaM2"` | `areaM2` | floor area (plot area for land), m² (given when > 0) |
| `"zoneValueM2"` | `zoneValueM2` | the official zone price per m² (τιμή ζώνης; given when ≥ 0); `assetZoneValueM2 g i` (−1: not given) |
| `"buildYear"` | `buildYear`, `age` | year of construction (given when > 0); age = tax year − it, at least 0 |
| `"floor"` | `floor` | floor (0 ground, negative below ground; given when present) |
| `"frontages"` | `frontages` | number of street frontages (given when ≥ 0) |
| any other number | `field key` | a number the coefficient table names (`.field "useCode"`) |

**The tax** (`ZoneTax`), one charge per asset of `kinds`:
* `base := .perArea bands`: `bands := [(zone value from, table on m²), …]`, the table of the highest band whose `from`
  ≤ the zone value (none reached: no tax for the asset, 0); amount = table(area) × Π coefficients;
* `base := .onValue table`: objective value = area × zone value × Π coefficients; amount = table(objective value);
* `coefs := [{ fact, bands := [(from, factor bp), …] }]`: each the factor of the highest band whose `from` ≤ the fact
  (none reached: 10000); `coefsFor` per asset (kind, region) where the coefficients differ (buildings and land).

**2.8.0 (R1 Europe pass 17): coefficients chosen from the asset's record.** `coefsAt g i a` (default `none`) gives the
coefficient list of asset `i` from anything its record holds (`assetFact? g i (.field "detached")`), before `coefsFor` and
`coefs`: GR ΕΝ.Φ.Ι.Α. άρθ. 4 Α παρ. 2 ε, a detached house takes Σ.Μ. 1,02 instead of the floor coefficient:
`coefsAt := fun g i _ => if assetFact? g i (.field "detached") == some 1 then some detachedCoefs else none`. The facts
an asset needs are those of its own list (`needsAt`; a detached house needs no floor). `needsAt_default`,
`coefsAtOf_default` (without `coefsAt`: as 2.7.0).

Everything is multiplied exactly and rounded down once (then `round`). **A fact the tax reads that the asset does not
give: no charge for it, `unknown` lists `"<code> <name>: asset <i> (<kind>): zoneValueM2, buildYear not given (grade C)"`**:
never guessed. Theorems: `ZoneTax.charges_noFacts` (an asset without every fact is not charged), `charges_ofCanon` (a
1.x household is untouched), `unknown_ofCanon`, `coefBp_nil`, `factor_nil`, `assetFact?_null`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-- 2.7.0: a fact of a real-estate asset. -/
inductive AssetFact where
  | areaM2 | zoneValueM2 | buildYear | age | floor | frontages
  /-- any other number of the asset record -/
  | field (key : String)
  deriving Repr, DecidableEq, Inhabited, BEq

def AssetFact.name : AssetFact → String
  | .areaM2 => "areaM2" | .zoneValueM2 => "zoneValueM2" | .buildYear => "buildYear" | .age => "age"
  | .floor => "floor" | .frontages => "frontages" | .field k => k

/-- A number of a record (`none`: absent or not a number). -/
def jsonNum? (j : Json) (k : String) : Option Int :=
  match j.getObjVal? k with
  | .ok (.num n) => some (numToInt n)
  | _ => none

/-- The zone price per m² of asset `i` (−1: not given). -/
def assetZoneValueM2 (g : CanonGlobal) (i : Nat) : Int :=
  match jsonNum? (assetJson g i) "zoneValueM2" with
  | some x => if 0 ≤ x then x else -1
  | none => -1

/-- **A fact of asset `i`** (`none`: not given). -/
def assetFact? (g : CanonGlobal) (i : Nat) : AssetFact → Option Int
  | .areaM2 => let a := assetAreaM2 g i; if 0 < a then some a else none
  | .zoneValueM2 => let z := assetZoneValueM2 g i; if 0 ≤ z then some z else none
  | .buildYear => (jsonNum? (assetJson g i) "buildYear").filter (0 < ·)
  | .age => ((jsonNum? (assetJson g i) "buildYear").filter (0 < ·)).map fun y => pos ((g.year : Int) - y)
  | .floor => jsonNum? (assetJson g i) "floor"
  | .frontages => (jsonNum? (assetJson g i) "frontages").filter (0 ≤ ·)
  | .field k => jsonNum? (assetJson g i) k

theorem assetFact?_null (g : CanonGlobal) (i : Nat) (f : AssetFact) (h : assetJson g i = Json.null) :
    assetFact? g i f = none := by
  cases f <;> simp [assetFact?, assetAreaM2, assetZoneValueM2, jsonNum?, intField, h, Json.getObjVal?] <;> rfl

/-- A coefficient: the factor (bp) of the highest band whose `from` ≤ the fact; none reached: 10000. -/
structure FactCoef where
  fact : AssetFact
  bands : List (Int × Int)
  deriving Repr, Inhabited, BEq

def FactCoef.bpOf (c : FactCoef) (x : Int) : Int := c.bands.foldl (fun acc (f, b) => if f ≤ x then b else acc) 10000

/-- What the tax is computed on. -/
inductive ZoneBase where
  /-- area × the per-m² table of the zone value's band (`(zone value from, table on m²)`) -/
  | perArea (bands : List (Int × QtyTable))
  /-- a table on the objective value, area × zone value (× the coefficients) -/
  | onValue (table : QtyTable)
  deriving Repr, Inhabited

structure ZoneTax where
  name : String := "property tax"
  kinds : List AssetKind := [.home, .realEstate]
  base : ZoneBase
  coefs : List FactCoef := []
  /-- coefficients by asset (kind, region …), where they differ from `coefs` -/
  coefsFor : Asset → Option (List FactCoef) := fun _ => none
  round : Rule := {}
  oecd : Oecd := .propertyRecurrent
  level : Level := .central
  /-- the charge's event is `"<event> <i>"` (1-based position of the asset) -/
  event : String := "asset"
  statute : String := ""
  /-- 2.8.0: the coefficients of asset `i` from its record (`none`: `coefsFor`, else `coefs`) -/
  coefsAt : CanonGlobal → Nat → Asset → Option (List FactCoef) := fun _ _ _ => none
  deriving Inhabited

namespace ZoneTax

def coefsOf (t : ZoneTax) (a : Asset) : List FactCoef := (t.coefsFor a).getD t.coefs

/-- 2.8.0: the coefficients of asset `i`: `coefsAt`, else `coefsOf`. -/
def coefsAtOf (t : ZoneTax) (g : CanonGlobal) (a : Asset) (i : Nat) : List FactCoef :=
  match t.coefsAt g i a with
  | some l => l
  | none => t.coefsOf a

theorem coefsAtOf_default (t : ZoneTax) (g : CanonGlobal) (a : Asset) (i : Nat) (h : t.coefsAt g i a = none) :
    t.coefsAtOf g a i = t.coefsOf a := by simp [coefsAtOf, h]

/-- The facts the tax reads for an asset. -/
def needs (t : ZoneTax) (a : Asset) : List AssetFact :=
  ([AssetFact.areaM2, .zoneValueM2] ++ (t.coefsOf a).map (·.fact)).eraseDups

/-- 2.8.0: the facts the tax reads for asset `i` (its own coefficient list). -/
def needsAt (t : ZoneTax) (g : CanonGlobal) (a : Asset) (i : Nat) : List AssetFact :=
  ([AssetFact.areaM2, .zoneValueM2] ++ (t.coefsAtOf g a i).map (·.fact)).eraseDups

theorem needsAt_default (t : ZoneTax) (g : CanonGlobal) (a : Asset) (i : Nat) (h : t.coefsAt g i a = none) :
    t.needsAt g a i = t.needs a := by simp [needsAt, needs, coefsAtOf, h]

/-- The facts asset `i` does not give. -/
def missing (t : ZoneTax) (g : CanonGlobal) (a : Asset) (i : Nat) : List AssetFact :=
  (t.needsAt g a i).filter fun f => (assetFact? g i f).isNone

/-- Π of the coefficients' factors (numerator) and `BP ^ count` (denominator). -/
def factor (t : ZoneTax) (g : CanonGlobal) (a : Asset) (i : Nat) : Int × Int :=
  (t.coefsAtOf g a i).foldl (fun (n, d) c => (n * c.bpOf ((assetFact? g i c.fact).getD 0), d * BP)) (1, 1)

/-- The table of the zone value's band (`none`: below every band). -/
def bandTable (bands : List (Int × QtyTable)) (z : Int) : Option QtyTable :=
  bands.foldl (fun acc (f, tb) => if f ≤ z then some tb else acc) none

/-- (base shown on the charge, amount) for asset `i` with area `ar` and zone value `z`. -/
def compute (t : ZoneTax) (g : CanonGlobal) (a : Asset) (i : Nat) (ar z : Int) : Int × Int :=
  let (n, d) := t.factor g a i
  match t.base with
  | .perArea bands =>
    match bandTable bands z with
    | some tb => (ar, t.round.apply (tb.amountAt n d ar))
    | none => (ar, 0)
  | .onValue tb =>
    let ov := divR .down (ar * z * n) d
    (ov, t.round.apply (tb.amount ov))

/-- One charge per asset of `kinds` that gives every fact the tax reads. -/
def charges (t : ZoneTax) (g : CanonGlobal) : List Charge :=
  (g.assets.zipIdx.filter fun (a, i) => t.kinds.contains a.kind && (t.missing g a i).isEmpty).map fun (a, i) =>
    let ar := (assetFact? g i .areaM2).getD 0
    let z := (assetFact? g i .zoneValueM2).getD 0
    let r := t.compute g a i ar z
    charge t.oecd t.name r.1 pos (fun _ => r.2) (event := s!"{t.event} {i + 1}") (level := t.level)
      (statute := t.statute)

/-- The assets of `kinds` the tax cannot compute, for `unsupported` (grade C). -/
def unknown (t : ZoneTax) (g : CanonGlobal) : List String :=
  (g.assets.zipIdx.filter fun (a, i) => t.kinds.contains a.kind && !(t.missing g a i).isEmpty).map fun (a, i) =>
    s!"{t.oecd.code} {t.name}: asset {i + 1} ({a.kind.name}): {", ".intercalate ((t.missing g a i).map (·.name))} not given (grade C)"

def family (t : ZoneTax) : Family :=
  { name := s!"{t.oecd.code} {t.name}", covers := [t.oecd], run := fun _ g _ => t.charges g }

theorem factor_nil (t : ZoneTax) (g : CanonGlobal) (a : Asset) (i : Nat) (h : t.coefsOf a = [])
    (ha : t.coefsAt g i a = none) : t.factor g a i = (1, 1) := by simp [factor, coefsAtOf, h, ha]

theorem coefBp_nil (f : AssetFact) (x : Int) : ({ fact := f, bands := [] } : FactCoef).bpOf x = 10000 := rfl

/-- **Never guessed**: an asset that does not give every fact the tax reads is not charged. -/
theorem charges_noFacts (t : ZoneTax) (g : CanonGlobal) (h : ∀ p ∈ g.assets.zipIdx, (t.missing g p.1 p.2).isEmpty = false) :
    t.charges g = [] := by
  unfold charges
  rw [List.map_eq_nil_iff, List.filter_eq_nil_iff]
  intro p hp
  simp [h p hp]

/-- A 1.x household (no assets) is untouched. -/
theorem charges_ofCanon (t : ZoneTax) (c : Canon) : t.charges (CanonGlobal.ofCanon c) = [] := by
  simp [charges, CanonGlobal.ofCanon]

theorem unknown_ofCanon (t : ZoneTax) (c : Canon) : t.unknown (CanonGlobal.ofCanon c) = [] := by
  simp [unknown, CanonGlobal.ofCanon]

end ZoneTax

end TaxKernel.Global
