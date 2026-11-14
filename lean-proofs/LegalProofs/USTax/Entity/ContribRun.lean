import LegalProofs.USTax.Entity.Contrib
import Lean.Data.Json

/-!
# Running the contribution game

    lake env lean --run LegalProofs/USTax/Entity/ContribRun.lean in.json out.json

`in.json`: `{"games": [Game], "moves": [Move]}`; `out.json`: for each game, for each move, `[family, parent, child,
baseline family]`.
-/

namespace Legal.USTax.Entity.Contrib
open Lean
deriving instance FromJson for Method
deriving instance FromJson for Game
deriving instance FromJson for Move
end Legal.USTax.Entity.Contrib

open Legal.USTax.Entity.Contrib Lean

def main (args : List String) : IO UInt32 := do
  match args with
  | [inp, out] =>
    let j ← IO.ofExcept (Json.parse (← IO.FS.readFile inp))
    let games ← IO.ofExcept (fromJson? (α := Array Game) (← IO.ofExcept (j.getObjVal? "games")))
    let moves ← IO.ofExcept (fromJson? (α := Array Move) (← IO.ofExcept (j.getObjVal? "moves")))
    let mut res : Array Json := #[]
    for g in games do
      let mut row : Array Json := #[]
      for mv in moves do
        let o := play g mv
        let b := baseline g mv
        row := row.push (toJson [o.family, o.parent, o.child, b.family])
      res := res.push (Json.arr row)
    IO.FS.writeFile out (Json.compress (Json.arr res))
    return 0
  | _ => IO.eprintln "usage: ContribRun <in.json> <out.json>"; return 2
