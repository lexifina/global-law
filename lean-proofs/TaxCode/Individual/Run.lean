import TaxCode.Individual.Form1040

/-!
# Running the model on a batch of households

    lake env lean --run TaxCode/Individual/Run.lean households.json results.json

`households.json` is an array of `Household` objects (every field present); `results.json` is the array of `Line`
results, in the same order. Used for differential testing against other tax calculators.
-/

namespace TaxCode.Individual
open Lean

deriving instance FromJson for Filing
deriving instance FromJson for Person
deriving instance FromJson for Dependent
deriving instance FromJson for Household
deriving instance ToJson for Filing
deriving instance ToJson for Person
deriving instance ToJson for Dependent
deriving instance ToJson for Household

end TaxCode.Individual

open TaxCode.Individual Lean

def main (args : List String) : IO UInt32 := do
  match args with
  | [inp, out] =>
    let j ← IO.ofExcept (Json.parse (← IO.FS.readFile inp))
    let hs ← IO.ofExcept (fromJson? (α := Array Household) j)
    let rs := hs.map form1040
    IO.FS.writeFile out (Json.compress (toJson rs))
    IO.println s!"{rs.size} returns computed"
    return 0
  | _ => IO.eprintln "usage: Run <households.json> <results.json>"; return 2
