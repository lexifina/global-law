import TaxKernel.Global2.Zone

/-!
# TaxKernel.Global2.LocalRate (2.8.0, 2026-11-21): local taxes whose rate each municipality sets, a declared rate input

Recurrent property taxes, local business taxes and some vehicle taxes are levied at a rate each municipality sets inside
a national framework (DE GrStG § 25 and GewStG § 16 Hebesatz, PT CIMI art. 112 IMI 0,3 %-0,45 %, FR taux votés, IT IMU
aliquota, US mill rates). The national framework (base, reliefs, the legal minimum and maximum rate) is statute; the rate
is a fact of the entity's municipality. The DE pilot read it from a `deHebesatz` input; 2.8.0 generalises that. **The
kernel never has a rate of its own.**

**The input** (optional): `"localRates": {"<taxKey>": {"rate": 0.3, "source": "…", "date": "2025-01-01", "municipality":
"Lisboa"}}` at the top of the line (else `company.localRates`, else `household.localRates`); per key a record or a plain
number ≥ 0 (source "input"). The number is read exactly (0.3 = 3/10) **in the tax's unit** (`unit := .percent`:
a Hebesatz of 470 is 470 %; `.permille`: a mill rate; `.bp`; `.perUnit`: money per unit of the base, e.g. per m²). An asset
record may carry its own `"localRates"` (an asset in another municipality): it wins over the entity's for that asset.
`inputAlias` reads an older top-level number (the DE pilot's `"deHebesatz"`) when `localRates` does not give the key.

**The tax** (`LocalTax`): `key`, `name`, `base` (`.assets kinds`: each asset's statutory value, assessed else market;
`.annualValue kinds`; `.area kinds`: `"areaM2"`; `.amount f`: one amount the model computes, e.g. the GewSt
Steuermessbetrag), reliefs (`ratioNum/ratioDen` the statutory ratio (Steuermesszahl, assessment ratio), then `exempt`, and
`homeExempt` more for a home), the statutory range `minNum/minDen` … `maxNum/maxDen` in the unit (−1: none), `round`.
tax = round(⌊relieved × rate / scale⌋), scale 100 (percent), 1000 (permille), 10000 (bp), 1 (per unit).

**The rate, in order** (`LocalTax.resolve`):
1. the entity's (or the asset's) `localRates.<key>` (else `inputAlias`);
2. else a rate the model declares, `LocalRateDecl := { municipality, num, den, source, date }` (`source` and `date` have no
   default): `byRegion` for the item's region (the asset's `region`, the company's `region`), else `default` when the item
   gives no region or is in the default's municipality (the statute names the convention);
3. else **no charge, grade C**: "4100 IMI: asset 1 (home): localRates.imi not given (the municipality's rate, within 0,3 %
   to 0,45 %) (grade C)".

**A rate outside the statutory range is flagged, never used or clamped**: no charge, "…: localRates.imi 0,5 % is outside
the statutory range 0,3 % to 0,45 % (grade C)" (a declared rate likewise). **Framework only** (`frameworkOnly := true`,
or `LocalTax.framework key name …`): where only the range is known the model books no number, one grade-C note with the
range per item (`unknown`).

One charge per item with a rate: `base` the value (or area, or amount), `relieved` after the ratio and exemptions, `due`
the tax, level local, statute = the tax's statute and "rate 470 % (Berlin, <source>, <date>; localRates)".
`GlobalModel.withLocalTaxes m [t]` adds the family and the grade-C lines.

Theorems: `resolveWith_input` (a given rate in range is used, whatever the model declares), `resolveWith_outOfRange`,
`resolveWith_none` (no input and no declared rate: no rate), `resolveWith_framework`, `taxAt_zero`, `taxAt_mono`
(a higher rate never lowers the tax), `LocalTax.charges_ofCanon` (asset bases: a 1.x household is untouched),
`withLocalTaxes_pit`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-- The unit a local rate is given in. -/
inductive RateUnit where
  /-- percent (a Hebesatz 470 = 470 %; an IMI 0.3 = 0,3 %) -/
  | percent
  /-- per mille (a mill rate) -/
  | permille
  /-- basis points -/
  | bp
  /-- money per unit of the base (per m², per unit of a basic amount) -/
  | perUnit
  deriving Repr, DecidableEq, Inhabited, BEq

