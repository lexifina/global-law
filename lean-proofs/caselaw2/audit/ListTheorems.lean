import Lean
import LegalProofs.CaseLaw2.Core
open Lean

-- Every theorem declared in a LegalProofs.CaseLaw2.* module, with its doc string.
#eval show Lean.Meta.MetaM Unit from do
  let env ← getEnv
  let mut out : Array String := #[]
  for (n, ci) in env.constants.toList do
    if let .thmInfo _ := ci then
      if n.isInternalDetail then continue
      if let some idx := env.getModuleIdxFor? n then
        let mod := env.header.moduleNames[idx.toNat]!
        if (`LegalProofs.CaseLaw2).isPrefixOf mod && (← findDeclarationRanges? n).isSome then
          let doc := ((← findDocString? env n).getD "").replace "\n" " "
          out := out.push s!"THM\t{n}\t{mod}\t{doc}"
  for l in out.qsort (· < ·) do IO.println l
