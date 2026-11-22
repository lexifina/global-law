import BbGlobal.Pit

/-!
# BB 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (registry: none levied (not cited from a text)): tried no statute read; would unlock: a text showing the abolition or absence.

**4300 (gap pass 2, 2026-11-22)**: not levied (grade B): Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Barbados (DSD_REV_LAC@DF_REVBRB v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/BRB.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. The Estate Duty (Waiver) Act, Cap. 65 s. 2 (lexifina/barbados-law estate-duty-waiver, official source barbadoslawcourts.gov.bb) waives the estate and succession duties of the Estate Duty Act, 1895 for deaths on or before 31 March 1981; no later estate or succession duty is known. 2025 revenue statistics not yet published.
-/

namespace BbGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon BbGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Barbados (DSD_REV_LAC@DF_REVBRB v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/BRB.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. The Estate Duty (Waiver) Act, Cap. 65 s. 2 (lexifina/barbados-law estate-duty-waiver, official source barbadoslawcourts.gov.bb) waives the estate and succession duties of the Estate Duty Act, 1895 for deaths on or before 31 March 1981; no later estate or succession duty is known. 2025 revenue statistics not yet published." }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end BbGlobal.Property
