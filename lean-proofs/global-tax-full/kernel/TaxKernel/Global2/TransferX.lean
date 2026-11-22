import TaxKernel.Global2.Basket

/-!
# TaxKernel.Global2.TransferX (2.1.1, 2026-11-21): what an inheritance or gift is made of (OECD 4300)

Some gift and inheritance duties apply to one kind of property only (MA CGI art. 133-I-C-4°: 1,5 % on gifts of
immovable property, art. 127-I-A, in the direct line, between spouses and between siblings; movables are outside it).
`Transfer` is unchanged; the extra facts are read from the transfer's own JSON by `transfersX g` (same order as
`g.transfers`, `transfersX_fst`):

| JSON on a `transfers` record | `TransferX` | meaning |
|---|---|---|
| `"assetKind"` (`home`, `realEstate`, `land`, `listedShares`, … as `AssetKind`) | `assetKind` | what the whole transfer is |
| `"realPropertyValue"` | `realPropertyValue` (−1: not given) | the part of it that is immovable property |

`realPropertyPart t x`: the given `realPropertyValue` (at most the transfer's statutory value), else the whole
statutory value when `assetKind` is immovable (`home`, `realEstate`, `land`), else 0 when `assetKind` is anything else,
else `none` (not known: the model must say so, not assume). `Transfer.restrict t v` is the transfer cut down to an
amount `v` (to feed a part to the 2.0 `InheritanceTax`).

`PartDuty`: a flat duty on a part of each transfer (default: the immovable part), with a rate per relation (relations
not listed: no duty), for gifts and/or inheritances: one charge (OECD 4300) per transfer whose part is known;
`PartDuty.unknown g` lists the transfers whose part is not known (for `unsupported`).
Theorems: `transfersX_fst`, `realPropertyPart_le`, `realPropertyPart_nonneg`, `PartDuty.amount_mono`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

structure TransferX where
  assetKind : Option AssetKind := none
  /-- the immovable-property part of the transfer (−1: not given) -/
  realPropertyValue : Int := -1
  deriving Repr, Inhabited, BEq

def TransferX.ofJson (j : Json) : TransferX :=
  { assetKind := match j.getObjVal? "assetKind" with
      | .ok (.str s) => some (AssetKind.ofString s)
      | _ => none,
    realPropertyValue := intField j "realPropertyValue" (-1) }

/-- Each transfer with its extras, in order. -/
def transfersX (g : CanonGlobal) : List (Transfer × TransferX) :=
  let js := (arrField g.raw "transfers").toList
  g.transfers.zipIdx.map fun (t, i) => (t, TransferX.ofJson (js.getD i Json.null))

theorem transfersX_fst (g : CanonGlobal) : (transfersX g).map Prod.fst = g.transfers := by
  simp [transfersX, List.map_map, Function.comp_def]

/-- The immovable-property part (`none`: not known). -/
def realPropertyPart (t : Transfer) (x : TransferX) : Option Int :=
  if 0 ≤ x.realPropertyValue then some (min x.realPropertyValue (pos t.statutoryValue))
  else match x.assetKind with
    | some k => some (if k.isRealEstate then pos t.statutoryValue else 0)
    | none => none

theorem realPropertyPart_le (t : Transfer) (x : TransferX) (v : Int) (h : realPropertyPart t x = some v) :
    v ≤ pos t.statutoryValue := by
  unfold realPropertyPart at h
  split at h
  · cases h; omega
  · split at h
    · cases h; split <;> (try simp only [pos]) <;> omega
    · cases h

theorem realPropertyPart_nonneg (t : Transfer) (x : TransferX) (v : Int) (h : realPropertyPart t x = some v) :
    0 ≤ v := by
  unfold realPropertyPart at h
  split at h
  · cases h; simp only [pos]; omega
  · split at h
    · cases h; split <;> (try simp only [pos]) <;> omega
    · cases h

/-- The transfer cut down to an amount `v` (no separate assessed value; reliefs capped at `v`). -/
def Transfer.restrict (t : Transfer) (v : Int) : Transfer :=
  { t with value := v, assessed := -1, homeValue := min t.homeValue v, businessValue := min t.businessValue v }

/-- A flat duty on a part of each transfer, by relation. -/
structure PartDuty where
  name : String
  /-- rate per relation, bp; relations not listed are not charged -/
  rates : List (Relation × Int)
  gifts : Bool := true
  inheritances : Bool := false
  /-- the part charged (default: the immovable part) -/
  part : Transfer → TransferX → Option Int := realPropertyPart
  round : Rule := {}
  statute : String := ""
  level : Level := .central

namespace PartDuty
def rateFor (d : PartDuty) (r : Relation) : Option Int := (d.rates.find? (·.1 == r)).map (·.2)

def kindOk (d : PartDuty) (t : Transfer) : Bool := if t.kind == .gift then d.gifts else d.inheritances

def amount (d : PartDuty) (rate v : Int) : Int := d.round.ofTicks (rate * pos v)

/-- One charge per transfer of the right kind and relation whose part is known. -/
def charges (d : PartDuty) (g : CanonGlobal) : List Charge :=
  (transfersX g).zipIdx.filterMap fun ((t, x), i) =>
    if !d.kindOk t then none else
    match d.rateFor t.relation, d.part t x with
    | some r, some v =>
      some (charge .estate d.name t.statutoryValue (fun _ => v) (fun b => d.amount r b)
        (event := s!"{if t.kind == .gift then "gift" else "inheritance"} {i + 1}") (level := d.level)
        (statute := d.statute))
    | _, _ => none

/-- Transfers the duty would reach whose part is not known. -/
def unknown (d : PartDuty) (g : CanonGlobal) : List String :=
  (transfersX g).zipIdx.filterMap fun ((t, x), i) =>
    if d.kindOk t && (d.rateFor t.relation).isSome && (d.part t x).isNone then
      some s!"{d.name}: transfer {i + 1} does not say what part is immovable property (give \"assetKind\" or \"realPropertyValue\"): not charged"
    else none

def family (d : PartDuty) : Family :=
  { name := s!"4300 {d.name}", covers := [.estate], run := fun _ g _ => d.charges g }
end PartDuty

/-- A larger part never pays less (monotone rounding modes, positive step, non-negative rate). -/
theorem PartDuty.amount_mono (d : PartDuty) (rate : Int) (hr : 0 ≤ rate) (hs : 0 < d.round.step)
    (hm : d.round.mode.isMonotoneMode) {v w : Int} (h : v ≤ w) : d.amount rate v ≤ d.amount rate w := by
  unfold PartDuty.amount
  apply Rule.ofTicks_mono _ hs hm
  have : pos v ≤ pos w := by simp only [pos]; omega
  exact Int.mul_le_mul_of_nonneg_left this hr

end TaxKernel.Global
