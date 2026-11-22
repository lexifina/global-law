import CzGlobal.Pit

/-!
# CZ 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (inheritance and gifts in the income tax (ZDP § 4a, § 10); inheritance tax abolished 2014: not cited): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4300 not levied (cited)**: zákonné opatření Senátu č. 340/2013 Sb. § 58 bod 1, § 59: "§ 58 Zrušovací ustanovení Zrušuje se: 1. Zákon č. 357/1992 Sb., o dani dědické, dani darovací a dani z převodu nemovitostí."; "§ 59 Toto zákonné opatření Senátu nabývá účinnosti dnem 1. ledna 2014." (gifts have since been taxed as income under zákon č. 586/1992 Sb., not as a 4300 tax)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Czech Republic, Individual - Other taxes, accessed 2025-04-20 (Wayback capture; `law/pwc_indother_wb2025.txt`): net wealth tax: none (PwC WWTS Individual - Other taxes, 2025-04-20 (Wayback capture))
-/

namespace CzGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "\"§ 58 Zrušovací ustanovení Zrušuje se: 1. Zákon č. 357/1992 Sb., o dani dědické, dani darovací a dani z převodu nemovitostí.\"; \"§ 59 Toto zákonné opatření Senátu nabývá účinnosti dnem 1. ledna 2014.\" (gifts have since been taxed as income under zákon č. 586/1992 Sb., not as a 4300 tax)" },
   { oecd := .wealth, why := "net wealth tax: none" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end CzGlobal.Wealth
