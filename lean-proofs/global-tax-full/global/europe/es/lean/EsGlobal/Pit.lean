import ESTax.Legacy
import TaxKernel.Global

/-! # Spain: the 1.x `main` is custom (it prints its own line), so the PIT is `GlobalModel.ofLine` with the exe's own
per-line function (finding K2.0-1; DE pilot pattern). -/

namespace EsGlobal
open TaxKernel TaxKernel.Global Lean

/-- The 1.x exe's output line for one input line (its loop's body without the final `compress`). -/
def pitLine (args : List String) (j : Json) : Json :=
  let force := if args.contains "--separate" then some ESTax.Filing.separate
    else if args.contains "--joint" then some ESTax.Filing.joint else none
  match parseCanon j with
  | .error e => Json.mkObj [("error", Json.str e)]
  | .ok c =>
    let f := match force with
      | some f => some f
      | none => match c.str? "filing" with
        | some "joint" => some ESTax.Filing.joint
        | some "separate" => some ESTax.Filing.separate
        | _ => none
    ESTax.compute f c

def base : GlobalModel := GlobalModel.ofLine "ES" "Spain" "EUR" "2025" pitLine

/-- The 1.x income tax of a household (for stacking). -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (pitLine args c.raw)

end EsGlobal
