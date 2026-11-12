import Lean
import TaxCode.Checks
import TaxCode.Individual.Form1040
import TaxCode.Certs.All
import LegalProofs.USTax
import LegalProofs.USTax.Family
import LegalProofs.USTax.TaxCourt
import LegalProofs.USTax.TaxCourt.Extra
import LegalProofs.USTax.TaxCourt.Rulings
import LegalProofs.USTax.Estate
import LegalProofs.USCaseLaw
import LegalProofs.Amendments
open Lean Elab Command

/-! Prints the declaration graph of the tax work as JSON lines, for the figure comparing the three formalisms.

    lake env lean tools/LawAnatomy.lean > ../law-anatomy.jsonl

One line per definition or theorem declared in a `TaxCode.*` module or a `LegalProofs.USTax.*` module (other than
`Hunt`): its name, module, kind, and the other such declarations its type or value uses. Compiler-generated auxiliaries
(`match_1`, `_proof_1`, equation lemmas) are folded into the declaration they belong to. -/

def keepModule (m : Name) : Bool :=
  let s := m.toString
  ((s.startsWith "TaxCode." || s.startsWith "LegalProofs.USTax") && !(s.startsWith "LegalProofs.USTax.Hunt") && !(s.startsWith "LegalProofs.USTax.Entity"))
    || (s.startsWith "LegalProofs.USCaseLaw" && !(s.startsWith "LegalProofs.USCaseLaw.Run")) || s == "LegalProofs.Amendments"

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
