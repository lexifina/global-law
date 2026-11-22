import GdGlobal.Pit

/-!
# GD 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (registry: none levied (not cited from a text)): tried no statute read; would unlock: a text showing the abolition or absence.

**4300 (gap pass 2, 2026-11-22)**: not levied (grade B): Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Grenada (DSD_REV_LAC@DF_REVGRD v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/GRD.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published.
-/

namespace GdGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon GdGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Inland Revenue Division (ird.gd) list of the taxes it administers, `gd/law/ird_home_2025-01-17.*` (Wayback 2025-01-17), names: Income Tax, Property Tax, Property Transfer Tax, Excise Tax, Withholding Tax, Value Added Tax, Annual Stamp Tax, Gaming Tax, Motor Vehicle Licence, licences; consolidated index of revenue Acts not held; none of them is a recurrent tax on net wealth." },
   { oecd := .estate, why := "Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Grenada (DSD_REV_LAC@DF_REVGRD v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/GRD.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published." }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end GdGlobal.Property
