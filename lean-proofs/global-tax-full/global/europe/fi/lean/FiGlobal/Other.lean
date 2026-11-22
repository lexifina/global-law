import FiGlobal.Pit

/-!
# FI 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes

* **6000 not levied (cited, gap pass, grade B)**: European Commission TEDB, FI: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 241, 242, 262, 623, 625, 2901, 246, 251, 252, 253, 264, 621, 2001, 5066) read against the OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 85 (6000: taxes on bases other than those of headings 1000-5000): none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: gift and inheritance taxes 4300; real property tax 4100; non-residents' income and interest withholding 1100 / 1200; public broadcasting tax 1100 (levied on taxable income); beverage-package, soft-drink and waste taxes 5128; insurance premium tax 5126; car registration tax 5200 (§ 83); transfer tax 4400; vehicle tax 5200; pharmacy tax 5126 (§ 72) (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))


## 6000 Kirkollisvero (evankelis-luterilainen ja ortodoksinen kirkko): not a tax (OECD guide § 6) (gap pass, grade C)
Source: Tuloverolaki (1535/1992) 124 § (deductions shared among municipal tax, health-care contribution and church tax, `fi/law/tvl_wb20250703.txt`); Statistics Finland, Taxes and tax-like payments: documentation of statistics (stat.fi/en/statistics/documentation/vermak, fetched 2026-11-22, `fi/law/statfi_vermak_doc.html`).
* OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 6: church taxes are included only in countries where the church forms part of general government; levies paid to non-government bodies are excluded even where compulsory, unless the government is more than an agent
* not a tax (OECD guide § 6, as decided for the Nordic church taxes): levied by the parishes, collected by Verohallinto with the municipal tax; the 1.x model charges it only with `churchRateBp` (default 0). The OECD Revenue Statistics table for Finland (DSD_REV_OECD@DF_REVFIN, `tools/in_gap2/oecd/FIN.csv`) has one church line, 1210 Church tax, at 0 in 2021-2024, and its 1100 lines (communal tax, tax on income, final withholding tax on interest) name no church tax: the individuals' church tax is outside the general-government figures

* **6000: absence withdrawn (gap pass 2)**: gap pass 2: the cited absence of the gap pass (TEDB list read against the guide) is withdrawn: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVFIN v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/FIN.csv`, SHA256SUMS; general government S13; 2025 not yet published) books revenue under heading 6000: 6200 total 108, 87, 79, 103 million EUR in 2021-2024 (unnamed); the national taxes behind it not read
-/

namespace FiGlobal.Other
open TaxKernel TaxKernel.Global



def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := ["FI gap pass: Kirkollisvero (evankelis-luterilainen ja ortodoksinen kirkko)", "FI 6000 gap pass 2: cited absence withdrawn (OECD Revenue Statistics book revenue under 6000)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["5200 Taxes on use of goods (motor vehicle taxes): not modelled (grade C: not read in the P7 pass)"] else [])
  ++ (if true then ["6000 Other taxes (6000): not modelled (grade C: gap pass 2, OECD Revenue Statistics book revenue under 6000)"] else [])


end FiGlobal.Other
