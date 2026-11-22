import CzGlobal.Pit
import TaxKernel.Global2

/-!
# CZ 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes


## 5200 Daň silniční (pass 10, kernel 2.4.0, grade A)
Source: Zákon č. 16/1993 Sb., o dani silniční, znění účinné od 1. 1. 2025 (`cz/law/silnicni_zneni-20250101.txt`).
* § 2 odst. 2: "Zdanitelným vozidlem se pro účely daně silniční rozumí silniční vozidlo kategorie N 2 a N 3 a jejich přípojná vozidla kategorie O 3 nebo O 4, pokud jsou registrovaná v registru silničních vozidel v České republice"
* passenger cars (M1), vans (N1), motorcycles (L) and buses (M2, M3) are therefore outside the tax: booked as a cited 0

* **6000 not levied (cited, gap pass, grade B)**: European Commission TEDB, CZ: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 86, 108, 4463, 90, 96, 97, 104, 106, 110, 1281) read against the OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 85 (6000: taxes on bases other than those of headings 1000-5000): none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: administrative fees: fees for services, non-tax (§§ 12-14); fee on building-land betterment 4500; gambling tax 5126 (§ 72); dog fee 5200 (§ 14); motor vehicle entry fees and road tax 5200 (§ 81); fees on entry tickets and on stays 5126 (§ 72); real estate tax 4100; levy on electricity from solar radiation 5128 (a tax on the producers' receipts from one good) (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))

* **6000: absence withdrawn (gap pass 2)**: gap pass 2: the cited absence of the gap pass (TEDB list read against the guide) is withdrawn: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVCZE v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/CZE.csv`, SHA256SUMS; general government S13; 2025 not yet published) books revenue under heading 6000: 6200 other taxes, fees and related payments 509,4 million CZK (2024; 219 to 633 in 2021-2024); the national taxes behind it not read
-/

namespace CzGlobal.Other
open TaxKernel TaxKernel.Global

/-- Zákon o dani silniční 16/1993 Sb. § 2 (2) (od 1. 1. 2022): only N2, N3 and their trailers O3, O4 are taxable -/
def p10czVeh : List VehicleTax :=
  [{ name := "Daň silniční", kinds := ["car", "motorcycle", "van", "bus"],    statute := "zákon 16/1993 Sb. § 2 odst. 2: zdanitelným vozidlem je silniční vozidlo kategorie N2 a N3 a přípojná vozidla O3, O4: cars, motorcycles, vans (N1) and buses are not taxable" }]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Daň silniční (pass 10)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p10czVeh g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["CZ 5200 Daň silniční pass 10: zákony pro lidi, znění od 1. 1. 2025 (`cz/law/silnicni_zneni-20250101.txt`) (grade A)", "CZ 6000 gap pass 2: cited absence withdrawn (OECD Revenue Statistics book revenue under 6000)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(vehicleTaxUnknown "Daň silniční" p10czVeh g).isEmpty then ["5200 Daň silniční: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Daň silniční" p10czVeh g).isEmpty then ["5200 Daň silniční: a vehicle no rule reaches: lorries N2/N3 and trailers O3/O4 (taxable, rates not modelled), other kinds (grade C)"] else [])
  ++ (if true then ["6000 Other taxes (6000): not modelled (grade C: gap pass 2, OECD Revenue Statistics book revenue under 6000)"] else [])

#guard (p10czVeh.head!).amount 2025 { kind := "car", engineCcm := 1600, fuel := .petrol, firstRegYear := 2020 } == 0
#guard (p10czVeh.filter (·.selects 2025 { kind := "truck", fuel := .diesel, firstRegYear := 2020 })).isEmpty

end CzGlobal.Other
