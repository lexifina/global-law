import LuGlobal.Pit

/-!
# LU 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (Taxe d'abonnement on funds (0.05 %/0.01 %)): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor here: taxe d'abonnement concerns funds only

* **6000 not levied (cited, gap pass, grade B)**: European Commission TEDB, LU: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 391, 392, 788, 4003, 398, 403, 2502) read against the OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 85 (6000: taxes on bases other than those of headings 1000-5000): none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: inheritance tax 4300; wealth tax (companies) 4200 (§ 51); withholding taxes on interest and capital income 1100 / 1200; insurance tax 5126; registration taxes 4400; tax on motor vehicles 5200; the registry's item, the taxe d'abonnement, is levied on the net assets of investment funds: a 4200 tax on corporate net wealth (§ 51), not 6000, outside the modelled entities (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))

* **6000: absence withdrawn (gap pass 2)**: gap pass 2: the cited absence of the gap pass (TEDB list read against the guide) is withdrawn: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVLUX v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/LUX.csv`, SHA256SUMS; general government S13; 2025 not yet published) books revenue under heading 6000: 6100 chancellery stamps, taxes on electricity production and distribution, natural gas consumption, water, foreign-affairs services (34,2 million EUR in 2024); the national taxes behind it not read
-/

namespace LuGlobal.Other
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := ["LU 6000 gap pass 2: cited absence withdrawn (OECD Revenue Statistics book revenue under 6000)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["5200 Taxes on use of goods (motor vehicle taxes): not modelled (grade C: not read in the P7 pass)"] else [])
  ++ (if true then ["6000 Other taxes (6000): not modelled (grade C: gap pass 2, OECD Revenue Statistics book revenue under 6000)"] else [])


end LuGlobal.Other
