import LegalProofs.USTax.Entity.Driver
import Lean.Data.Json

/-!
# Running owner-family plans in batches

    lake env lean --run LegalProofs/USTax/Entity/Run.lean jobs.json out.json

`jobs.json`: `{"specs": {name: ESpec}, "jobs": [{"spec": name, "plan": EPlan, "log": bool}]}` with every field of every
object present. `out.json`: one `EOutcome` per job, in order (the year log only when asked for). The search scripts
(`tools/taxcode/loopholes/entity_*.py`) write the jobs and read the outcomes; every number in them is computed here.
-/

namespace Legal.USTax.Entity
open Lean Legal.USTax.Family

deriving instance FromJson for Acct
deriving instance FromJson for Form
deriving instance FromJson for Exit
deriving instance FromJson for Biz
deriving instance FromJson for Kid
deriving instance FromJson for ESpec
deriving instance FromJson for Gift
deriving instance FromJson for EPlan
deriving instance ToJson for EYear
deriving instance ToJson for EOutcome

structure Job where
  spec : String
  plan : EPlan
  log : Bool
  deriving FromJson

end Legal.USTax.Entity

open Legal.USTax.Entity Lean

def main (args : List String) : IO UInt32 := do
  match args with
  | [inp, out] =>
    let j ← IO.ofExcept (Json.parse (← IO.FS.readFile inp))
    let specsJ ← IO.ofExcept (j.getObjVal? "specs")
    let jobs ← IO.ofExcept (fromJson? (α := Array Job) (← IO.ofExcept (j.getObjVal? "jobs")))
    let mut specs : List (String × ESpec) := []
    match specsJ with
    | .obj kvs =>
      for (k, v) in kvs.toArray do
        specs := (k, ← IO.ofExcept (fromJson? (α := ESpec) v)) :: specs
    | _ => IO.eprintln "specs must be an object"; return 2
    let mut res : Array Json := #[]
    for jb in jobs do
      match specs.lookup jb.spec with
      | none => IO.eprintln s!"no spec {jb.spec}"; return 2
      | some s =>
        let o := simulate s jb.plan
        res := res.push (toJson (if jb.log then o else { o with log := [] }))
    IO.FS.writeFile out (Json.compress (Json.arr res))
    IO.println s!"{res.size} plans"
    return 0
  | _ => IO.eprintln "usage: Run <jobs.json> <out.json>"; return 2
