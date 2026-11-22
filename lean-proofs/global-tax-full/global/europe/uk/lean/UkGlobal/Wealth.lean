import UkGlobal.Pit

/-!
# UK 2025: Wealth family not reached (grade C)

* 4200 Net wealth tax (none recorded (not cited)): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, United Kingdom, Individual - Other taxes, accessed 2025-05-24 (Wayback capture; `law/pwc_indother_wb2025.txt`): annual tax on individuals' wealth: none (PwC WWTS Individual - Other taxes, 2025-05-24 (Wayback capture))
-/

namespace UkGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "annual tax on individuals' wealth: none" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end UkGlobal.Wealth
