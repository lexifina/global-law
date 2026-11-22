import JpTax.Legacy
import TaxKernel.Global

/-! # Japan: kernel-2.0 model around the pre-kernel 1.x model (`cmp/jp`), wrapped by its own line function. -/

namespace JpGlobal
open TaxKernel TaxKernel.Global Lean

/-- The 1.x exe's line (`runLine` without the final `compress`). -/
def pitLine (args : List String) (j : Json) : Json :=
  let h := { _root_.parseHousehold j with oecd := args.contains "--oecd" }
  resultJson h (JpTax.compute h)

def base : GlobalModel := GlobalModel.ofLine "JP" "Japan" "JPY" "2025" pitLine

/-- The 1.x income tax of a household (for stacking). -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (pitLine args c.raw)

end JpGlobal
