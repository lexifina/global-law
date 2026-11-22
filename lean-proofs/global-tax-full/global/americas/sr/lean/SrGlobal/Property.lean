import SrGlobal.Pit

/-!
# SR 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (registry: none levied (not cited from a text)): tried no statute read; would unlock: a text showing the abolition or absence.
-/

namespace SrGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon SrGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R5-3k-G, pass 13): Grondwet art. 155 lid 1: \"Belastingen worden geheven krachtens de wet\" (`sr/law/const_art-155.md`). No law read in this build levies a recurrent tax on net wealth (laws read include: Wet BTW 2022 (S.B. 2022 no. 121) art. 4, 21; Wet Inkomstenbelasting art. 47 lid 1: 36 percent; Wet Inkomstenbelasting 1922 art. 1 lid 3, art. 27 lid 2 (S.B. 2024 no. 3): not a binnenlandse bron of a non-resident: no tax, none withheld; Wet Dividendbelasting 1973 arts. 1-6 (S.B. 1981 no. 184, S.B. 1984 no. 109); 1.x model (see its summary.json); Wet Algemeen Pensioen 2014 (S.B. 2014 no. 113, 9 Sep 2014) art. 8: lid 1 3 % of the bijdragegrondslag)." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed"


end SrGlobal.Property
