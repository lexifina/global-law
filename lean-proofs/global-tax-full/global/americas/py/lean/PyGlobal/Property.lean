import PyGlobal.Pit

/-!
# PY 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (none read): tried not read in this pass; would unlock: the act's 2025 text.

**4300 (gap pass 2, 2026-11-22)**: not levied (grade B): Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Paraguay (DSD_REV_LAC@DF_REVPRY v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/PRY.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published.
-/

namespace PyGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon PyGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R5-3k-G, pass 12): Constitución art. 179: \"Todo tributo, cualquiera sea su naturaleza o denominación, será establecido exclusivamente por la ley\" (`py/law/const_art-179.md`). no law read in this build levies a recurrent tax on net wealth (laws read include: Ley 6380/19 arts. 85-100; Ley 6380/19 art. 21 (10 %); Ley 6380/19 art. 43 2 (IDU 15 %, non-resident); 1.x model (see its summary.json); Ley 6380/2019 arts. 53, 56, 59, 60; Ley 98/1992 (not read))." },
   { oecd := .estate, why := "Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Paraguay (DSD_REV_LAC@DF_REVPRY v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/PRY.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published." }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end PyGlobal.Property
