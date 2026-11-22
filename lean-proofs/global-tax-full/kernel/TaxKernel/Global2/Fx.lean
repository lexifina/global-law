import TaxKernel.Global2.Assets
import TaxKernel.Global2.Basket

/-!
# TaxKernel.Global2.Fx (2.7.0, 2026-11-21): amounts fixed in a foreign currency, an explicitly declared rate (R4-17-1)

ZW (R4 SSA pass 17): the ZINARA vehicle licence tariff (Vehicle Registration and Licensing Regulations, Third Schedule
Part II as substituted by SI 67 of 2024) is fixed in US$ and "may be payable in local currency (ZiG) ... at the ruling
exchange rate of the day", while the ZW model works in ZWG; the IMTT cap (US$10 150) and the Finance Act's US$ stamp bands
have the same shape (also LR and MW specific duties in US$). There is no statutory rate, so **the kernel never has a rate
of its own**: a rate is used only when it is declared, with where it comes from.

**The rate** (`FxRate`): `num / den` units of the model's currency for one unit of `currency` (ISO 4217), with its
`source` and `date` (both required fields of the structure: a rule-level rate cannot be written without them). Two ways to
declare one:
* **on the entity** (the case's rate: "the ruling exchange rate of the day"): the input line's `"fxRates"` (top level, else
  `company.fxRates`, else `household.fxRates`), one entry per currency, either a number (`{"USD": 26.75}`) or a record
  (`{"USD": {"rate": 26.75, "source": "RBZ interbank mid-rate", "date": "2025-06-30"}}`); the JSON number is read exactly
  (26.75 = 2675/100). A rate that is not a positive number is not given. `fxInput? g "USD"`;
* **on the rule** (a rate the model declares, e.g. a published official rate for the year): `fxRate := some { currency :=
  "USD", num := 2675, den := 100, source := "…", date := "…" }` on a `VehicleTax` (or passed to `fxFor`).

`fxFor g cur declared` = the entity's rate if it gives one (the case's own fact wins), else the declared rate if it is for
`cur` and positive, else **`none`: the rule books nothing and the model lists `fxUnknownLine` (grade C)**. The charge's
statute names the rate used (`FxRate.note`: "US$ amounts at 26.75 (RBZ interbank mid-rate, 2025-06-30)").

Conversion: `FxRate.convert r x = ⌊x × num / den⌋`; a table in the foreign currency, `QtyTable.amountAt t num den q` =
`⌊(band × den_t + marginal numerator) × num / (den_t × den)⌋` (one rounding: the exact table amount, converted);
`amountAt t 1 1 = amount` (`QtyTable.amountAt_one`). A quantity given in the model's currency and banded in the foreign
one (a value against a US$ threshold) is `FxRate.toForeign r x = ⌊x × den / num⌋`.

Theorems: `FxRate.convert_one`, `convert_nonneg`, `convert_mono`, `QtyTable.amountAt_one`, `fxFor_input`,
`fxFor_noInput`, `fxFor_none` (no input and no declared rate: no rate), `fxInput?_null`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-- A declared exchange rate: `num / den` units of the model's currency per unit of `currency`. -/
structure FxRate where
  /-- ISO 4217 code of the foreign currency (`"USD"`) -/
  currency : String
  num : Int
  den : Int := 1
  /-- where the rate comes from (the authority, the publication) -/
  source : String
  /-- the date the rate is for (ISO) -/
  date : String
  deriving Repr, Inhabited, BEq, DecidableEq

namespace FxRate

/-- Positive, for a named currency. -/
def valid (r : FxRate) : Bool := r.currency != "" && decide (0 < r.num) && decide (0 < r.den)

/-- An amount in the foreign currency, in the model's currency (rounded down). -/
def convert (r : FxRate) (x : Int) : Int := divR .down (x * r.num) r.den

/-- An amount in the model's currency, in the foreign one (rounded down): to test it against a foreign threshold. -/
def toForeign (r : FxRate) (x : Int) : Int := if r.num ≤ 0 then 0 else divR .down (x * r.den) r.num

/-- `den` is `10^k`: the number of decimals, else `none`. -/
def decimals (den : Int) : Option Nat :=
  ((List.range 13).filter fun k => (10 : Int) ^ k == den).head?

/-- The rate as text: `26.75` for 2675/100, else `num/den`. -/
def rateText (r : FxRate) : String :=
  match decimals r.den with
  | some 0 => toString r.num
  | some k =>
    let s := toString r.num.natAbs
    let s := String.ofList (List.replicate (k + 1 - min (k + 1) s.length) '0') ++ s
    (if r.num < 0 then "-" else "") ++ (s.take (s.length - k)).toString ++ "." ++ (s.drop (s.length - k)).toString
  | none => s!"{r.num}/{r.den}"

/-- What the charge's statute says about the rate. -/
def note (r : FxRate) : String :=
  let src := ", ".intercalate ([r.source, r.date].filter (· != ""))
  s!"{r.currency} amounts at {r.rateText}" ++ (if src.isEmpty then " (source not stated)" else s!" ({src})")

