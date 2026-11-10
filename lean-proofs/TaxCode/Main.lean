import TaxCode.Checks

/-!
# `taxcheck`: the drafting checks as a test suite

    lake exe taxcheck <t26.json> <ids.tsv> <findings.json> [baseline.json]

Runs every check over the release point, writes the findings, prints counts by class, and, given a baseline from an
earlier release point, lists what is new and what has been fixed. It exits with status 1 if anything is new, so a
new release point that introduces a drafting error fails the run.
-/

open TaxCode Lean

def findingJson (f : Finding) : Json :=
  Json.mkObj [("class", f.cls), ("citing", f.citing), ("target", f.target), ("detail", f.detail)]

def main (args : List String) : IO UInt32 := do
  match args with
  | t26 :: ids :: out :: rest =>
    let c ← load t26 ids
    IO.println s!"release {c.release}: {c.provs.size} provisions in Title 26, {c.all.size} identifiers in the US Code"
    let fs := runAll c
    IO.FS.writeFile out (Json.compress (Json.arr (fs.map findingJson)))
    let classes := fs.foldl (fun (m : Std.HashMap String Nat) f => m.insert f.cls (m.getD f.cls 0 + 1)) {}
    for (k, v) in classes.toList do IO.println s!"  {k}: {v}"
    match rest with
    | [base] =>
      let bj ← IO.ofExcept (Json.parse (← IO.FS.readFile base))
      let arr ← IO.ofExcept (bj.getArr?)
      let keys := arr.filterMap fun j => (do
        let cls ← j.getObjValAs? String "class"; let a ← j.getObjValAs? String "citing"
        let t ← j.getObjValAs? String "target"; pure (cls ++ "|" ++ a ++ "|" ++ t)).toOption
      let old : Std.HashSet String := keys.foldl (·.insert ·) {}
      let now : Std.HashSet String := fs.foldl (fun s f => s.insert f.key) {}
      let new := fs.filter fun f => !old.contains f.key
      let fixed := keys.filter fun k => !now.contains k
      IO.println s!"against the baseline: {new.size} new, {fixed.size} fixed"
      for f in new.toList.take 50 do IO.println s!"  NEW {f.cls}: {f.citing} → {f.target} ({f.detail})"
      return if new.isEmpty then 0 else 1
    | _ => return 0
  | _ => IO.eprintln "usage: taxcheck <t26.json> <ids.tsv> <findings.json> [baseline.json]"; return 2
