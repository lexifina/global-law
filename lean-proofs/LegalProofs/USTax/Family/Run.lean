import LegalProofs.USTax.Family.Driver
import Lean.Data.Json

/-!
# Running family plans in batches

    lake env lean --run LegalProofs/USTax/Family/Run.lean jobs.json out.json

`jobs.json`: `{"specs": {name: Spec}, "jobs": [{"spec": name, "plan": [YearPlan, …], "log": bool}]}` with every field
of every object present. `out.json`: one `Outcome` per job, in order (the year log only when asked for).
The search (`tools/taxcode/loopholes/family_search.py`) writes the jobs and reads the outcomes; every number in them
is computed here.
-/

namespace Legal.USTax.Family
open Lean

deriving instance FromJson for Acct
deriving instance FromJson for ParentSpec
deriving instance FromJson for KidSpec
deriving instance FromJson for Spec
deriving instance FromJson for YearPlan
deriving instance ToJson for YearLog
deriving instance ToJson for Outcome

structure Job where
  spec : String
  plan : List YearPlan
  log : Bool
  deriving FromJson

end Legal.USTax.Family

open Legal.USTax.Family Lean

def main (args : List String) : IO UInt32 := do
  match args with
  | [inp, out] =>
    let j ← IO.ofExcept (Json.parse (← IO.FS.readFile inp))
    let specsJ ← IO.ofExcept (j.getObjVal? "specs")
    let jobs ← IO.ofExcept (fromJson? (α := Array Job) (← IO.ofExcept (j.getObjVal? "jobs")))
    let mut specs : List (String × Spec) := []
    match specsJ with
    | .obj kvs =>
      for (k, v) in kvs.toArray do
        specs := (k, ← IO.ofExcept (fromJson? (α := Spec) v)) :: specs
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