def RateUnit.scale : RateUnit → Int
  | .percent => 100 | .permille => 1000 | .bp => 10000 | .perUnit => 1

def RateUnit.sign : RateUnit → String
  | .percent => " %" | .permille => " ‰" | .bp => " bp" | .perUnit => " per unit"

theorem RateUnit.scale_pos (u : RateUnit) : 0 < u.scale := by cases u <;> decide

/-- A local rate, `num / den` in the tax's unit, and where it comes from. -/
structure LocalRateDecl where
  /-- the municipality (or district) that set it -/
  municipality : String
  num : Int
  den : Int := 1
  /-- the act, ordinance or publication -/
  source : String
  /-- the date of the act or the date it applies from (ISO) -/
  date : String
  deriving Repr, Inhabited, BEq, DecidableEq

namespace LocalRateDecl

def valid (r : LocalRateDecl) : Bool := decide (0 ≤ r.num) && decide (0 < r.den)

/-- The rate as text (`0.3`, `470`). -/
def text (r : LocalRateDecl) : String :=
  ({ currency := "-", num := r.num, den := r.den, source := "", date := "" } : FxRate).rateText

/-- What the charge's statute says about the rate. -/
def note (r : LocalRateDecl) (u : RateUnit) (how : String) : String :=
  let src := ", ".intercalate ([r.municipality, r.source, r.date].filter (· != ""))
  s!"rate {r.text}{u.sign} (" ++ (if src.isEmpty then "" else src ++ "; ") ++ how ++ ")"

end LocalRateDecl

/-! ## The input -/

/-- The `"localRates"` object of a record (`null`: none). -/
def localRatesOf (j : Json) : Json :=
  match j.getObjVal? "localRates" with
  | .ok o => o
  | .error _ => Json.null

/-- The entity's `"localRates"`: top level, else `company.localRates`, else `household.localRates`. -/
def localRatesJson (g : CanonGlobal) : Json :=
  match g.raw.getObjVal? "localRates" with
  | .ok j => j
  | .error _ =>
    let sub (k : String) : Option Json := match g.raw.getObjVal? k with
      | .ok o => match o.getObjVal? "localRates" with | .ok j => some j | .error _ => none
      | .error _ => none
    match sub "company" with
    | some j => j
    | none => (sub "household").getD Json.null

/-- An entry: a number ≥ 0, or `{ "rate": n, "source", "date", "municipality" }`; `none`: not a rate. -/
def localRateOfJson (j : Json) : Option LocalRateDecl :=
  let mk (n : JsonNumber) (m src date : String) : Option LocalRateDecl :=
    let r : LocalRateDecl := { municipality := m, num := n.mantissa, den := (10 : Int) ^ n.exponent, source := src, date }
    if r.valid then some r else none
  match j with
  | .num n => mk n "" "input" ""
  | .obj _ => match j.getObjVal? "rate" with
    | .ok (.num n) => mk n (strField j "municipality") (strField j "source" "input") (strField j "date")
    | _ => none
  | _ => none

/-- The entry for `key` in a `"localRates"` object: `none` not given; `some none` given but not a rate. -/
def localEntry? (lr : Json) (key : String) : Option (Option LocalRateDecl) :=
  match lr.getObjVal? key with
  | .ok j => some (localRateOfJson j)
  | .error _ => none

/-! ## The tax -/

/-- What a local tax is levied on. -/
inductive LocalBase where
  /-- each asset of these kinds: its statutory value (assessed where given, else market value) -/
  | assets (kinds : List AssetKind)
  /-- each asset of these kinds: its annual value (`"annualValue"`; not given: grade C) -/
  | annualValue (kinds : List AssetKind)
  /-- each asset of these kinds: its `"areaM2"` (not given: grade C) -/
  | area (kinds : List AssetKind)
  /-- one amount the model computes (`none`: the tax does not apply to the entity) -/
  | amount (f : CanonGlobal → Option Int)
  deriving Inhabited

/-- How the rate was resolved. -/
inductive LocalRateRes where
  | rate (r : LocalRateDecl) (how : String)
  | outOfRange (r : LocalRateDecl) (how : String)
  | unknown (why : String)
  deriving Repr, Inhabited, BEq

