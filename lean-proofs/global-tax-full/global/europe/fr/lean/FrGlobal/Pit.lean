import Compare.Legacy
import TaxKernel.Global

/-! # France: the 1.x model is `cmptax fr` (the Compare project around the pre-kernel FrTax model, vendored
unchanged); wrapped by the exe's own per-line function (`GlobalModel.ofLine`; DESIGN §4). -/

namespace FrGlobal
open TaxKernel TaxKernel.Global Lean

/-- `cmptax fr`'s output line for one input line (`runOne "fr"`, with the options `cmptax` passes: "fr" first). -/
def pitLine (args : List String) (j : Json) : Json :=
  match Compare.parseCanon j with
  | .error e => Json.mkObj [("error", Json.str e)]
  | .ok c => (Compare.Fr.out c ("fr" :: args)).toJson

def base : GlobalModel := GlobalModel.ofLine "FR" "France" "EUR" "2025" pitLine

/-- The 1.x income tax of a household (for stacking). -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (pitLine args c.raw)

end FrGlobal
