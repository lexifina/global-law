import DeGlobal.Pit

/-!
# DE 2025: Wealth family not reached (grade C)

* 4200 Net wealth tax (Vermögensteuer not levied since 1997 (VStG suspended, BVerfG 1995): not cited): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Germany, Individual - Other taxes, accessed 2025-06-23 (Wayback capture; `law/pwc_indother_wb2025.txt`): Vermögensteuer: not levied at present (PwC WWTS Individual - Other taxes, 2025-06-23 (Wayback capture))
-/

namespace DeGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Vermögensteuer: not levied at present" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end DeGlobal.Wealth