/-- One item a local tax reads: an asset, or the entity's amount. -/
structure LocalItem where
  event : String
  base : Int
  relieved : Int
  /-- the asset's record (its own `"localRates"`), `null` for an amount -/
  record : Json := Json.null
  /-- the item's municipality (`""`: not given) -/
  region : String := ""
  /-- a fact the base needs and the item does not give (`""`: none) -/
  missing : String := ""
  deriving Inhabited

structure LocalTax where
  /-- the key in `"localRates"` -/
  key : String
  name : String
  base : LocalBase
  unit : RateUnit := .percent
  /-- statutory ratio on the value (Steuermesszahl, assessment ratio), `ratioNum / ratioDen` -/
  ratioNum : Int := 1
  ratioDen : Int := 1
  /-- exempt amount after the ratio -/
  exempt : Int := 0
  /-- further exempt amount for an asset of kind home -/
  homeExempt : Int := 0
  /-- the statutory range, in the unit (−1: none) -/
  minNum : Int := -1
  minDen : Int := 1
  maxNum : Int := -1
  maxDen : Int := 1
  /-- the model's default municipality rate (source and date required) -/
  default : Option LocalRateDecl := none
  /-- declared rates by municipality, matched against the item's region -/
  byRegion : List LocalRateDecl := []
  /-- only the range is known: never a number, a grade-C note with the range -/
  frameworkOnly : Bool := false
  /-- an older top-level number field read as the rate (`"deHebesatz"`), `""`: none -/
  inputAlias : String := ""
  /-- the region of an `.amount` item -/
  regionOf : CanonGlobal → String := fun g => g.company.region
  round : Rule := {}
  oecd : Oecd := .propertyRecurrent
  level : Level := .local
  /-- an asset charge's event is `"<event> <i>"` (1-based); an amount's is `amountEvent` -/
  event : String := "asset"
  amountEvent : String := "year"
  statute : String := ""
  deriving Inhabited

/-- `x × num / (den × scale)`, rounded down: the tax on a relieved base at a rate. -/
def taxAt (u : RateUnit) (relieved num den : Int) : Int := divR .down (relieved * num) (den * u.scale)

theorem taxAt_zero (u : RateUnit) (relieved den : Int) : taxAt u relieved 0 den = 0 := by
  simp [taxAt, divR]

/-- **A higher rate never lowers the tax** (same denominator, non-negative base). -/
theorem taxAt_mono (u : RateUnit) (relieved den : Int) {n₁ n₂ : Int} (hb : 0 ≤ relieved) (hd : 0 < den)
    (h : n₁ ≤ n₂) : taxAt u relieved n₁ den ≤ taxAt u relieved n₂ den := by
  unfold taxAt
  have hs := u.scale_pos
  exact divR_mono .down (den * u.scale) (Int.mul_pos hd hs) (Or.inl rfl) (Int.mul_le_mul_of_nonneg_left h hb)

namespace LocalTax

/-- A rate within the statutory range. -/
def inRange (t : LocalTax) (r : LocalRateDecl) : Bool :=
  (decide (t.minNum < 0) || decide (t.minNum * r.den ≤ r.num * t.minDen))
    && (decide (t.maxNum < 0) || decide (r.num * t.maxDen ≤ t.maxNum * r.den))

def boundText (t : LocalTax) (n d : Int) : String :=
  ({ municipality := "", num := n, den := d, source := "", date := "" } : LocalRateDecl).text ++ t.unit.sign

/-- The statutory range as text (`""`: none). -/
def rangeText (t : LocalTax) : String :=
  if 0 ≤ t.minNum && 0 ≤ t.maxNum then s!"within {t.boundText t.minNum t.minDen} to {t.boundText t.maxNum t.maxDen}"
  else if 0 ≤ t.minNum then s!"at least {t.boundText t.minNum t.minDen}"
  else if 0 ≤ t.maxNum then s!"at most {t.boundText t.maxNum t.maxDen}"
  else ""

def rangeParen (t : LocalTax) : String := if t.rangeText.isEmpty then "" else ", " ++ t.rangeText

/-- The rate given for an item: the asset's own `localRates`, else the entity's, else the alias field. -/
def given? (t : LocalTax) (g : CanonGlobal) (record : Json) : Option (Option LocalRateDecl × String) :=
  match localEntry? (localRatesOf record) t.key with
  | some e => some (e, "asset localRates")
  | none =>
    match localEntry? (localRatesJson g) t.key with
    | some e => some (e, "localRates")
    | none =>
      if t.inputAlias == "" then none else
      match g.raw.getObjVal? t.inputAlias with
      | .ok j => some (localRateOfJson j, t.inputAlias)
      | .error _ => none

