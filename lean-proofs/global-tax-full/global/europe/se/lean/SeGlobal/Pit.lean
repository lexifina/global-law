import SETax.Legacy
import TaxKernel.Global

/-! # Sweden: the 1.x `main` is custom (it prints its own line), so the PIT is `GlobalModel.ofLine` with the exe's own
per-line function (finding K2.0-1; DE pilot pattern). -/

namespace SeGlobal
open TaxKernel TaxKernel.Global Lean

/-- The 1.x exe's output line for one input line (its loop's body without the final `compress`). -/
def pitLine (args : List String) (j : Json) : Json :=
  match parseCanon j with
  | .error e => Json.mkObj [("error", Json.str e)]
  | .ok c =>
    let b := if args.contains "--oecd" then SETax.p2025oecd else SETax.p2025
    let k := SETax.country b (args.contains "--state-first") (args.contains "--oecd")
    if args.contains "--euromod" then
      let o := k.compute (_root_.euromodCanon c)
      ({ o with detail := o.detail ++ [TaxKernel.Out.dStr "convention2" "EUROMOD (--euromod): CR SE 2.6.6 Table 2.28"] }).toJson
    else (k.computeWith args c).toJson

def base : GlobalModel := GlobalModel.ofLine "SE" "Sweden" "SEK" "2025" pitLine

/-- The 1.x income tax of a household (for stacking). -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (pitLine args c.raw)

end SeGlobal
