import MkGlobal.Pit

/-!
# MK 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Закон за даноците на имот (данок на наследство и подарок)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4300 Данок на наследство и подарок (pass 6 note, grade C)**: Закон за даноците на имот (municipal rates): first order of succession exempt; second order 2-3 %, third order and unrelated 4-5 %, the rate set by each municipality within the range: the model's municipality and its decision not read (2025-05-27 (PwC Worldwide Tax Summaries, North Macedonia, Individual - Other taxes, accessed 2025-05-27 (Wayback capture; `law/pwc_indother_wb2025.txt`)))
-/

namespace MkGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty || !g.assets.isEmpty then ["4300 Inheritance and gift tax: not modelled (grade C: not read in the P6 pass)"] else [])
  ++ (if !g.transfers.isEmpty || !g.assets.isEmpty then ["4200 Net wealth tax: not modelled (grade C: not read in the P6 pass)"] else [])


end MkGlobal.Wealth
