import VcGlobal.Pit

/-!
# VC 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (registry: none levied (not cited from a text)): tried no statute read; would unlock: a text showing the abolition or absence.
-/

namespace VcGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon VcGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Inland Revenue Department (ird.gov.vc) list of the taxes it administers, `vc/law/ird_taxes_20250425024416.*` ('List of Taxes: The following taxes are administered by the Inland Revenue Department', Wayback 2025-04-25), names: Corporate Income Tax, Value Added Tax, Personal Income Tax, Withholding Taxes, Excise Tax, Climate Resiliency Levy, PAYE, Travel Tax, Insurance Business Tax, Property Tax; consolidated index of revenue Acts not held; none of them is a recurrent tax on net wealth." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed"


end VcGlobal.Property
