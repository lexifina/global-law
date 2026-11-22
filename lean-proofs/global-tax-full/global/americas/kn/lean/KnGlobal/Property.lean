import KnGlobal.Pit

/-!
# KN 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (registry: none levied (not cited from a text)): tried no statute read; would unlock: a text showing the abolition or absence.
-/

namespace KnGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon KnGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Inland Revenue Department (sknird.com) list of the taxes it administers, `kn/law/ird_tax_laws_2025-03-22.*` (Wayback 2025-03-22), names: Property Tax, Value Added Tax, Corporate Income Tax, Driver's and Vehicle Licence; consolidated index of revenue Acts not held; none of them is a recurrent tax on net wealth." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed"


end KnGlobal.Property
