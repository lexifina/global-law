import PtGlobal.Pit

/-!
# PT 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Código do Imposto do Selo verba 1.2 (10 %; family exempt)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (Adicional ao IMI (CIMI art. 135-A)): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Portugal, Individual - Other taxes, accessed 2025-08-01 (Wayback capture; `law/pwc_indother_wb2025.txt`): net wealth tax: none (PwC WWTS Individual - Other taxes, 2025-08-01 (Wayback capture))
-/

namespace PtGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "net wealth tax: none" }]

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty || !g.assets.isEmpty then ["4300 Inheritance and gift tax: not modelled (grade C: not read in the P6 pass)"] else [])


end PtGlobal.Wealth
