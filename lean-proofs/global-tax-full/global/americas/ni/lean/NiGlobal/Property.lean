import NiGlobal.Pit

/-!
# NI 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (Ley 822 (ganancias de capital on inheritances)): tried not read in this pass; would unlock: the act's 2025 text.
-/

namespace NiGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon NiGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 108: \"Los tributos se crean, modifican y derogan por ley\" (`ni/law/const_articulo-108.md`). no law read in this build levies a recurrent tax on net wealth (laws read include: Ley 822 arts. 109, 127; Ley 822 art. 52 (30 %); Ley 822 arts. 53, 87, 89 (Ley 891 of 2014, Ley 987 of 2019); 1.x model (see its summary.json); Ley 822 arts. 82, 83, 87 (Ley 891, Ley 987); Decreto 975 arts. 11 (2), 16 as reformed by Decreto Presidencial 06-2019)." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed"


end NiGlobal.Property
