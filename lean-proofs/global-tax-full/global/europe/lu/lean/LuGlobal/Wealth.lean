import LuGlobal.Pit

/-!
# LU 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Loi du 27 décembre 1817 (droits de succession)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (Loi du 16 octobre 1934 (impôt sur la fortune des collectivités 0,5 %)): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Luxembourg, Individual - Other taxes, accessed 2025-06-24 (Wayback capture; `law/pwc_indother_wb2025.txt`): wealth tax on individuals: abolished from 1.1.2006 (the companies' impôt sur la fortune is outside this household entry) (PwC WWTS Individual - Other taxes, 2025-06-24 (Wayback capture))
-/

namespace LuGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "wealth tax on individuals: abolished from 1.1.2006 (the companies' impôt sur la fortune is outside this household entry)" }]

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty || !g.assets.isEmpty then ["4300 Inheritance and gift tax: not modelled (grade C: not read in the P6 pass)"] else [])


end LuGlobal.Wealth
