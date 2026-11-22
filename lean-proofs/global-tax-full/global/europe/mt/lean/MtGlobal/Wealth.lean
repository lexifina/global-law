import MtGlobal.Pit

/-!
# MT 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (Duty on Documents and Transfers Act (causa mortis transfers of immovables)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Malta, Individual - Other taxes, accessed 2025-07-08 (Wayback capture; `law/pwc_indother_wb2025.txt`): net wealth tax: none (PwC WWTS Individual - Other taxes, 2025-07-08 (Wayback capture))

* **4300 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Malta, Individual - Other taxes, accessed 2025-07-08 (Wayback capture; `law/pwc_indother_wb2025.txt`): inheritance / estate / gift tax: none; duty on documents on transmissions causa mortis of immovables (5 %) and shares is a stamp duty (4400, not modelled) (PwC WWTS Individual - Other taxes, 2025-07-08 (Wayback capture))
-/

namespace MtGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "net wealth tax: none" },
   { oecd := .estate, why := "inheritance / estate / gift tax: none; duty on documents on transmissions causa mortis of immovables (5 %) and shares is a stamp duty (4400, not modelled)" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end MtGlobal.Wealth
