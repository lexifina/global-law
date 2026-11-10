import TaxCode.Individual.Form1040

/-!
# Running the model on a batch of households

    lake env lean --run TaxCode/Individual/Run.lean households.json results.json

`households.json` is an array of `Household` objects (every field present); `results.json` is the array of `Line`
results, in the same order. Used for differential testing against other tax calculators.

    lake env lean --run TaxCode/Individual/Run.lean households.json results.json elections.json

With a third file, an array of `true` / `false` / `null` of the same length, each return's §63(e) choice is fixed
(itemize / standard deduction / the cheaper). Married people filing separately must make the same choice
(§63(c)(6)(A)), which the loophole search needs to impose.
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
  | [inp, out, el] =>
    let j ← IO.ofExcept (Json.parse (← IO.FS.readFile inp))
    let hs ← IO.ofExcept (fromJson? (α := Array Household) j)
    let es ← IO.ofExcept (fromJson? (α := Array (Option Bool)) (← IO.ofExcept (Json.parse (← IO.FS.readFile el))))
    if es.size != hs.size then IO.eprintln "elections and households differ in length"; return 2
    let rs := (hs.zip es).map fun (h, e) => match e with
      | none => form1040 h
      | some b => form1040With { electItemize := some b } h
    IO.FS.writeFile out (Json.compress (toJson rs))
    IO.println s!"{rs.size} returns computed"
    return 0
  | _ => IO.eprintln "usage: Run <households.json> <results.json> [elections.json]"; return 2
