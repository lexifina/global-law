import Lean.Data.Json

/-!
# TaxKernel.Canon: the canonical household (copied from `cmp/compare/lean/Compare/Canon.lean`)

Copied unchanged in substance from the five-country comparison (namespace `Compare` → `TaxKernel`); one field
added: `raw`, the whole input object, so a country can read an extra field the harness sets (an election such as
`"jpDividends": "declared"`, a region) with `Canon.str?` / `Canon.int?`.

`cmp/shared/CONTRACT.md` fixes one input line per household (JSON) and one output line per household and
country. This file reads the input into a Lean structure and writes the output object. Amounts are whole units of
the local currency (`Int`). A missing field reads as its default (0, no children, not married); a number with a
fraction is rounded half up to the unit.
-/

namespace TaxKernel
open Lean

structure Adult where
  age : Nat := 40
  wages : Int := 0
  selfEmployment : Int := 0
  pension : Int := 0
  deriving Repr, Inhabited

structure Child where
  age : Nat := 0
  deriving Repr, Inhabited

structure Canon where
  id : String
  year : Nat := 2025
  adults : List Adult := [{}]
  married : Bool := false
  children : List Child := []
  interest : Int := 0
  dividends : Int := 0
  capitalGains : Int := 0
  rentalIncome : Int := 0
  charitable : Int := 0
  pensionContributions : Int := 0
  /-- the whole input object (for extra fields: elections, region) -/
  raw : Json := Json.null
  deriving Inhabited

/-- A JSON number as a whole number of units, half up (`mantissa / 10^exponent`). -/
def numToInt (n : JsonNumber) : Int :=
  let d : Int := (10 : Int) ^ n.exponent
  (2 * n.mantissa + d) / (2 * d)

def intField (j : Json) (k : String) (dflt : Int := 0) : Int :=
  match j.getObjVal? k with
  | .ok (.num n) => numToInt n
  | _ => dflt

def natField (j : Json) (k : String) (dflt : Nat := 0) : Nat :=
  (intField j k dflt).toNat

def boolField (j : Json) (k : String) (dflt : Bool := false) : Bool :=
  match j.getObjVal? k with
  | .ok (.bool b) => b
  | _ => dflt

def arrField (j : Json) (k : String) : Array Json :=
  match j.getObjVal? k with
  | .ok (.arr a) => a
  | _ => #[]

def parseAdult (j : Json) : Adult :=
  { age := natField j "age" 40, wages := intField j "wages", selfEmployment := intField j "selfEmployment",
    pension := intField j "pension" }

def parseCanon (j : Json) : Except String Canon := do
  let id ← match j.getObjVal? "id" with
    | .ok (.str s) => pure s
    | .ok (.num n) => pure (toString (numToInt n))
    | _ => throw "missing id"
  let adults := (arrField j "adults").toList.map parseAdult
  if adults.isEmpty || adults.length > 2 then throw s!"{id}: 1 or 2 adults required"
  pure { id, year := natField j "year" 2025, adults, married := boolField j "married",
         children := (arrField j "children").toList.map fun c => { age := natField c "age" },
         interest := intField j "interest", dividends := intField j "dividends",
         capitalGains := intField j "capitalGains", rentalIncome := intField j "rentalIncome",
         charitable := intField j "charitable", pensionContributions := intField j "pensionContributions", raw := j }

/-- Gross income in the sense of the contract: earnings, pensions and investment and rental income. -/
def Canon.gross (c : Canon) : Int :=
  c.adults.foldl (fun a p => a + p.wages + p.selfEmployment + p.pension) 0
    + c.interest + c.dividends + c.capitalGains + c.rentalIncome

/-- An extra string field of the input (`none` if absent). -/
def Canon.str? (c : Canon) (k : String) : Option String :=
  match c.raw.getObjVal? k with
  | .ok (.str s) => some s
  | _ => none

/-- An extra numeric field of the input (`none` if absent). -/
def Canon.int? (c : Canon) (k : String) : Option Int :=
  match c.raw.getObjVal? k with
  | .ok (.num n) => some (numToInt n)
  | _ => none

/-- An extra boolean field of the input (`none` if absent). -/
def Canon.bool? (c : Canon) (k : String) : Option Bool :=
  match c.raw.getObjVal? k with
  | .ok (.bool b) => some b
  | _ => none

/-- The first adult (there is always one) and the second, if any. -/
def Canon.adult1 (c : Canon) : Adult := c.adults.headD {}
def Canon.adult2? (c : Canon) : Option Adult := c.adults[1]?
def Canon.isCouple (c : Canon) : Bool := c.adults.length == 2
def Canon.nChildren (c : Canon) : Nat := c.children.length
/-- Children under `age` (strictly). -/
def Canon.childrenUnder (c : Canon) (age : Nat) : Nat := (c.children.filter (·.age < age)).length
/-- Earnings of one adult: wages + self-employment. -/
def Adult.earnings (a : Adult) : Int := a.wages + a.selfEmployment
/-- The household's investment income (interest + dividends + capital gains). -/
def Canon.investment (c : Canon) : Int := c.interest + c.dividends + c.capitalGains

/-- Split a household total between two returns: the first gets the odd unit. -/
def half1 (x : Int) : Int := x - x / 2
def half2 (x : Int) : Int := x / 2

/-- One output line (contract): the figures every country reports. -/
structure Out where
  id : String
  country : String
  currency : String
  incomeTax : Int
  surtaxes : List (String × Int)
  localIncomeTax : Int
  employeeSocial : Int
  benefits : Int
  detail : List (String × Json)
  unsupported : List String

def Out.net (o : Out) (gross : Int) : Int :=
  gross - o.incomeTax - o.surtaxes.foldl (fun a p => a + p.2) 0 - o.localIncomeTax - o.employeeSocial + o.benefits

def Out.toJson (o : Out) : Json :=
  Json.mkObj [("id", Json.str o.id), ("country", Json.str o.country), ("currency", Json.str o.currency),
    ("incomeTax", Lean.toJson o.incomeTax),
    ("surtaxes", Json.mkObj (o.surtaxes.map fun (k, v) => (k, Lean.toJson v))),
    ("localIncomeTax", Lean.toJson o.localIncomeTax), ("employeeSocial", Lean.toJson o.employeeSocial),
    ("benefits", Lean.toJson o.benefits), ("detail", Json.mkObj o.detail),
    ("unsupported", Json.arr (o.unsupported.map Json.str).toArray)]

end TaxKernel
