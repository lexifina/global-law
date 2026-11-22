import BsGlobal.Pit

/-!
# BS 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (registry: none levied (not cited from a text)): tried no statute read; would unlock: a text showing the abolition or absence.

**4300 (gap pass 2, 2026-11-22)**: not levied (grade B): Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for The Bahamas (DSD_REV_LAC@DF_REVBHS v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/BHS.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published.
-/

namespace BsGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon BsGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Department of Inland Revenue (inlandrevenue.finance.gov.bs) list of the taxes it administers, `bs/law/dir_home_2025-02-06.*` (Wayback 2025-02-06), names: Value Added Tax, Business Licence, Real Property Tax, stamp duty (DMTT), Condo-Hotel Tax; consolidated index of revenue Acts not held; none of them is a recurrent tax on net wealth." },
   { oecd := .estate, why := "Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for The Bahamas (DSD_REV_LAC@DF_REVBHS v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/BHS.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published." }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end BsGlobal.Property
