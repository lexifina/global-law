import LegalProofs.USCaseLaw.Recodification
import Std.Data.HashSet

/-!
# Runner: the totality check for one restatement

    lake env lean --run LegalProofs/USCaseLaw/RunRecodification.lean <in.tsv> <out.tsv> [explained]

Input rows (tab-separated):
* `O id`: a provision in force at an old location the day before the restatement (`36:169j`, `42:2451`);
* `M id images`: the official tables map it to these provisions (comma-separated);
* `X id reason`: the official tables omit it, for this reason;
* `E id explanation`: no table row, but the record explains it (another law repealed it, or its words turn up
  elsewhere); used only when the third argument is `explained`;
* `N id`: a provision in force once the restatement took effect.

Prints one line: old provisions, mapped, omitted, unaccounted, images not in force, and whether the check passes.
Writes the unaccounted provisions (`U id`) and the images not in force (`I id image`) to the output file.
-/

open Legal.USCaseLaw.Recodification

def main (args : List String) : IO UInt32 := do
  let (inp, out, useE) ← match args with
    | [i, o] => pure (i, o, false)
    | [i, o, "explained"] => pure (i, o, true)
    | _ => do IO.eprintln "usage: RunRecodification.lean <in.tsv> <out.tsv> [explained]"; return 2
  let s ← IO.FS.readFile inp
  let mut old : Array String := #[]
  let mut dispo : Array (String × Disposition) := #[]
  let mut inForce : Std.HashSet String := {}
  let mut inForceL : Array String := #[]
  for l in s.splitOn "\n" do
    let f := (l.splitOn "\t").toArray
    match f[0]? with
    | some "O" => old := old.push f[1]!
    | some "M" => dispo := dispo.push (f[1]!, .mapped ((f[2]!.splitOn ",").filter (· ≠ "")))
    | some "X" => dispo := dispo.push (f[1]!, .omitted f[2]!)
    | some "E" => if useE then dispo := dispo.push (f[1]!, .omitted f[2]!)
    | some "N" => inForce := inForce.insert f[1]!; inForceL := inForceL.push f[1]!
    | _ => pure ()
  -- The model's lists, with the in-force list reduced to the images the tables name (membership is all `sound`
  -- asks of it; a hash set keeps the reduction fast over titles with thousands of sections).
  let named : List String := dispo.toList.flatMap fun p => match p.2 with | .mapped is => is | _ => []
  let r : Restatement := { old := old.toList, dispo := dispo.toList, inForce := named.filter inForce.contains }
  let un := unaccounted r
  let miss := missingImages r
  let nMapped := r.old.countP fun o => match lookup r o with | some (.mapped _) => true | _ => false
  let nOmitted := r.old.countP fun o => match lookup r o with | some (.omitted _) => true | _ => false
  let h ← IO.FS.Handle.mk out .write
  for o in un do h.putStrLn s!"U\t{o}"
  for (o, i) in miss do h.putStrLn s!"I\t{o}\t{i}"
  IO.println s!"{inp}: old {r.old.length}; mapped {nMapped}; omitted {nOmitted}; unaccounted {un.length}; images not in force {miss.length}; total {total r}; sound {sound r}; check {check r}"
  return 0
