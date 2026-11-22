import AgGlobal.Pit

/-!
# AG 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (registry: none levied (not cited from a text)): tried no statute read; would unlock: a text showing the abolition or absence.

**4300 (gap pass 2, 2026-11-22)**: not levied (grade B): Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Antigua and Barbuda (DSD_REV_LAC@DF_REVATG v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/ATG.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published.
-/

namespace AgGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon AgGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Inland Revenue Department (ird.gov.ag) list of the taxes it administers, `ag/law/ird_home_2025-01-14.*` (Wayback 2025-01-14) with its linked list 'Taxes, Duties, Levies & Fees Administered by the IRD' (`ag/law/ird_taxes_administered_2021.*`), names: (2021 table, OCR `ag/law/ird_taxes_administered_2021.ocr.txt`) Antigua and Barbuda Sales Tax, Unincorporated Business Tax, property tax, undeveloped land tax, non-citizen land holding tax, stamp duty, travel tax, slot machine tax, withholding tax, insurance and money-transfer levies, licences; the 2025 home page adds corporate income tax and the Tourism Guest Levy; consolidated index of revenue Acts not held; none of them is a recurrent tax on net wealth." },
   { oecd := .estate, why := "Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Antigua and Barbuda (DSD_REV_LAC@DF_REVATG v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/ATG.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published." }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end AgGlobal.Property
