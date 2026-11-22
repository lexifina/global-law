import ClGlobal.Pit

/-!
# CL 2025: Social family — no dated statute text reached (grade C)

* Seguro de cesantía (employer), SIS, Ley 21.735 employer contribution (Ley 19.728 art. 5; DL 3.500 art. 59; Ley 21.735): tried LeyChile reachable but not read in this pass; would unlock: LeyChile versions of Ley 19.728 and Ley 21.735 (from 1.8.2025).
-/

namespace ClGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon ClGlobal

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Seguro de cesantía (employer), SIS, Ley 21.735 employer contribution: statute not reached in a dated form (grade C): not computed"


end ClGlobal.Social
