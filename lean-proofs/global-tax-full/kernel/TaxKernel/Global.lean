import TaxKernel.Global.Types
import TaxKernel.Global.Master
import TaxKernel.Global.Corporate
import TaxKernel.Global.Capital
import TaxKernel.Global.Property
import TaxKernel.Global.Transfers
import TaxKernel.Global.Consumption
import TaxKernel.Global.Run

/-!
# TaxKernel.Global (2.0.0, 2026-11-21): every tax, one master equation (design: cmp20/global/DESIGN.md)

Import it explicitly (`import TaxKernel.Global`; it imports `TaxKernel.World2`, `TaxKernel.World` and the whole 1.x
kernel). Neither the root module `TaxKernel` nor `World`/`World2` imports it, so every 1.x model and its oleans are
unchanged by construction.

2.3.0 (2026-11-21, global/KERNEL_REQUESTS.md R-FT2-1 and R1 Europe pass 4): `computeGlobal` reports withholding that no
rule computes as grade C in `unsupported` instead of booking a 0 (`Master`, `WhtRead`; a statutory zero is a cited 0 %
rule: `WhtRule.zero`, `Wht.zeroOn`, `Wht.family` in `Capital`), and `CorpRegime.smallEmployees` adds an employee limit
to the small-company test (`Corporate`). Totals and every household output are unchanged (API.md §4e.2).
-/
