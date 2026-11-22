import SkGlobal.Pit

/-!
# SK 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (none (abolished 2004; not cited)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4300 not levied (cited)**: zákon č. 554/2003 Z. z. § 19, čl. III (Slov-Lex, version 2016-07-01): "§ 19 Zrušuje sa zákon Slovenskej národnej rady č. 318/1992 Zb. o dani z dedičstva, dani z darovania a dani z prevodu a prechodu nehnuteľností ..."; "Tento zákon nadobúda účinnosť 1. januára 2004"; § 17: tax liabilities arisen before 1 January 2004 only

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Slovak Republic, Individual - Other taxes, accessed 2025-05-27 (Wayback capture; `law/pwc_indother_wb2025.txt`): net wealth tax: none (PwC WWTS Individual - Other taxes, 2025-05-27 (Wayback capture))
-/

namespace SkGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "\"§ 19 Zrušuje sa zákon Slovenskej národnej rady č. 318/1992 Zb. o dani z dedičstva, dani z darovania a dani z prevodu a prechodu nehnuteľností ...\"; \"Tento zákon nadobúda účinnosť 1. januára 2004\"; § 17: tax liabilities arisen before 1 January 2004 only" },
   { oecd := .wealth, why := "net wealth tax: none" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end SkGlobal.Wealth