theorem convert_one (r : FxRate) (h1 : r.num = 1) (h2 : r.den = 1) (x : Int) : r.convert x = x := by
  simp [convert, h1, h2, divR]

theorem convert_nonneg (r : FxRate) (hv : r.valid = true) (x : Int) (hx : 0 ≤ x) : 0 ≤ r.convert x := by
  simp only [valid, Bool.and_eq_true, decide_eq_true_eq] at hv
  simp only [convert, divR]
  exact Int.ediv_nonneg (Int.mul_nonneg hx (by omega)) (by omega)

theorem convert_mono (r : FxRate) (hv : r.valid = true) {x y : Int} (h : x ≤ y) : r.convert x ≤ r.convert y := by
  simp only [valid, Bool.and_eq_true, decide_eq_true_eq] at hv
  simp only [convert, divR]
  exact Int.ediv_le_ediv (by omega) (Int.mul_le_mul_of_nonneg_right h (by omega))

end FxRate

/-! ## The entity's rates -/

/-- The `"fxRates"` object of the line: top level, else `company.fxRates`, else `household.fxRates` (`null`: none). -/
def fxRatesJson (g : CanonGlobal) : Json :=
  match g.raw.getObjVal? "fxRates" with
  | .ok j => j
  | .error _ =>
    let sub (k : String) : Option Json := match g.raw.getObjVal? k with
      | .ok o => match o.getObjVal? "fxRates" with | .ok j => some j | .error _ => none
      | .error _ => none
    match sub "company" with
    | some j => j
    | none => (sub "household").getD Json.null

/-- An entry of `"fxRates"`: a positive number, or `{ "rate": n, "source": s, "date": d }`. -/
def fxOfJson (cur : String) (j : Json) : Option FxRate :=
  let mk (n : JsonNumber) (src date : String) : Option FxRate :=
    let r : FxRate := { currency := cur, num := n.mantissa, den := (10 : Int) ^ n.exponent, source := src, date }
    if r.valid then some r else none
  match j with
  | .num n => mk n "input fxRates" ""
  | .obj _ => match j.getObjVal? "rate" with
    | .ok (.num n) => mk n (strField j "source" "input fxRates") (strField j "date")
    | _ => none
  | _ => none

/-- The entity's rate for `cur` (`none`: not given). -/
def fxInput? (g : CanonGlobal) (cur : String) : Option FxRate :=
  match (fxRatesJson g).getObjVal? cur with
  | .ok j => fxOfJson cur j
  | .error _ => none

/-- **The rate for amounts in `cur`**: the entity's own (its input), else the rule's declared rate (for `cur`, positive),
else none (grade C: never a built-in rate). -/
def fxFor (g : CanonGlobal) (cur : String) (declared : Option FxRate := none) : Option FxRate :=
  match fxInput? g cur with
  | some r => some r
  | none => match declared with
    | some r => if r.valid && r.currency == cur then some r else none
    | none => none

/-- The grade-C line for a rule whose amounts are in `cur` and no rate is given. -/
def fxUnknownLine (code name cur : String) (what : String := "") : String :=
  s!"{code} {name}: " ++ (if what.isEmpty then "" else what ++ ": ")
    ++ s!"amounts in {cur} and no exchange rate given (fxRates.{cur}) (grade C)"

theorem fxFor_input (g : CanonGlobal) (cur : String) (d : Option FxRate) (r : FxRate) (h : fxInput? g cur = some r) :
    fxFor g cur d = some r := by simp [fxFor, h]

theorem fxFor_noInput (g : CanonGlobal) (cur : String) (r : FxRate) (h : fxInput? g cur = none) (hv : r.valid = true)
    (hc : r.currency = cur) : fxFor g cur (some r) = some r := by simp [fxFor, h, hv, hc]

/-- **Never a rate of its own**: no input and no declared rate, no rate. -/
theorem fxFor_none (g : CanonGlobal) (cur : String) (h : fxInput? g cur = none) : fxFor g cur none = none := by
  simp [fxFor, h]

theorem fxInput?_null (g : CanonGlobal) (cur : String) (h : fxRatesJson g = Json.null) : fxInput? g cur = none := by
  rw [fxInput?, h]; rfl

/-! ## A table in the foreign currency -/

namespace QtyTable

/-- The table's amount times `num / den`, rounded down once (the exact amount converted). -/
def amountAt (t : QtyTable) (num den : Int) (q : Int) : Int :=
  divR .down ((t.band (t.counted q) * t.den + marginalNum t.steps (t.counted q)) * num) (t.den * den)

/-- In the table's own currency (`1/1`) it is the table's amount. -/
theorem amountAt_one (t : QtyTable) (hd : 0 < t.den) (q : Int) : t.amountAt 1 1 q = t.amount q := by
  simp only [amountAt, amount, marginal, divR, Int.mul_one]
  rw [Int.add_comm, Int.add_mul_ediv_right _ _ (by omega), Int.add_comm]

/-- The table's amount converted at a rate (`FxRate.convert` of the exact amount). -/
def amountFx (t : QtyTable) (r : FxRate) (q : Int) : Int := t.amountAt r.num r.den q

end QtyTable

end TaxKernel.Global
