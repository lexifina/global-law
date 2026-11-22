import PTTax.Legacy
import TaxKernel.Global

/-! # Portugal: the 1.x `main` is custom (it prints its own line), so the PIT is `GlobalModel.ofLine` with the exe's own
per-line function (finding K2.0-1; DE pilot pattern). -/

namespace PtGlobal
open TaxKernel TaxKernel.Global Lean

/-- The 1.x exe's output line for one input line (its loop's body without the final `compress`). -/
def pitLine (args : List String) (j : Json) : Json :=
  match parseCanon j with
  | .error e => Json.mkObj [("error", Json.str e)]
  | .ok c => _root_.outJson (PTTax.country.computeWith args c)

def base : GlobalModel := GlobalModel.ofLine "PT" "Portugal" "EUR" "2025" pitLine

/-- The 1.x income tax of a household (for stacking). -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (pitLine args c.raw)

end PtGlobal
