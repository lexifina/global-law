import Lean
import LegalProofs.USCaseLaw
import LegalProofs.CaseLaw2
open Lean Elab Command

/-! Prints the declaration graph of the tax work as JSON lines, for the figure comparing case-law v1 and v2.

    lake env lean tools/CaseLawAnatomy.lean > ../caselaw-anatomy.jsonl

One line per definition or theorem declared in a `TaxCode.*` module or a `LegalProofs.USTax.*` module (other than
`Hunt`): its name, module, kind, and the other such declarations its type or value uses. Compiler-generated auxiliaries
(`match_1`, `_proof_1`, equation lemmas) are folded into the declaration they belong to. -/

def keepModule (m : Name) : Bool :=
  let s := m.toString
  s == "LegalProofs.USCaseLaw.Courts" || s == "LegalProofs.USCaseLaw.Precedent" || s == "LegalProofs.USCaseLaw.Examples"
    || (s.startsWith "LegalProofs.CaseLaw2" && s != "LegalProofs.CaseLaw2.Registry" && s != "LegalProofs.CaseLaw2.Audit")

/-- The user-facing declaration a (possibly auxiliary) name belongs to. -/
def owner (n : Name) : Name :=
  let cs := n.components
  let rec go : List Name → Name → Name
    | [], acc => acc
    | c :: rest, acc =>
      let s := c.toString
      if c.isInternal || s.startsWith "match_" || s.startsWith "eq_" || s == "proof_1" || s.startsWith "_" then acc
      else go rest (acc ++ c)
  go cs .anonymous

run_cmd do
  let env ← getEnv
  let mods := env.header.moduleNames
  let modOf (n : Name) : Option Name := (env.getModuleIdxFor? n).map fun i => mods[i.toNat]!
  -- collect the declarations we draw
  let mut keep : NameSet := {}
  for (n, ci) in env.constants.toList do
    match modOf n with
    | some m =>
      if keepModule m && !n.isInternal && owner n == n then
        match ci with
        | .thmInfo _ | .defnInfo _ | .opaqueInfo _ | .inductInfo _ => keep := keep.insert n
        | _ => pure ()
    | none => pure ()
  -- edges: every kept declaration used (directly or through an auxiliary) by another
  let mut deps : Std.HashMap Name NameSet := {}
  for (n, ci) in env.constants.toList do
    let o := owner n
    if !keep.contains o then continue
    let used := ci.type.getUsedConstants ++ (ci.value?.map (·.getUsedConstants)).getD #[]
    let mut s := deps.getD o {}
    for u in used do
      let uo := owner u
      if uo != o && keep.contains uo then s := s.insert uo
    deps := deps.insert o s
  for n in keep.toList do
    let some ci := env.find? n | continue
    let kind := match ci with | .thmInfo _ => "thm" | .inductInfo _ => "type" | _ => "def"
    let ds := (deps.getD n {}).toList.map (fun d => s!"\"{d}\"")
    IO.println s!"\{\"n\":\"{n}\",\"m\":\"{(modOf n).getD .anonymous}\",\"k\":\"{kind}\",\"d\":[{", ".intercalate ds}]}"
