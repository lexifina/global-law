import Lean
import LegalProofs
open Lean Elab Command

/-! Prints, as JSON lines, the dependency graph of a proof: every constant its proof term uses, recursively inside the
`Legal` namespace, with core library constants as leaves. Used by the video to draw the real proof tree.

    lake env lean tools/DepTree.lean > tools/out/deptree.jsonl -/

partial def walk (env : Environment) (root : Name) (maxDepth : Nat) : IO (Array (Name × Name × Nat)) := do
  let seen ← IO.mkRef ({} : NameSet)
  let out ← IO.mkRef (#[] : Array (Name × Name × Nat))
  let rec go (n : Name) (d : Nat) : IO Unit := do
    if (← seen.get).contains n || d > maxDepth then return
    seen.modify (·.insert n)
    let some ci := env.find? n | return
    let body : Option Expr := match ci with
      | .thmInfo t => some t.value
      | .defnInfo d => some d.value
      | _ => none
    let used := (body.map (·.getUsedConstants)).getD #[]
    for m in used do
      if m.isInternal || m == n then continue
      let isLegal := (`Legal).isPrefixOf m
      out.modify (·.push (n, m, d))
      if isLegal then go m (d + 1)
  go root 0
  return (← out.get)

run_cmd do
  let env ← getEnv
  for root in [`Legal.AWaffV.fine_dead, `Legal.consolidate_perm] do
    let edges ← walk env root 4
    for (a, b, d) in edges do
      IO.println s!"\{\"root\":\"{root}\",\"from\":\"{a}\",\"to\":\"{b}\",\"depth\":{d}}"
