import DkGlobal.Pit
import TaxKernel.Global2

/-!
# DK 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes


## 5200 Brændstofforbrugsafgift (grøn ejerafgift) (pass 11, kernel 2.4.0, grade A)
Source: Bekendtgørelse af lov om afgift efter brændstofforbrug m.v. for visse person- og varebiler (brændstofforbrugsafgiftsloven), LBK nr. 1050 af 12/08/2025, retsinformation.dk (`dk/law/bfa_lbk2025_1050.txt`).
* § 3 c stk. 1: cars first registered on 1 July 2021 or later pay by WLTP CO2 g/km: per six months 390 kr up to 58 g, rising by bands to 13 650 kr above 645 g; diesel cars also pay udligningsafgift (160 kr to 6 530 kr)
* § 3 c stk. 3: for 2025 the CO2 amounts rise by 6,5 %; stk. 4: for 2025 and 2026 the udligningsafgift falls by 30 %; both rounded up to whole kroner divisible by ten
* § 4: six-month periods, paid from the day of registration: the model books two periods for a car held all year (prorated by months otherwise)
* § 3 b: diesel cars without a measured particle emission of at most 5 mg/km pay 1 000 kr a year more (not in the input)

* **6000 not levied (cited, gap pass, grade B)**: European Commission TEDB, DK: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 140-199, 757, 147-186, 610, 1941, 2681, 6822-6824, 174, 196) read against the OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 85 (6000: taxes on bases other than those of headings 1000-5000): none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: estate and gift taxes 4300; property value tax and municipal land tax 4100; share income and claims taxation 1100 / 1200; tax on the yield of pension scheme assets 1100; duty on wage and salary costs (lønsumsafgift) 3000 (§ 47); the product and environmental excises (CFCs, chocolate, coffee, packaging, water, nitrogen, sulphur and others) 5121 / 5128; insurance taxes 5126; car registration, weight and green taxes, road charges 5200; gambling and air passenger taxes 5126 (§ 72); EU ETS sector CO2 tax 5128; financial levy on commercial premises 4100 (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))


## 6000 Kirkeskat (folkekirken): not a tax (OECD guide § 6) (gap pass, grade C)
Source: Danmarks Statistik, Statistikbanken table SKAT (Skatter og afgifter, general government finances, ESA 2010; 219 tax types, none for kirkeskat: 1.1.01-1.1.07 then 1.1.09), fetched 2026-11-22 through api.statbank.dk (`dk/law/dst_skat_tableinfo_da.json`, `dk/law/dst_skat_tableinfo_en.json`); the church-tax statute (lov om folkekirkens økonomi) not read; the OECD Revenue Statistics table for Denmark (`tools/in_gap2/oecd/DNK.csv`) has no church-tax line either.
* OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 6: church taxes are included only in countries where the church forms part of general government; levies paid to non-government bodies are excluded even where compulsory, unless the government is more than an agent
* not a tax (OECD guide § 6): Statistics Denmark's table of general-government taxes (ESA 2010) has no church-tax line; the 1.x line keeps kirkeskat at the default municipality's rate (DKTax `churchRate7`) as it is, so the global pit includes it although it is not a tax in OECD terms

