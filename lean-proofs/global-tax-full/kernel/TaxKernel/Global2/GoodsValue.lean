import TaxKernel.Global2.Customs

/-!
# TaxKernel.Global2.GoodsValue (2.9.0, 2026-11-21): container size and the manufacturer's value on basket lines

Two facts a basket line could not carry (KERNEL_REQUESTS.md R3-GAP-2; PROGRESS_ASIAPAC MY 5112, MM specific goods tax):

* **R3-GAP-2, the container**: Hong Kong's liquor duty (Dutiable Commodities Ordinance Cap. 109 Sch. 1 Part I para. 1A, from
  16 Oct 2024) is 100 % of the first $200 of the value **of each container** of not more than 1 litre and 10 % of the rest;
  above 1 litre it is per litre (para. 1B-1C). A per-litre reading taxes a case of cheap bottles like one dear bottle.
* **the manufacturer's value**: MY Sales Tax Act 2018 s. 9 (5 % / 10 % on the sale value of the manufacturer), MM Union
  Taxation Law specific goods tax on the ex-factory value of local production, excises on the manufacturer's price: the
  retail price of the basket is not that value.

`Spend` and `SpendX` are unchanged: as for 2.1.0 and 2.8.0 the facts are read from the line's own JSON.

| JSON field on a `consumption` line | `LineValueX` | meaning (not given: −1) |
|---|---|---|
| `"containerMl"` | `containerMl` | the size of one container (bottle, can) in ml, > 0 |
| `"exFactoryValue"` (alias `"manufacturerValue"`) | `exFactoryValue` | the manufacturer's selling value of the line (ex-factory), money ≥ 0 |
| `"customsValue"` (2.8.0) | (`CustomsX`) | the customs value of the line |

