import MtGlobal.Pit

/-!
# MT 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes

* **6000 not levied (cited, gap pass, grade B)**: European Commission TEDB, MT: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 425, 431-433, 671-673, 678, 680, 1901, 4427) read against the OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 85 (6000: taxes on bases other than those of headings 1000-5000): none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: annual circulation tax 5200; gaming and lotteries 5126 (§ 72); duty on documents and transfers 4400 (immovables, property transfers) and 5126 (insurance policies); mobile telephony excise duty 5126; fees for rights of use 5200; motor vehicle registration tax 5200 (§ 83); cement excise 5121 (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))
-/

namespace MtGlobal.Other
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .other, why := "none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: annual circulation tax 5200; gaming and lotteries 5126 (§ 72); duty on documents and transfers 4400 (immovables, property transfers) and 5126 (insurance policies); mobile telephony excise duty 5126; fees for rights of use 5200; motor vehicle registration tax 5200 (§ 83); cement excise 5121" }]

def notes : List String := ["MT 6000 gap pass: not levied (cited, B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["5200 Taxes on use of goods (motor vehicle taxes): not modelled (grade C: not read in the P7 pass)"] else [])


end MtGlobal.Other
