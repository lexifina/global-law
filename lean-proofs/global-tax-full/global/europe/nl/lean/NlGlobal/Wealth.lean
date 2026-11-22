import NlGlobal.Pit

/-!
# NL 2025: Wealth family not reached (grade C)

* 4200 Net wealth tax (box 3 is an income tax (P3)): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)

* **4200 not levied (cited, pass 6, grade B)**: PwC Worldwide Tax Summaries, Netherlands, Individual - Other taxes, accessed 2025-07-18 (Wayback capture; `law/pwc_indother_wb2025.txt`): wealth tax: none as such; deemed return on savings and investments taxed in box 3 of the income tax (1100, the 1.x model) (PwC WWTS Individual - Other taxes, 2025-07-18 (Wayback capture))
-/

namespace NlGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "wealth tax: none as such; deemed return on savings and investments taxed in box 3 of the income tax (1100, the 1.x model)" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end NlGlobal.Wealth
