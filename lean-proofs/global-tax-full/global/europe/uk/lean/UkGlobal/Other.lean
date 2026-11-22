import UkGlobal.Pit
import TaxKernel.Global2

/-!
# UK 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes


## 5200 Vehicle excise duty (pass 9, kernel 2.4.0, grade A)
Source: Vehicle Excise and Registration Act 1994, Schedule 1, legislation.gov.uk, point-in-time view as at 01/06/2025 (`uk/law/vera1994_sch1_20250601.txt`).
* para. 1GC: the first licence of a car first registered on or after 1 April 2017 is charged by CO2 (Table 1): 0 g £10, to 50 g £110, to 75 £130, to 90 £270, to 100 £350, to 110 £390, to 130 £440, to 150 £540, to 170 £1,360, to 190 £2,190, to 225 £3,300, to 255 £4,680, above £5,490
* para. 1GD: later licences "£195"; para. 1GE: "£620" where the price exceeds £40,000 and the car was first registered less than six years before (if registered before 1 April 2025, only with CO2 above 0)
* para. 1B (cars registered 1 March 2001 - 31 March 2017): £20 to 110 g, £35 to 120, £165, £195, £215, £265, £315, £345, £395, £430, £735 (225-255), £760 above; £430 in the last two rows for cars first registered before 23 March 2006

* FT review (sixth pass): para. 1GE (1) (a) tests the price, para. 1GF (1) the list price (kernel `.listPrice`), not the vehicle's value; without a list price a car first registered from 2020 is grade C.

* FT review (seventh pass): cars first registered before March 2001 (1985-2000 by calendar year) pay the para. 1 general rate: £220 up to 1,549 cc or electrically propelled (para. 1 (2A)), £360 otherwise (para. 1 (2)); before 1985: grade C (historic vehicles).

