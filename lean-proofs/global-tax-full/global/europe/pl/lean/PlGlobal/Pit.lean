import PlTax.Legacy
import TaxKernel.Global

/-! # Poland: the 1.x `main` is custom (it prints its own line), so the PIT is `GlobalModel.ofLine` with the exe's own
per-line function (finding K2.0-1; DE pilot pattern). -/

namespace PlGlobal
open TaxKernel TaxKernel.Global Lean

/-- The 1.x exe's output line for one input line (its loop's body without the final `compress`). -/
def pitLine (args : List String) (j : Json) : Json :=
  let h := { _root_.parseHousehold j with fyStart := args.contains "--fy-start" }
  _root_.resultJson h (PlTax.compute h)

def base : GlobalModel := GlobalModel.ofLine "PL" "Poland" "PLN" "2025" pitLine

/-- The 1.x income tax of a household (for stacking). -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (pitLine args c.raw)

end PlGlobal
