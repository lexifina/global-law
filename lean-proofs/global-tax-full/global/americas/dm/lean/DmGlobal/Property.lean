import DmGlobal.Pit

/-!
# DM 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (registry: none levied (not cited from a text)): tried no statute read; would unlock: a text showing the abolition or absence.
-/

namespace DmGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon DmGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Inland Revenue Division (ird.gov.dm) list of the taxes it administers, `dm/law/ird_tax_laws_2025-01-21.*` and `dm/law/ird_past_taxes_2025-04-18.*` (Wayback 2025), names: Corporate Income Tax, Personal Income Tax, Withholding Tax, Value Added Tax, Excise Tax, Travel Tax, Licenses; 'Past Taxes' (the Sales Tax replaced by the VAT among them); consolidated index of revenue Acts not held; none of them is a recurrent tax on net wealth." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed"


end DmGlobal.Property