* **6000 not levied (cited, gap pass, grade B)**: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVGBR v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/GBR.csv`, SHA256SUMS; general government S13; 2025 not yet published): heading 6000 total 0 in 2021-2024: the OECD books no revenue under heading 6000 in any of 2021-2024 (guide § 85: taxes on bases other than those of 1000-5000) (OECD Revenue Statistics 2021-2024 (2025 not yet published); no 6000 tax known in the national law read)
-/

namespace UkGlobal.Other
open TaxKernel TaxKernel.Global

/-- VERA 1994 Sch. 1 para. 1GC Table 1 (first licence, cars first registered on or after 1 April 2017; licences from 1.4.2025) -/
def p9ukFirst : QtyTable := QtyTable.ofCeilings [(0, 10), (50, 110), (75, 130), (90, 270), (100, 350), (110, 390), (130, 440), (150, 540), (170, 1360), (190, 2190), (225, 3300), (255, 4680)] 5490
/-- VERA 1994 Sch. 1 para. 1B table (cars first registered 1 March 2001 - 31 March 2017; licences from 1.4.2025) -/
def p9uk1B : QtyTable := QtyTable.ofCeilings [(100, 20), (110, 20), (120, 35), (130, 165), (140, 195), (150, 215), (165, 265), (175, 315), (185, 345), (200, 395), (225, 430), (255, 735)] 760
/-- para. 1B, cars first registered before 23 March 2006: 430 in the last two rows -/
def p9uk1B06 : QtyTable := QtyTable.ofCeilings [(100, 20), (110, 20), (120, 35), (130, 165), (140, 195), (150, 215), (165, 265), (175, 315), (185, 345), (200, 395), (225, 430), (255, 430)] 430
def p9ukVed : List VehicleTax :=
  [{ name := "Vehicle excise duty", kinds := ["car"], occasion := .registration, regFrom := 2017,    parts := [(.co2GKm, p9ukFirst)], statute := "VERA 1994 Sch. 1 para. 1GC (2), Table 1 (first vehicle licence)" },  { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2020, fixed := 620, when := [(.listPrice, 40000, VehicleTax.noBound), (.co2GKm, 0, VehicleTax.noBound)], statute := "VERA 1994 Sch. 1 para. 1GE (1) (a)-(c), (2): £620 where the price (para. 1GF (1): the list price) exceeds £40,000 and the car is under six years old" },  { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2017, regTo := 2019, fixed := 195, statute := "VERA 1994 Sch. 1 para. 1GD (1): £195" },  { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2020, fixed := 195, when := [(.listPrice, -1, 40000)], statute := "VERA 1994 Sch. 1 para. 1GD (1): £195 (list price £40,000 or less, para. 1GE (1) (a), 1GF)" },  { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2020, regTo := 2024, fixed := 195, when := [(.co2GKm, -1, 0)], statute := "VERA 1994 Sch. 1 para. 1GD (1): £195 (CO2 0 g/km, registered before 1 April 2025: para. 1GE (1) (c) (ii) excludes 1GE)" },  { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2001, regTo := 2005,    parts := [(.co2GKm, p9uk1B06)], statute := "VERA 1994 Sch. 1 para. 1B (registered before 23 March 2006)" },  { name := "Vehicle excise duty", kinds := ["car"], regFrom := 2001, regTo := 2016,    parts := [(.co2GKm, p9uk1B)], statute := "VERA 1994 Sch. 1 para. 1B" },  { name := "Vehicle excise duty", kinds := ["car"], regFrom := 1985, regTo := 2000, fuels := [.electric], fixed := 220, statute := "VERA 1994 Sch. 1 para. 1 (2A): general rate £220, electrically propelled vehicle (first registered before 1 March 2001)" },  { name := "Vehicle excise duty", kinds := ["car"], regFrom := 1985, regTo := 2000, fixed := 220, when := [(.engineCcm, -1, 1549)], statute := "VERA 1994 Sch. 1 para. 1 (2A): general rate £220, cylinder capacity not exceeding 1,549 cc (first registered before 1 March 2001)" },  { name := "Vehicle excise duty", kinds := ["car"], regFrom := 1985, regTo := 2000, fixed := 360, when := [(.engineCcm, 1549, VehicleTax.noBound)], statute := "VERA 1994 Sch. 1 para. 1 (2): general rate £360 (first registered before 1 March 2001)" }]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Vehicle excise duty (pass 9)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p9ukVed g (firstOnly := true) }]

def absent : List Absent :=
  [{ oecd := .other, why := "the OECD books no revenue under heading 6000 in any of 2021-2024 (guide § 85: taxes on bases other than those of 1000-5000)" }]

def notes : List String := ["UK 5200 Vehicle excise duty pass 9: legislation.gov.uk point in time 01/06/2025 (licences from 1.4.2025) (grade A)", "UK 6000 gap pass: not levied (cited, B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(vehicleTaxUnknown "Vehicle excise duty" p9ukVed g).isEmpty then ["5200 Vehicle excise duty: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Vehicle excise duty" p9ukVed g).isEmpty then ["5200 Vehicle excise duty: a vehicle no rule reaches: cars first registered before 1985 (historic vehicles, Sch. 2 para. 1A, not held), motorcycles, vans, lorries and other vehicles (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.fuel == .diesel && v.newReg) then ["5200 Vehicle excise duty: a new diesel car is taken as meeting Euro 6d (Table 2 for other diesels not applied)"] else [])
  ++ (if g.vehicles.any (fun v => v.firstRegYear == 2017 || v.firstRegYear == 2006 || v.firstRegYear == 2001) then ["5200 Vehicle excise duty: registration-year boundaries (1 April 2017, 23 March 2006, 1 March 2001) are taken by calendar year"] else [])
  ++ (if g.vehicles.any (fun v => v.firstRegYear ≥ 2020) then ["5200 Vehicle excise duty: the £40,000 supplement (para. 1GE) is tested on the list price (para. 1GF; non-standard accessories not added) for cars first registered from 2020 (six years read by calendar year)"] else [])
  ++ (if g.vehicles.any (fun v => v.firstRegYear ≥ 1985 && v.firstRegYear ≤ 2000) then ["5200 Vehicle excise duty: a car first registered 1985-2000 pays the para. 1 general rate (£220 / £360 by cylinder capacity, licences from 1.4.2025); one constructed before 1985 would be a historic vehicle (Sch. 2 para. 1A, not held)"] else [])

#guard p9ukFirst.amount 0 == 10
#guard p9ukFirst.amount 120 == 440
#guard p9ukFirst.amount 256 == 5490
#guard p9uk1B.amount 150 == 215
#guard p9uk1B06.amount 260 == 430
#guard (p9ukVed[2]!).amount 2025 { kind := "car", co2GKm := 120, fuel := .petrol, firstRegYear := 2019 } == 195
#guard (p9ukVed[1]!).amount 2025 { kind := "car", co2GKm := 120, fuel := .diesel, firstRegYear := 2022, value := 30842, listPrice := 50221 } == 620
#guard (p9ukVed[3]!).amount 2025 { kind := "car", co2GKm := 120, fuel := .petrol, firstRegYear := 2022, value := 45000, listPrice := 39000 } == 195
#guard (p9ukVed[1]!).computes 2025 { kind := "car", co2GKm := 120, fuel := .petrol, firstRegYear := 2022, value := 45000 } == false
#guard (p9ukVed[3]!).computes 2025 { kind := "car", co2GKm := 120, fuel := .petrol, firstRegYear := 2022, value := 45000 } == false
#guard (p9ukVed[7]!).amount 2025 { kind := "car", fuel := .electric, firstRegYear := 1998 } == 220
#guard (p9ukVed[8]!).amount 2025 { kind := "car", engineCcm := 1549, fuel := .petrol, firstRegYear := 1999 } == 220
#guard (p9ukVed[9]!).amount 2025 { kind := "car", engineCcm := 1550, fuel := .diesel, firstRegYear := 1999 } == 360
#guard (p9ukVed[9]!).computes 2025 { kind := "car", engineCcm := 1550, fuel := .diesel, firstRegYear := 2001 } == false
#guard (p9ukVed[8]!).computes 2025 { kind := "car", fuel := .petrol, firstRegYear := 1999 } == false
#guard (p9ukVed[8]!).computes 2025 { kind := "car", engineCcm := 1200, fuel := .petrol, firstRegYear := 1984 } == false

end UkGlobal.Other
