import ByGlobal.Pit

/-!
# BY 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (государственная пошлина on inheritance certificates): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Belarus, Individual - Other taxes, accessed 2021-11-30 (Wayback capture; `law/pwc_indother_wb2025.txt`): wealth tax: none (2021 capture, the newest archived) (PwC WWTS Individual - Other taxes, 2021-11-30 (Wayback capture))

* **4300 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Belarus, Individual - Other taxes, accessed 2021-11-30 (Wayback capture; `law/pwc_indother_wb2025.txt`): inheritance / gift tax: none as such; receipts fall under the PIT (inheritances exempt, gifts partly exempt; the 1.x PIT) (PwC WWTS Individual - Other taxes, 2021-11-30 (Wayback capture))
-/

namespace ByGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "net wealth tax: none in 2025 (Особенная часть, разделы V-VII: no such tax among the republican and local taxes)" },
   { oecd := .estate, why := "inheritance / gift tax: none in 2025 (no such chapter; ст. 208 п. 21, 22, 22-1: inheritances and close-family gifts exempt from подоходный налог, other gifts above 11 516 рублей are income)" }]

def notes : List String := ["BY 4200 Net wealth tax (not levied): back to B (pass 18, 2025 text read)", "BY 4300 Inheritance and gift tax (not levied): back to B (pass 18, 2025 text read)"]

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end ByGlobal.Wealth