**The tax** (`GoodsValueTax`): an ad valorem rate (`rateBp`) or **marginal value bands** (`bands := [(upTo, rateBp), …]`,
the last `upTo` −1 = the rest) on a value chosen by `value`:
`.retail` (the tax-inclusive price), `.netOfVat` (net of VAT at `vatBp`), `.beforeTax` (the value before this tax and VAT:
the price with the tax and VAT taken out, the bands inverted exactly), `.exFactory` (the line's `"exFactoryValue"`),
`.customs` (the line's `"customsValue"`); `valueImported` for imported lines; `fallback` the base used when the line does
not give the value (`none`: **grade C**, never guessed).

**Per container** (`perContainer := true`): the bands apply to the value of each container (`"containerMl"`; the
quantity in ml is the line's `quantity`, thousandths of a litre): `n = quantity / containerMl` containers, each of value
`V / n`; containers larger than `maxContainerMl` are taxed per litre. Computed exactly as
`Σ r_k · clamp(V·u − L_k·Q, 0, W_k·Q) / (u · 10 000)` (`u` the container or 1000 ml, `Q` the quantity; `bandNum`),
rounded down once. No `"containerMl"` (or no quantity) on a line the rule takes: grade C.

Selection: `goods` (`[]`: all) less `exceptGoods`, `sub`, strength `minAbvBp < abv ≤ maxAbvBp`, origin `imported`, and a
date window `validFrom ≤ date < validTo` on the line's `"date"` (an undated line under a dated rule: grade C).

One charge per line taxed: `base` = the price, `relieved` = the value taxed, `due` = the tax, event `"line <i> (<good>)"`,
bearer consumer, heading `oecd` (`.excise` 5121 by default; `.salesTax` 5112 for a manufacturer's sales tax).
`GlobalModel.withGoodsValueTaxes m [t]` adds the family and the grade-C lines.

Theorems: `bandNum_nil`, `bandNum_flat`, `bandNum_nonneg`, `dutyAt_flat`, `valueOf_given`, `valueOf_missing`,
`lineValueX_null`, `consumptionV_fst`, `GoodsValueTax.charges_ofCanon`, `unknown_ofCanon`, `withGoodsValueTaxes_pit`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-! ## The line's facts -/

/-- The container and the manufacturer's value of a basket line (2.9.0). -/
structure LineValueX where
  /-- `"containerMl"`: one container in ml (−1: not given) -/
  containerMl : Int := -1
  /-- `"exFactoryValue"` / `"manufacturerValue"`: money (−1: not given) -/
  exFactoryValue : Int := -1
  deriving Repr, Inhabited, BEq

/-- A number ≥ 0 at `k` (−1: absent, not a number or negative). -/
def nonnegField (j : Json) (k : String) : Int :=
  match j.getObjVal? k with
  | .ok (.num _) => let v := intField j k (-1); if 0 ≤ v then v else -1
  | _ => -1

def LineValueX.ofJson (j : Json) : LineValueX :=
  { containerMl := let c := nonnegField j "containerMl"; if 0 < c then c else -1,
    exFactoryValue := let v := nonnegField j "exFactoryValue"; if 0 ≤ v then v else nonnegField j "manufacturerValue" }

theorem lineValueX_null : LineValueX.ofJson Json.null = {} := rfl

/-- Each basket line with its 2.1.0 extras, its customs facts and its container and manufacturer's value. -/
def consumptionV (g : CanonGlobal) : List (Spend × SpendX × CustomsX × LineValueX) :=
  let js := (arrField g.raw "consumption").toList
  (consumptionC g).zipIdx.map fun ((s, x, c), i) => (s, x, c, LineValueX.ofJson (js.getD i Json.null))

theorem consumptionV_fst (g : CanonGlobal) : (consumptionV g).map (·.1) = g.consumption := by
  rw [← consumptionC_fst g]
  simp only [consumptionV, List.map_map, Function.comp_def]
  rw [show (fun x : (Spend × SpendX × CustomsX) × Nat => x.1.fst) = Prod.fst ∘ Prod.fst from rfl, ← List.map_map,
    List.zipIdx_map_fst]

/-! ## Value bands -/

/-- `Σ r_k · clamp(x − L_k·q, 0, W_k·q)` over the bands `(upTo, r)` from the lower bound `lo` (`upTo < 0`: the rest). -/
def bandNum : List (Int × Int) → Int → Int → Int → Int
  | [], _, _, _ => 0
  | (upTo, r) :: rest, lo, x, q =>
    if upTo < 0 then r * pos (x - lo * q)
    else r * min (pos (x - lo * q)) (pos (upTo - lo) * q) + bandNum rest upTo x q

theorem bandNum_nil (lo x q : Int) : bandNum [] lo x q = 0 := rfl

theorem bandNum_flat (r x q : Int) : bandNum [(-1, r)] 0 x q = r * pos x := by simp [bandNum]

theorem bandNum_nonneg (l : List (Int × Int)) (lo x q : Int) (hq : 0 ≤ q) (hr : ∀ p ∈ l, 0 ≤ p.2) :
    0 ≤ bandNum l lo x q := by
  induction l generalizing lo with
  | nil => simp [bandNum]
  | cons hd rest ih =>
    obtain ⟨upTo, r⟩ := hd
    have h0 : 0 ≤ r := hr (upTo, r) (by simp)
    have hrest := ih upTo (fun p hp => hr p (by simp [hp]))
    have hp1 := pos_nonneg (x - lo * q)
    have hp2 : 0 ≤ pos (upTo - lo) * q := Int.mul_nonneg (pos_nonneg _) hq
    simp only [bandNum]
    split
    · exact Int.mul_nonneg h0 hp1
    · have : 0 ≤ min (pos (x - lo * q)) (pos (upTo - lo) * q) := by omega
      have := Int.mul_nonneg h0 this
      omega

/-- The value `x` (scaled) at which `x·10 000 + bandNum(x) = y`, rounded down: the value before the tax. -/
def bandInvert : List (Int × Int) → Int → Int → Int → Int → Int
  | [], lo, acc, q, y => lo * q + divR .down (pos (y - lo * q * BP - acc)) BP
  | (upTo, r) :: rest, lo, acc, q, y =>
    let xLo := lo * q
    if upTo < 0 then xLo + divR .down (pos (y - xLo * BP - acc)) (BP + r)
    else
      let w := r * (pos (upTo - lo) * q)
      if y ≤ upTo * q * BP + acc + w then xLo + divR .down (pos (y - xLo * BP - acc)) (BP + r)
      else bandInvert rest upTo (acc + w) q y

/-! ## The tax -/

inductive GoodsValueBase where
  /-- the tax-inclusive price -/
  | retail
  /-- the price net of VAT -/
  | netOfVat
  /-- the value before this tax and VAT -/
  | beforeTax
  /-- the line's `"exFactoryValue"` / `"manufacturerValue"` -/
  | exFactory
  /-- the line's `"customsValue"` -/
  | customs
  deriving Repr, DecidableEq, Inhabited, BEq

def GoodsValueBase.text : GoodsValueBase → String
  | .retail => "the price" | .netOfVat => "the price net of VAT" | .beforeTax => "the value before the tax"
  | .exFactory => "the manufacturer's value" | .customs => "the customs value"

structure GoodsValueTax where
  name : String
  /-- the goods taxed (`[]`: every good) -/
  goods : List Good := []
  exceptGoods : List Good := []
  /-- the line's `"sub"` (`""`: any) -/
  sub : String := ""
  minAbvBp : Int := -1
  maxAbvBp : Int := 100000
  /-- `none` any origin; `some true` imported lines only; `some false` local production only -/
  imported : Option Bool := none
  value : GoodsValueBase := .beforeTax
  /-- the value for imported lines (`none`: `value`) -/
  valueImported : Option GoodsValueBase := none
  /-- the base when the line does not give an `.exFactory` / `.customs` value (`none`: grade C) -/
  fallback : Option GoodsValueBase := none
  rateBp : Int := 0
  /-- marginal bands `(upTo, rateBp)` on the value (of each container with `perContainer`); the last `upTo` −1 = the
  rest; non-empty: replaces `rateBp` -/
  bands : List (Int × Int) := []
  perContainer : Bool := false
  /-- containers larger than this (ml) are taxed per litre (−1: never) -/
  maxContainerMl : Int := -1
  /-- VAT on the tax-inclusive price, bp (`.netOfVat`, `.beforeTax`) -/
  vatBp : Int := 0
  validFrom : String := ""
  validTo : String := ""
  oecd : Oecd := .excise
  level : Level := .central
  statute : String := ""
  deriving Inhabited

/-- The tax on a value `v` taxed in units of `u` ml out of `q` ml (`u = q = 1`: the whole line), rounded down once. -/
def dutyAt (sched : List (Int × Int)) (u q v : Int) : Int := divR .down (bandNum sched 0 (v * u) q) (u * BP)

theorem dutyAt_flat (r v : Int) : dutyAt [(-1, r)] 1 1 v = divR .down (r * pos v) BP := by
  simp [dutyAt, bandNum]

namespace GoodsValueTax

def schedule (t : GoodsValueTax) : List (Int × Int) := if t.bands.isEmpty then [(-1, t.rateBp)] else t.bands

def selects (t : GoodsValueTax) (s : Spend) (x : SpendX) : Bool :=
  (t.goods.isEmpty || t.goods.contains s.good) && !t.exceptGoods.contains s.good && (t.sub == "" || t.sub == x.sub)
    && decide (t.minAbvBp < s.abvBp) && decide (s.abvBp ≤ t.maxAbvBp)
    && (match t.imported with | none => true | some b => b == x.imported)

def dated (t : GoodsValueTax) : Bool := t.validFrom != "" || t.validTo != ""

/-- The units: `(u, q, note)`: a container (or a litre above `maxContainerMl`) out of the quantity; `(1, 1)` the line. -/
def units (t : GoodsValueTax) (s : Spend) (lv : LineValueX) : Except String (Int × Int × String) :=
  if !t.perContainer then .ok (1, 1, "") else
  if lv.containerMl ≤ 0 then .error "containerMl not given (the tax is per container)" else
  if s.quantity ≤ 0 then .error "quantity not given (the tax is per container)" else
  if 0 ≤ t.maxContainerMl && t.maxContainerMl < lv.containerMl then
    .ok (1000, s.quantity, s!"containers of {lv.containerMl} ml: per litre")
  else .ok (lv.containerMl, s.quantity, s!"per container of {lv.containerMl} ml")

def netOfVat (t : GoodsValueTax) (s : Spend) : Int := divR .down (pos s.amount * BP) (BP + t.vatBp)

/-- The value on a base; `none`: the line does not give it. -/
def valueOn (t : GoodsValueTax) (b : GoodsValueBase) (s : Spend) (c : CustomsX) (lv : LineValueX) (u q : Int) :
    Option Int :=
  match b with
  | .retail => some (pos s.amount)
  | .netOfVat => some (t.netOfVat s)
  | .beforeTax => some (divR .down (bandInvert t.schedule 0 0 q (t.netOfVat s * u * BP)) u)
  | .exFactory => if 0 ≤ lv.exFactoryValue then some lv.exFactoryValue else none
  | .customs => if 0 ≤ c.customsValue then some c.customsValue else none

/-- **The value taxed** and the base it is on: the line's own value, else the declared fallback, else `none` (grade C). -/
def valueOf (t : GoodsValueTax) (s : Spend) (x : SpendX) (c : CustomsX) (lv : LineValueX) (u q : Int) :
    Option (Int × GoodsValueBase) :=
  let b := if x.imported then t.valueImported.getD t.value else t.value
  match t.valueOn b s c lv u q with
  | some v => some (v, b)
  | none => match t.fallback with
    | some f => (t.valueOn f s c lv u q).map fun v => (v, f)
    | none => none

theorem valueOf_given (t : GoodsValueTax) (s : Spend) (x : SpendX) (c : CustomsX) (lv : LineValueX) (u q : Int)
    (hx : x.imported = false) (hb : t.value = .exFactory) (hv : 0 ≤ lv.exFactoryValue) :
    t.valueOf s x c lv u q = some (lv.exFactoryValue, .exFactory) := by
  simp [valueOf, valueOn, hx, hb, hv]

/-- **The manufacturer's value is never guessed**: not given and no declared fallback, no value (grade C). -/
theorem valueOf_missing (t : GoodsValueTax) (s : Spend) (x : SpendX) (c : CustomsX) (lv : LineValueX) (u q : Int)
    (hx : x.imported = false) (hb : t.value = .exFactory) (hv : lv.exFactoryValue < 0) (hf : t.fallback = none) :
    t.valueOf s x c lv u q = none := by
  have hv' : ¬ 0 ≤ lv.exFactoryValue := by omega
  simp [valueOf, valueOn, hx, hb, hf, hv']

/-- What the tax does with one line. -/
def lineOutcome (t : GoodsValueTax) (year : Nat) (s : Spend) (x : SpendX) (c : CustomsX) (lv : LineValueX) :
    CustomsOutcome :=
  if !t.selects s x then .none else
  let inWindow : Except String Bool :=
    if !t.dated then .ok true else
    match dayOfYear? year x.date with
    | some d => .ok (inForceOn year t.validFrom t.validTo d)
    | none => .error (if x.date == "" then "no \"date\" (the rule is in force for part of the year)"
                      else s!"date \"{x.date}\" is not a date (YYYY-MM-DD)")
  match inWindow with
  | .error e => .unknown e
  | .ok false => .none
  | .ok true =>
  match t.units s lv with
  | .error e => .unknown e
  | .ok (u, q, unote) =>
  match t.valueOf s x c lv u q with
  | none =>
    let b := if x.imported then t.valueImported.getD t.value else t.value
    .unknown s!"{b.text} not given (\"{if b == .customs then "customsValue" else "exFactoryValue"}\")"
  | some (v, b) =>
    let d := dutyAt t.schedule u q v
    .due v d ("; ".intercalate ([t.statute, s!"on {b.text}", unote].filter (· != "")))

/-- One charge per line taxed. -/
def charges (t : GoodsValueTax) (g : CanonGlobal) : List Charge :=
  (consumptionV g).zipIdx.filterMap fun ((s, x, c, lv), i) =>
    match t.lineOutcome g.year s x c lv with
    | .due v d st =>
      some (charge t.oecd t.name (pos s.amount) (fun _ => v) (fun _ => d) (event := s!"line {i + 1} ({s.good.name})")
        (level := t.level) (bearer := .consumer) (statute := st))
    | _ => none

/-- The lines the tax cannot compute (grade C). -/
def unknown (t : GoodsValueTax) (g : CanonGlobal) : List String :=
  (consumptionV g).zipIdx.filterMap fun ((s, x, c, lv), i) =>
    match t.lineOutcome g.year s x c lv with
    | .unknown why => some s!"{t.oecd.code} {t.name}: line {i + 1} ({s.good.name}): {why} (grade C)"
    | _ => none

def family (t : GoodsValueTax) : Family :=
  { name := s!"{t.oecd.code} {t.name}", covers := [t.oecd], run := fun _ g _ => t.charges g }

theorem charges_ofCanon (t : GoodsValueTax) (c : Canon) : t.charges (CanonGlobal.ofCanon c) = [] := by
  simp [charges, consumptionV, consumptionC, consumptionX, CanonGlobal.ofCanon]

theorem unknown_ofCanon (t : GoodsValueTax) (c : Canon) : t.unknown (CanonGlobal.ofCanon c) = [] := by
  simp [unknown, consumptionV, consumptionC, consumptionX, CanonGlobal.ofCanon]

end GoodsValueTax

/-- The family of several value taxes. -/
def goodsValueFamily (ts : List GoodsValueTax) (name : String := "taxes on the value of goods") : Family :=
  { name, covers := (ts.map (·.oecd)).eraseDups, run := fun _ g _ => ts.flatMap (·.charges g) }

/-- **Value taxes on a model**: the family last, the grade-C lines after the model's own `unsupported`. -/
def GlobalModel.withGoodsValueTaxes (m : GlobalModel) (ts : List GoodsValueTax)
    (name : String := "taxes on the value of goods") : GlobalModel :=
  { m with families := m.families ++ [goodsValueFamily ts name],
           unsupported := fun args g => m.unsupported args g ++ ts.flatMap (·.unknown g) }

theorem withGoodsValueTaxes_pit (m : GlobalModel) (ts : List GoodsValueTax) (n : String) (args : List String)
    (g : CanonGlobal) : ((m.withGoodsValueTaxes ts n).computeGlobal args g).pit = (m.computeGlobal args g).pit := rfl

end TaxKernel.Global
