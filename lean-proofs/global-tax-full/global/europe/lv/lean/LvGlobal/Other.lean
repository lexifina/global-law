import LvGlobal.Pit

/-!
# LV 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes

* **6000 not levied (cited, gap pass, grade B)**: European Commission TEDB, LV: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 4447, 4542, 6825, 406, 412, 416, 789, 1081, 1102) read against the OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 85 (6000: taxes on bases other than those of headings 1000-5000): none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: solidarity tax and contributions 2000 / 1100 (on earnings above the contribution ceiling); immovable property tax 4100; excise duty on other excise goods 5121; natural resources tax 5128 / 5200; lotteries and gambling tax 5126; state fee for registering ownership rights 4400; company car tax and vehicle operation tax 5200 (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))
-/

namespace LvGlobal.Other
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .other, why := "none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: solidarity tax and contributions 2000 / 1100 (on earnings above the contribution ceiling); immovable property tax 4100; excise duty on other excise goods 5121; natural resources tax 5128 / 5200; lotteries and gambling tax 5126; state fee for registering ownership rights 4400; company car tax and vehicle operation tax 5200" }]

def notes : List String := ["LV 6000 gap pass: not levied (cited, B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["5200 Taxes on use of goods (motor vehicle taxes): not modelled (grade C: not read in the P7 pass)"] else [])


end LvGlobal.Other
