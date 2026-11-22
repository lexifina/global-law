import TtGlobal.Pit

/-!
# TT 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (registry: none levied (not cited from a text)): tried no statute read; would unlock: a text showing the abolition or absence.

**4300 (gap pass 2, 2026-11-22)**: not levied (grade B): Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Trinidad and Tobago (DSD_REV_LAC@DF_REVTTO v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/TTO.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published.
-/

namespace TtGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon TtGlobal

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .wealth, why := "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Board of Inland Revenue (ird.gov.tt) list of the taxes it administers, `tt/law/ird_legislation_2025-01-19.*` ('Legislation and Tax Laws', Wayback 2025-01-19), names: Petroleum Taxes Act, Value Added Tax Act, Income Tax Act, Corporation Tax Act, Property Tax Act, Stamp Duty; consolidated index: lexifina/trinidad-and-tobago-law@ed76505a0355 `laws.csv` (`tt/law/lexifina_tt_laws_index.csv`, every Chapter on laws.gov.tt): the revenue Chapters are 74:01, 75:01 Income Tax, 75:02 Corporation Tax, 75:03 Unemployment Levy, 75:04 Petroleum Taxes, 75:06 Value Added Tax, 76:01 and 76:03 Stamp Duty, 76:04 Property Tax, 77:01 Miscellaneous Taxes, 62:02 Petroleum Production Levy; none of them is a recurrent tax on net wealth." },
   { oecd := .estate, why := "Not levied (grade B, gap pass 2, 2026-11-22): the OECD Revenue Statistics detailed table for Trinidad and Tobago (DSD_REV_LAC@DF_REVTTO v2.1, sdmx.oecd.org, fetched 2026-11-21 with a plain research user-agent, copy americas/p7t/oecd/TTO.csv): general government heading 4300 (estate, inheritance and gift taxes) = 0.0 in 2021, 2022, 2023 and 2024, no 4310 or 4320 line; Interpretative Guide §52 (4300 = taxes on estates, inheritances and gifts). No estate, inheritance or gift tax is known in the national law. 2025 revenue statistics not yet published." }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []


end TtGlobal.Property
