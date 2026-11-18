import UsLoop.Core
import Lean.Data.Json

/-!
    usloop in.json out.json

`in.json`: an array of `{"h": Household, "f": Facts}` (every field present; `scripts/model.py` fills defaults).
`out.json`: the array of `Line` results.
-/

namespace TaxCode.Individual
open Lean
deriving instance FromJson for Filing
deriving instance FromJson for Person
deriving instance FromJson for Dependent
deriving instance FromJson for Household
end TaxCode.Individual

namespace TaxCode.Individual.B
open Lean
deriving instance FromJson for Facts
end TaxCode.Individual.B

open TaxCode.Individual Lean

structure Case where
  h : Household
  f : B.Facts
  deriving FromJson

def main (args : List String) : IO UInt32 := do
  match args with
  | [inp, out] =>
    let j ← IO.ofExcept (Json.parse (← IO.FS.readFile inp))
    let cs ← IO.ofExcept (fromJson? (α := Array Case) j)
    let rs := cs.map fun c => UsLoop.form1040F c.f c.h
    IO.FS.writeFile out (Json.compress (toJson rs))
    return 0
  | _ => IO.eprintln "usage: usloop <in.json> <out.json>"; return 2
