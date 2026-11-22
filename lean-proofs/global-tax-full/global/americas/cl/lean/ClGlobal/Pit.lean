import ClTax
import TaxKernel.Global
import AmerCommon

/-!
# Chile 2025 on kernel 2.0: the PIT (1.x `ClTax`, vendored unchanged from `cmp20/world/B01-oecd5/cl/lean`, sha256 in
`VENDORED_FROM_world_cl.sha256`) and the indexed units shared by every family

This project is the kernel-2.0 pilot (`cmp20/global/pilots/cl`, built from BCN LeyChile texts as in force on
2025-07-01, saved in `law/`), integrated into the Americas region and split into one file per family.
* **Values**: UTA December 2025 = 12 × UTM 69.542 (SII utm2025.htm; the 1.x model's `utaDec`); UF on 31-12-2025 =
  39.727,96 (SII uf2025.htm, parsed in `world/B01-oecd5/cl/src/sii/uf_lastday.json`).
-/

namespace ClGlobal
open TaxKernel TaxKernel.Global Lean

def base : GlobalModel := GlobalModel.ofCountry ClTax.country

/-- The income tax of the 1.x model (impuesto único + global complementario lines). -/
def pitOf (args : List String) (c : Canon) : Int :=
  let o := ClTax.country.computeWith args c
  o.incomeTax + sumInts (o.surtaxes.map (·.2)) + o.localIncomeTax

/-- UF on 31-12-2025, centavos (SII uf2025.htm). -/
def ufDec31C : Int := 3972796
def ufToPesos (uf : Int) : Int := divR .down (uf * ufDec31C) 100
/-- UTA of December 2025 (1.x `ClTax.utaDec`). -/
def uta : Int := ClTax.utaDec

#guard uta == 834504
#guard ufToPesos 8000 == 317823680
#guard ufToPesos 75000 == 2979597000

end ClGlobal
