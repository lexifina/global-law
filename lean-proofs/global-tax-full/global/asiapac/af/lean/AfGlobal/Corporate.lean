import AfGlobal.Pit

/-!
# Afghanistan 2025: income tax of legal persons and withholding (1200)

Source: Income Tax Law 2009, MoF consolidation "Version: December 2016" (`itl.txt`; 2025 application not confirmed: grade B).
* **art. 4 (1)**: "The income tax of legal persons shall be 20" percent.
* **art. 46 (1) 2**: legal persons withhold "twenty percent tax from interest, dividends, royalties, prizes, … and service
  charges".
-/

namespace AfGlobal.Corporate
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["session 11 year-in-force audit: the only text is the MoF consolidation 'Version: December 2016' of the Income Tax Law 2009; no 2025 version, amendment list or 2025 official source reached (the 2025 application of the 2016 text is not established): grade C"] else [])


end AfGlobal.Corporate
