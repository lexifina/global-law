import RoGlobal.Pit

/-!
# RO 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Codul fiscal art. 111 (inheritance of real estate after 2 years 1 %)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Romania, Individual - Other taxes, accessed 2025-06-16 (Wayback capture; `law/pwc_indother_wb2025.txt`): net wealth tax: none (PwC WWTS Individual - Other taxes, 2025-06-16 (Wayback capture))

* **4300 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Romania, Individual - Other taxes, accessed 2025-06-16 (Wayback capture; `law/pwc_indother_wb2025.txt`): inheritance / gift tax: none; income tax on inherited real estate where the succession is not settled within 2 years (1100) (PwC WWTS Individual - Other taxes, 2025-06-16 (Wayback capture))
-/

namespace RoGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "net wealth tax: none" },
   { oecd := .estate, why := "inheritance / gift tax: none; income tax on inherited real estate where the succession is not settled within 2 years (1100)" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end RoGlobal.Wealth
