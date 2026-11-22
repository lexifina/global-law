import HtGlobal.Pit

/-!
# HT 2025: Consumption family — no dated statute text reached (grade C)

* Taxe sur le chiffre d'affaires (TCA) (DÃ©cret TCA (2005) / DÃ©cret du 19 dÃ©cembre 2022): tried only the 2026 Code Fiscal (Le Moniteur 30.9.2026, in force 1.10.2026) is on dgi.gouv.ht; the 2025 law not found; would unlock: the DÃ©cret in force in 2025 (Le Moniteur).
* Droits d'accises (Loi du 3 septembre 1971 (as amended)): tried same; would unlock: the 2025 accise texts.
-/

namespace HtGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon HtGlobal

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Taxe sur le chiffre d'affaires (TCA); Droits d'accises: statute not reached in a dated form (grade C): not computed"


end HtGlobal.Consumption
