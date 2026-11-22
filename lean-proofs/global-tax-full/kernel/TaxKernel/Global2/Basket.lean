import TaxKernel.Global

/-!
# TaxKernel.Global2.Basket (2.1.0): dates and per-line extras of the consumption basket

Kernel 2.1 adds parts without changing any 2.0 name or signature, so the extra facts a statute needs about a basket
line are read from the line itself (`g.raw`, the whole input line, keeps every field), not added to `Spend`:

| JSON field on a `consumption` line | `SpendX` field | used by |
|---|---|---|
| `"date": "YYYY-MM-DD"` (else the line's top-level `"date"`) | `date` | `DatedVat`, `ExciseRule.validFrom/validTo` |
| `"massG"` grams (thousandths of a kg) | `massG` (−1: not given) | `ExciseRule.perKgNum` (per kg / per tonne) |
| `"platoBp"` degree Plato × 100 (12 °P = 1200) | `platoBp` | `ExciseRule.perPlatoNum` (beer per hl and degree) |
| `"sugarMg100ml"` mg of sugar per 100 ml (5 g = 5000) | `sugarMg100ml` | `ExciseRule.sugarBands` |
| `"sub"` a sub-category (`"sweetenedDrinks"`, `"energyDrinks"`, …) | `sub` | `ExciseRule.sub` |
| `"imported": true` (else the good is in the top-level `"importedGoods"`) | `imported` | `ExciseRule.imported` |

`consumptionX g` pairs each `Spend` of `g.consumption` with its extras (`consumptionX_fst`: the spends are exactly
`g.consumption`); an entity built in Lean without `raw` gets the defaults.

Dates are ISO strings; `dayOfYear? year s` is the number of days of `year` before `s` (a date in an earlier year is 0,
a later year the whole year); `scaleDays a d n` is the share `a × d / n` of an amount for `d` days of an `n`-day year
(`scaleDays_full`: the whole year changes nothing).
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-! ## Dates -/

def isLeapYear (y : Nat) : Bool := y % 4 == 0 && (y % 100 != 0 || y % 400 == 0)

def daysInYear (y : Nat) : Nat := if isLeapYear y then 366 else 365

/-- Days of the year before the first day of month `m` (1 … 12). -/
def daysBeforeMonth (leap : Bool) (m : Nat) : Nat :=
  [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334].getD (m - 1) 0 + (if leap && 2 < m then 1 else 0)

/-- `"YYYY-MM-DD"` → (year, days of that year before the date); `none` when it is not such a date. -/
def parseIsoDate (s : String) : Option (Nat × Nat) :=
  match s.splitOn "-" with
  | [ys, ms, ds] =>
    match ys.toNat?, ms.toNat?, ds.toNat? with
    | some y, some m, some d =>
      if 1 ≤ m ∧ m ≤ 12 ∧ 1 ≤ d ∧ d ≤ 31 then some (y, daysBeforeMonth (isLeapYear y) m + d - 1) else none
    | _, _, _ => none
  | _ => none

/-- Days of `year` before the date `s` (0 … days in the year; an earlier year gives 0, a later year the whole year);
`none` when `s` is not a date. -/
def dayOfYear? (year : Nat) (s : String) : Option Nat :=
  (parseIsoDate s).map fun (y, d) =>
    if y < year then 0 else if year < y then daysInYear year else min d (daysInYear year)

/-- A start date: `""` (or no date) is the first day of the year. -/
def startDay (year : Nat) (s : String) : Nat := (dayOfYear? year s).getD 0

/-- An end date (exclusive): `""` (or no date) is the end of the year. -/
def endDay (year : Nat) (s : String) : Nat := (dayOfYear? year s).getD (daysInYear year)

/-- The share of an amount for `d` days of an `n`-day year, rounded down; the whole year (`d = n`) is the amount. -/
def scaleDays (a : Int) (d n : Nat) : Int := if d = n then a else divR .down (a * d) n

theorem scaleDays_full (a : Int) (n : Nat) : scaleDays a n n = a := by simp [scaleDays]

theorem scaleDays_nonneg (a : Int) (d n : Nat) (ha : 0 ≤ a) : 0 ≤ scaleDays a d n := by
  unfold scaleDays; split
  · exact ha
  · simp only [divR]; exact Int.ediv_nonneg (Int.mul_nonneg ha (by omega)) (by omega)

/-- A part of the year never carries more than the amount. -/
theorem scaleDays_le (a : Int) (d n : Nat) (ha : 0 ≤ a) (hd : d ≤ n) : scaleDays a d n ≤ a := by
  unfold scaleDays; split
  · omega
  · simp only [divR]
    by_cases hn : n = 0
    · subst hn; simp; exact ha
    · have hn' : (0 : Int) < n := by omega
      apply Int.ediv_le_of_le_mul hn'
      have : a * (d : Int) ≤ a * (n : Int) := Int.mul_le_mul_of_nonneg_left (by omega) ha
      exact this

/-! ## Per-line extras -/

/-- Facts about a basket line beyond `Spend` (read from the line's JSON). -/
structure SpendX where
  /-- `"YYYY-MM-DD"`, or `""` (undated: spread over the year) -/
  date : String := ""
  /-- mass of the line in grams (thousandths of a kg); −1: not given (the rule's statutory mass per unit is used) -/
  massG : Int := -1
  /-- extract of beer, degree Plato × 100 -/
  platoBp : Int := 0
  /-- sugar, mg per 100 ml -/
  sugarMg100ml : Int := 0
  /-- sub-category of the good (`"sweetenedDrinks"`, `"energyDrinks"`, …; `""`: none) -/
  sub : String := ""
  /-- imported (else local production) -/
  imported : Bool := false
  deriving Repr, Inhabited, BEq

/-- The extras of one consumption line; `date` and `imported` are the entity-level defaults. -/
def SpendX.ofJson (j : Json) (date : String := "") (imported : Bool := false) : SpendX :=
  { date := strField j "date" date, massG := intField j "massG" (-1), platoBp := intField j "platoBp",
    sugarMg100ml := intField j "sugarMg100ml", sub := strField j "sub", imported := boolField j "imported" imported }

/-- Each basket line with its extras, in basket order. -/
def consumptionX (g : CanonGlobal) : List (Spend × SpendX) :=
  let js := (arrField g.raw "consumption").toList
  let date := (g.str? "date").getD ""
  let imp := strList g.raw "importedGoods"
  g.consumption.zipIdx.map fun (s, i) => (s, SpendX.ofJson (js.getD i Json.null) date (imp.contains s.good.name))

theorem consumptionX_fst (g : CanonGlobal) : (consumptionX g).map Prod.fst = g.consumption := by
  simp [consumptionX, List.map_map, Function.comp_def]

theorem consumptionX_length (g : CanonGlobal) : (consumptionX g).length = g.consumption.length := by
  simp [consumptionX]

end TaxKernel.Global
