import IeGlobal.Pit
import TaxKernel.Global2

/-!
# IE 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes


## 5200 Motor tax (pass 10, kernel 2.4.0, grade A)
Source: Finance (Excise Duties) (Vehicles) Act 1952, Law Reform Commission Revised Acts (`ie/law/fedva1952_rev.txt`).
* para. 3 (o) (M1 registered on or after 1 January 2021, WLTP CO2): 0 g €120; to 50 €140; to 80 €150; to 90 €160; to 100 €170; to 110 €180; to 120 €190; to 130 €200; to 140 €210; to 150 €270; to 160 €280; to 170 €420; to 190 €600; to 200 €790; to 225 €1,250; above €2,400
* para. 3 (d) (M1 registered 1 July 2008 - 31 December 2020): 0 g €120; to 80 €170; to 100 €180; to 110 €190; to 120 €200; to 130 €270; to 140 €280; to 155 €400; to 170 €600; to 190 €790; to 225 €1,250; above €2,400
* the rates have stood since the Finance Act 2020 (para. 3 (o), annotation F39); the revised text is dated after 2025 and shows no later rate change

* **6000 not levied (cited, gap pass, grade B)**: European Commission TEDB, IE: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 634, 860, 3342, 6522, 329, 642, 644-646, 855, 857-862, 2301) read against the OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 85 (6000: taxes on bases other than those of headings 1000-5000): none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: capital gains tax 1100 / 1200; private health insurance and life and non-life insurance levies 5126; local property tax, vacant homes tax, rates and the non-principal private residence charge 4100; vehicle duties and vehicle registration tax 5200; stamp duty on property and on shares 4400; excise on licences and permits 5200 (§ 14); landfill and plastic bag levies 5128; pension fund stamp duty levy (levied on the assets of pension funds, a property base, not 6000) (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))

* **6000: absence withdrawn (gap pass 2)**: gap pass 2: the cited absence of the gap pass (TEDB list read against the guide) is withdrawn: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVIRL v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/IRL.csv`, SHA256SUMS; general government S13; 2025 not yet published) books revenue under heading 6000: 6200 total 10,0, 13,2, 14,4, 31,3 million EUR in 2021-2024 (unnamed); the national taxes behind it not read
-/

namespace IeGlobal.Other
open TaxKernel TaxKernel.Global

/-- Finance (Excise Duties) (Vehicles) Act 1952, Schedule Part I para. 3 (o): M1 registered from 1 January 2021, WLTP CO2 -/
def p10ieO : QtyTable := QtyTable.ofCeilings [(0, 120), (50, 140), (80, 150), (90, 160), (100, 170), (110, 180), (120, 190), (130, 200), (140, 210), (150, 270), (160, 280), (170, 420), (190, 600), (200, 790), (225, 1250)] 2400
/-- para. 3 (d): M1 registered 1 July 2008 - 31 December 2020, CO2 (NEDC) -/
def p10ieD : QtyTable := QtyTable.ofCeilings [(0, 120), (80, 170), (100, 180), (110, 190), (120, 200), (130, 270), (140, 280), (155, 400), (170, 600), (190, 790), (225, 1250)] 2400
def p10ieVeh : List VehicleTax :=
  [{ name := "Motor tax", kinds := ["car"], regFrom := 2021, parts := [(.co2GKm, p10ieO)], level := .local,    statute := "Finance (Excise Duties) (Vehicles) Act 1952, Sch. Part I para. 3 (o) (WLTP CO2 bands)" },  { name := "Motor tax", kinds := ["car"], regFrom := 2008, regTo := 2020, parts := [(.co2GKm, p10ieD)], level := .local,    statute := "Finance (Excise Duties) (Vehicles) Act 1952, Sch. Part I para. 3 (d) (CO2 bands)" }]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Motor tax (pass 10)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p10ieVeh g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["IE 5200 Motor tax pass 10: Revised Acts, updated to 1 June 2026 (`ie/law/fedva1952_rev.txt`) (grade A)", "IE 6000 gap pass 2: cited absence withdrawn (OECD Revenue Statistics book revenue under 6000)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(vehicleTaxUnknown "Motor tax" p10ieVeh g).isEmpty then ["5200 Motor tax: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Motor tax" p10ieVeh g).isEmpty then ["5200 Motor tax: a vehicle no rule reaches: cars registered before July 2008 (engine-size rates, para. 3 (e)), goods vehicles, motorcycles and other classes (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.firstRegYear == 2008) then ["5200 motor tax: a car of 2008 is taken as registered from 1 July 2008 (para. 3 (d)); earlier ones pay by engine size (para. 3 (e), not modelled)"] else [])
  ++ (if g.vehicles.any (fun v => v.firstRegYear < 2021 && v.co2GKm ≥ 0) then ["5200 motor tax: CO2 of a car registered before 2021 is read as the NEDC value of para. 3 (d)"] else [])
  ++ (if true then ["6000 Other taxes (6000): not modelled (grade C: gap pass 2, OECD Revenue Statistics book revenue under 6000)"] else [])

#guard p10ieO.amount 0 == 120
#guard p10ieO.amount 120 == 190
#guard p10ieO.amount 121 == 200
#guard p10ieO.amount 226 == 2400
#guard p10ieD.amount 140 == 280
#guard p10ieD.amount 141 == 400
#guard (p10ieVeh.head!).amount 2025 { kind := "car", co2GKm := 120, fuel := .petrol, firstRegYear := 2022 } == 190

end IeGlobal.Other