/-- **The rate**, from what the item is given (`given?`) and its region. -/
def resolveWith (t : LocalTax) (gv : Option (Option LocalRateDecl × String)) (region : String) : LocalRateRes :=
  if t.frameworkOnly then
    .unknown s!"framework only: the municipality sets the rate{t.rangeParen}; not computed"
  else
  match gv with
  | some (some r, how) => if t.inRange r then .rate r how else .outOfRange r how
  | some (none, how) =>
    .unknown s!"{how}.{t.key} is not a rate (a number ≥ 0 or {"{"}rate, source, date, municipality})"
  | none =>
    let decl : Option (LocalRateDecl × String) :=
      if region != "" then
        match (t.byRegion ++ t.default.toList).find? (·.municipality == region) with
        | some d => some (d, s!"the model's rate for {region}")
        | none => none
      else match t.default with
        | some d => some (d, s!"the model's default municipality {d.municipality}")
        | none => none
    match decl with
    | some (d, how) => if d.valid && t.inRange d then .rate d how else .outOfRange d how
    | none =>
      if region != "" && (t.default.isSome || !t.byRegion.isEmpty) then
        .unknown s!"no declared rate for municipality {region}: localRates.{t.key} not given{t.rangeParen}"
      else .unknown s!"localRates.{t.key} not given (the municipality's rate{t.rangeParen})"

def resolve (t : LocalTax) (g : CanonGlobal) (it : LocalItem) : LocalRateRes :=
  t.resolveWith (t.given? g it.record) it.region

/-- After the ratio and the exemptions. -/
def relievedOf (t : LocalTax) (v : Int) (home : Bool) : Int :=
  pos (divR .down (pos v * t.ratioNum) t.ratioDen - t.exempt - (if home then t.homeExempt else 0))

/-- The items the tax reads. -/
def items (t : LocalTax) (g : CanonGlobal) : List LocalItem :=
  let assetItems (kinds : List AssetKind) (val : Asset → Nat → Option Int) (what : String) : List LocalItem :=
    (g.assets.zipIdx.filter fun (a, _) => kinds.contains a.kind).map fun (a, i) =>
      let ev := s!"{t.event} {i + 1}"
      match val a i with
      | some v => { event := ev, base := v, relieved := t.relievedOf v (a.kind == .home), record := assetJson g i,
                    region := a.region }
      | none => { event := ev, base := 0, relieved := 0, record := assetJson g i, region := a.region,
                  missing := s!"{a.kind.name}: {what} not given" }
  match t.base with
  | .assets ks => assetItems ks (fun a _ => some a.statutoryValue) "value"
  | .annualValue ks => assetItems ks (fun a _ => if 0 ≤ a.annualValue then some a.annualValue else none) "annualValue"
  | .area ks => assetItems ks (fun _ i => let ar := assetAreaM2 g i; if 0 < ar then some ar else none) "areaM2"
  | .amount f =>
    match f g with
    | some v => [{ event := t.amountEvent, base := v, relieved := t.relievedOf v false, region := t.regionOf g }]
    | none => []

/-- The tax on an item at a rate. -/
def amountAt (t : LocalTax) (it : LocalItem) (r : LocalRateDecl) : Int := t.round.apply (taxAt t.unit it.relieved r.num r.den)

def charges (t : LocalTax) (g : CanonGlobal) : List Charge :=
  (t.items g).filterMap fun it =>
    if it.missing != "" then none else
    match t.resolve g it with
    | .rate r how =>
      some (charge t.oecd t.name it.base (fun _ => it.relieved) (fun _ => t.amountAt it r) (event := it.event)
        (level := t.level) (statute := "; ".intercalate ([t.statute, r.note t.unit how].filter (· != ""))))
    | _ => none

/-- The items the tax cannot compute, for `unsupported` (grade C). -/
def unknown (t : LocalTax) (g : CanonGlobal) : List String :=
  (t.items g).filterMap fun it =>
    let pre := s!"{t.oecd.code} {t.name}: {it.event}"
    if it.missing != "" then some s!"{pre} ({it.missing}) (grade C)" else
    match t.resolve g it with
    | .rate _ _ => none
    | .outOfRange r how =>
      some s!"{pre}: {how} {r.text}{t.unit.sign} is outside the statutory range ({t.rangeText}) (grade C)"
    | .unknown why => some s!"{pre}: {why} (grade C)"

def family (t : LocalTax) : Family :=
  { name := s!"{t.oecd.code} {t.name}", covers := [t.oecd], run := fun _ g _ => t.charges g }

/-- A framework-only tax: the range and the statute, no number. -/
def framework (key name : String) (base : LocalBase) (unit : RateUnit) (minNum minDen maxNum maxDen : Int)
    (statute : String) (oecd : Oecd := .propertyRecurrent) : LocalTax :=
  { key, name, base, unit, minNum, minDen, maxNum, maxDen, statute, oecd, frameworkOnly := true }

/-! ### Theorems -/

/-- **The entity's rate wins**: a given rate within the range is the rate, whatever the model declares. -/
theorem resolveWith_input (t : LocalTax) (r : LocalRateDecl) (how region : String) (hf : t.frameworkOnly = false)
    (h : t.inRange r = true) : t.resolveWith (some (some r, how)) region = .rate r how := by
  simp [resolveWith, hf, h]

/-- **Out of range: flagged, never used.** -/
theorem resolveWith_outOfRange (t : LocalTax) (r : LocalRateDecl) (how region : String) (hf : t.frameworkOnly = false)
    (h : t.inRange r = false) : t.resolveWith (some (some r, how)) region = .outOfRange r how := by
  simp [resolveWith, hf, h]

/-- **Never a rate of its own**: no input and no declared rate, no rate. -/
theorem resolveWith_none (t : LocalTax) (region : String) (hd : t.default = none) (hb : t.byRegion = []) :
    ∃ why, t.resolveWith none region = .unknown why := by
  unfold resolveWith
  split
  · exact ⟨_, rfl⟩
  · simp [hd, hb]

/-- A framework-only tax never gives a rate. -/
theorem resolveWith_framework (t : LocalTax) (gv : Option (Option LocalRateDecl × String)) (region : String)
    (hf : t.frameworkOnly = true) : ∃ why, t.resolveWith gv region = .unknown why := by
  simp [resolveWith, hf]

/-- Only a resolved rate is charged. -/
theorem charges_rate (t : LocalTax) (g : CanonGlobal)
    (h : ∀ it ∈ t.items g, ∀ r how, t.resolve g it ≠ .rate r how) : t.charges g = [] := by
  unfold charges
  rw [List.filterMap_eq_nil_iff]
  intro it hit
  split
  · rfl
  · split
    · rename_i r how hr; exact absurd hr (h it hit r how)
    all_goals rfl

/-- A 1.x household (no assets) is untouched by a tax on assets. -/
theorem charges_ofCanon (t : LocalTax) (c : Canon) (ks : List AssetKind)
    (hb : t.base = .assets ks ∨ t.base = .annualValue ks ∨ t.base = .area ks) :
    t.charges (CanonGlobal.ofCanon c) = [] := by
  rcases hb with hb | hb | hb <;> simp [charges, items, hb, CanonGlobal.ofCanon]

end LocalTax

/-- The local-tax family of several taxes. -/
def localTaxFamily (ts : List LocalTax) (name : String := "local taxes at the municipality's rate") : Family :=
  { name, covers := (ts.map (·.oecd)).eraseDups, run := fun _ g _ => ts.flatMap (·.charges g) }

/-- **Local taxes on a model**: the family last, and the grade-C lines after the model's own `unsupported`. -/
def GlobalModel.withLocalTaxes (m : GlobalModel) (ts : List LocalTax)
    (name : String := "local taxes at the municipality's rate") : GlobalModel :=
  { m with families := m.families ++ [localTaxFamily ts name],
           unsupported := fun args g => m.unsupported args g ++ ts.flatMap (·.unknown g) }

theorem withLocalTaxes_pit (m : GlobalModel) (ts : List LocalTax) (n : String) (args : List String) (g : CanonGlobal) :
    ((m.withLocalTaxes ts n).computeGlobal args g).pit = (m.computeGlobal args g).pit := rfl

end TaxKernel.Global
