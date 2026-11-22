import HtGlobal.Pit

/-!
# HT 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (registry: none levied (not cited from a text)): tried no statute read; would unlock: a text showing the abolition or absence.
-/

namespace HtGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon HtGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R5-3k-G, pass 12): Constitution art. 218: \"Aucun impôt au profit de l'État ne peut être établi que par une loi\" (`ht/law/const_art-218.md`). no law read in this build levies a recurrent tax on net wealth (laws read include: Décret du 29 septembre 2005 art. 149 B, 150-153; 1.x model (see its summary.json))." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed"


end HtGlobal.Property
