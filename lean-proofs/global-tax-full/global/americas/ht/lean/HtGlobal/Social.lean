import HtGlobal.Pit

/-!
# HT 2025: Social family — no dated statute text reached (grade C)

* Employer social security contributions (Loi ONA / OFATMA): tried employer rates not in the 1.x builder's texts; the act was not fetched; would unlock: the act or regulation fixing the 2025 employer rates.
-/

namespace HtGlobal.Social
open TaxKernel TaxKernel.Global AmerCommon HtGlobal

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Employer social security contributions: statute not reached in a dated form (grade C): not computed"


end HtGlobal.Social
