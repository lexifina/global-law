import UkTax.Legacy
import TaxKernel.Global

/-! # United Kingdom: the 1.x model (`cmp/uk`, not built on the kernel) is vendored unchanged and wrapped by its
exe's own per-line function (`GlobalModel.ofLine`; DESIGN §4, finding K2.0-1). -/

namespace UkGlobal
open TaxKernel TaxKernel.Global Lean

/-- The reading the 1.x `main` builds from the options (copied from `UkTax/Legacy.lean`, `legacyMain`). -/
def readingOf (args : List String) : UkTax.Reading :=
  let base := if args.contains "--oecd" then UkTax.Reading.oecd
              else if args.contains "--literal" then UkTax.Reading.literal
              else if args.contains "--pe" then UkTax.Reading.pe else UkTax.Reading.hmrc
  { base with
    peRasDeduction := base.peRasDeduction || args.contains "--pe-ras"
    peMaUnused := base.peMaUnused || args.contains "--pe-ma"
    peNoGiftAidCharge := base.peNoGiftAidCharge || args.contains "--pe-ga"
    peNoMca := base.peNoMca || args.contains "--pe-mca"
    psaLiteral := base.psaLiteral || args.contains "--psa-literal"
    ras := if args.contains "--ras-literal" then .mainRatesOnly
           else if args.contains "--ras-unconditional" || args.contains "--pe-cgt" then .unconditional
           else base.ras }

/-- The 1.x exe's output line for one input line. -/
def pitLine (args : List String) (j : Json) : Json :=
  let hh := _root_.parseHousehold j
  _root_.outputJson hh (UkTax.householdCalc (UkTax.paramsFor hh.year) (readingOf args) hh)

def base : GlobalModel := GlobalModel.ofLine "UK" "United Kingdom" "GBP" "2025" pitLine

/-- The 1.x income tax of a household (for stacking). -/
def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (pitLine args c.raw)

end UkGlobal
