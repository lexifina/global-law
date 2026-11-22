import LvGlobal.Pit

/-!
# LV 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (inheritance outside IIN (exempt); no inheritance tax: not cited): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Latvia, Individual - Other taxes, accessed 2025-05-14 (Wayback capture; `law/pwc_indother_wb2025.txt`): net wealth tax: none (PwC WWTS Individual - Other taxes, 2025-05-14 (Wayback capture))

* **4300 not levied (cited, pass 6, grade A)**: likums Par iedzīvotāju ienākuma nodokli 9. panta 1. daļas 9. punkts (likumi.lv, current text fetched 2026-11-21, `lv/law/iin.txt`): no inheritance tax act; income from an inheritance is exempt from the personal income tax (except royalties paid to heirs and inherited state funded pension capital); gifts fall under the income tax rules (not modelled here) (likumi.lv current text (provision in force in 2025))
-/

namespace LvGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "net wealth tax: none" },
   { oecd := .estate, why := "no inheritance tax act; income from an inheritance is exempt from the personal income tax (except royalties paid to heirs and inherited state funded pension capital); gifts fall under the income tax rules (not modelled here)" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end LvGlobal.Wealth