* **6000: absence withdrawn (gap pass 2)**: gap pass 2: the cited absence of the gap pass (TEDB list read against the guide) is withdrawn: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVDNK v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/DNK.csv`, SHA256SUMS; general government S13; 2025 not yet published) books revenue under heading 6000: 6200 Other taxes 4 461,9 million DKK (2024); heading total 1 339 to 5 889 million DKK in 2021-2024; the national taxes behind it not read
-/

namespace DkGlobal.Other
open TaxKernel TaxKernel.Global

/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1

/-- brændstofforbrugsafgiftsloven § 3 c stk. 1 A, stk. 3: CO2-baseret afgift for 2025 (half-year amounts + 6,5 %, rounded up to
10 kr, two periods), kroner a year by g CO2/km -/
def p11dkA : QtyTable := QtyTable.ofCeilings [(58, 840), (65, 940), (73, 980), (80, 1040), (87, 1100), (102, 1160), (116, 1260), (131, 1380), (145, 1460), (160, 2220), (174, 2980), (189, 3780), (203, 4540), (218, 5300), (232, 6060), (246, 6800), (262, 7600), (277, 8360), (290, 9120), (319, 10620), (350, 12220), (377, 13720), (409, 15240), (433, 16780), (461, 18320), (492, 19840), (519, 21380), (548, 22960), (581, 24480), (605, 26000), (645, 27500)] 29080
/-- § 3 c stk. 1 A, stk. 4: udligningsafgift for diesel cars, 2025 (half-year amounts − 30 %, rounded up to 10 kr), a year -/
def p11dkU : QtyTable := QtyTable.ofCeilings [(58, 240), (65, 240), (73, 240), (80, 240), (87, 240), (102, 240), (116, 1040), (131, 1860), (145, 2000), (160, 2200), (174, 2380), (189, 2560), (203, 2760), (218, 2940), (232, 3180), (246, 3360), (262, 3600), (277, 3760), (290, 3940), (319, 4360), (350, 4720), (377, 5100), (409, 5540), (433, 5860), (461, 6220), (492, 6680), (519, 7040), (548, 7420), (581, 7840), (605, 8240), (645, 8740)] 9160
def p11dkVeh : List VehicleTax :=
  [{ name := "Brændstofforbrugsafgift (grøn ejerafgift)", kinds := ["car"], fuels := [.diesel], regFrom := 2021, parts := [(.co2GKm, p11dkA), (.co2GKm, p11dkU)],    statute := "brændstofforbrugsafgiftsloven § 3 c stk. 1 A, stk. 3, 4: CO2-baseret afgift and udligningsafgift (diesel), cars first registered from 1 July 2021, 2025 amounts" },  { name := "Brændstofforbrugsafgift (grøn ejerafgift)", kinds := ["car"], fuels := [.petrol, .electric, .hybrid, .pluginHybrid, .lpg, .cng, .hydrogen, .other], regFrom := 2021,    parts := [(.co2GKm, p11dkA)],    statute := "brændstofforbrugsafgiftsloven § 3 c stk. 1 A, stk. 3: CO2-baseret afgift, cars first registered from 1 July 2021, 2025 amounts" }]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Brændstofforbrugsafgift (grøn ejerafgift) (pass 11)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p11dkVeh g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["DK 5200 Brændstofforbrugsafgift (grøn ejerafgift) pass 11: retsinformation.dk, LBK nr. 1050 af 12/08/2025 (`dk/law/bfa_lbk2025_1050.txt`) (grade A)", "DK gap pass: Kirkeskat (folkekirken)", "DK 6000 gap pass 2: cited absence withdrawn (OECD Revenue Statistics book revenue under 6000)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(vehicleTaxUnknown "Brændstofforbrugsafgift (grøn ejerafgift)" p11dkVeh g).isEmpty then ["5200 Brændstofforbrugsafgift (grøn ejerafgift): a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Brændstofforbrugsafgift (grøn ejerafgift)" p11dkVeh g).isEmpty then ["5200 Brændstofforbrugsafgift (grøn ejerafgift): a vehicle no rule reaches: cars first registered before July 2021 (km/l tables of § 3, not an input attribute), vans, other kinds (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.firstRegYear == 2021) then ["5200 grøn ejerafgift: a car first registered in 2021 is taken as registered from 1 July 2021 (§ 3 c)"] else [])
  ++ (if g.vehicles.any (fun v => v.fuel == .diesel) then ["5200 grøn ejerafgift: a diesel car is taken as having a measured particle emission of at most 5 mg/km (no § 3 b surcharge of 1 000 kr)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg) then ["5200 registreringsafgift (registreringsafgiftsloven) on a car registered in the year not modelled (grade C)"] else [])
  ++ (if true then ["6000 Other taxes (6000): not modelled (grade C: gap pass 2, OECD Revenue Statistics book revenue under 6000)"] else [])

#guard p11dkA.amount 120 == 1380
#guard p11dkA.amount 58 == 840
#guard p11dkA.amount 646 == 29080
#guard p11dkU.amount 100 == 240
#guard p11dkU.amount 140 == 2000
#guard p11amt p11dkVeh { kind := "car", fuel := .petrol, co2GKm := 120, firstRegYear := 2023 } == 1380
#guard p11amt p11dkVeh { kind := "car", fuel := .diesel, co2GKm := 140, firstRegYear := 2022 } == 3460
#guard p11amt p11dkVeh { kind := "car", fuel := .electric, co2GKm := 0, firstRegYear := 2024 } == 840
#guard p11amt p11dkVeh { kind := "car", fuel := .petrol, co2GKm := 120, firstRegYear := 2019 } == -1

end DkGlobal.Other
