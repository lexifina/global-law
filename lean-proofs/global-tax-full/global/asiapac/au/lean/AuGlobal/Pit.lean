import AuTax.Legacy
import TaxKernel.Global

/-! # Australia: kernel-2.0 model. The 1.x `main` (now `legacyMain`) runs its own loop and prints `outputJson`, so the
PIT is `GlobalModel.ofLine` with that per-line function (finding K2.0-1; DE pilot pattern). -/

namespace AuGlobal
open TaxKernel TaxKernel.Global Lean

/-- The 1.x exe's line: `outputJson (parseHousehold j es isup) (compute …)` with the flags `legacyMain` reads. -/
def pitLine (args : List String) (j : Json) : Json :=
  let es := args.contains "--es" || args.contains "--oecd"
  let isup := args.contains "--income-support" || args.contains "--oecd"
  let h := _root_.parseHousehold j es isup
  outputJson h (AuTax.compute h)

def base : GlobalModel := GlobalModel.ofLine "AU" "Australia" "AUD" "2025" pitLine

/-- The 1.x income tax of a household (for stacking). -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (pitLine args c.raw)

end AuGlobal
