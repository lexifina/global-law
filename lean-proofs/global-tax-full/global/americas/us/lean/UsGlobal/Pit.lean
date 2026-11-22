import UsGlobal.Legacy
import TaxKernel.Global
import AmerCommon

/-!
# United States: the PIT is the 1.x model through its own line function (`GlobalModel.ofLine`)

The US model is not built on the kernel (Form 1040 model `TaxCode.Individual` + the contract adapter `Compare.Us`).
`pitLine` is what `cmptax us` prints for one input line, so `model_pit` holds by `rfl` (kernel `ofLine_unchanged`).
-/

namespace UsGlobal
open TaxKernel TaxKernel.Global Lean

def pitLine (_ : List String) (j : Json) : Json :=
  match Compare.parseCanon j with
  | .error e => Json.mkObj [("error", Json.str e)]
  | .ok c => (Compare.Us.out c).toJson

def base : GlobalModel := GlobalModel.ofLine "US" "United States" "USD" "2025" pitLine

/-- The 1.x federal income tax (regular tax, AMT, NIIT, Additional Medicare) of a household: for stacking. -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (base.pit args c)

end UsGlobal
