import HrGlobal.Pit
import TaxKernel.Global2

/-!
# HR 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes


## 5200 Porez na cestovna motorna vozila (pass 11, kernel 2.4.0, grade B)
Source: Zakon o lokalnim porezima, pročišćeni tekst (NN 115/16 to 152/24), zakon.hr via the Internet Archive 2025-06-15 (`hr/law/zlp_zakonhr_wb20250615.txt`); NN 115/2016 (`hr/law/nn2016_115_2524_zlp.txt`).
* čl. 11 st. 1: owners of passenger cars, motorcycles and quadricycles pay the tax once a year, on registration or extension of the registration
* čl. 11 st. 3 t. 1 (cars, EUR): up to 55 kW 40 / 33 / 27; 55-70 kW 53 / 46 / 33; 70-100 kW 80 / 66 / 53; 100-130 kW 119 / 93 / 80; above 130 kW 199 / 159 / 133, for up to 2, 2 to 5 and 5 to 10 years of age; the table has no row for older vehicles
* čl. 12 st. 3: a vehicle acquired during the year and not registered before pays the annual tax less the part of the year before the purchase (the model prorates by months held)
* grade B: the euro amounts (NN 114/22) are read in an unofficial consolidated text; the 2016 Narodne novine text (kuna) agrees in structure

* **6000 not levied (cited, gap pass, grade B)**: European Commission TEDB, HR: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 3181, 3201-3213, 3221, 3222) read against the OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 85 (6000: taxes on bases other than those of headings 1000-5000): none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: real estate transfer tax 4400; taxes and fees on games of chance and winnings 5126 / 5200 (§§ 14, 72); tax on road motor vehicles 5200; special tax on coffee and soft drinks 5128; special tax on motor vehicles 5200 (§ 83) (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))
-/

namespace HrGlobal.Other
open TaxKernel TaxKernel.Global

/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1

def p11hrCar (a b c d e : Int) : QtyTable := QtyTable.ofCeilings [(55, a), (70, b), (100, c), (130, d)] e
def p11hrMoto (a b c d : Int) : QtyTable := QtyTable.ofCeilings [(20, a), (50, b), (80, c)] d
def p11hrPcmv : String := "Porez na cestovna motorna vozila"
def p11hrRow (k : String) (lo hi : Int) (t : QtyTable) (st : String) : VehicleTax :=
  { name := p11hrPcmv, kinds := [k], «when» := [(.age, lo, hi)], parts := [(.engineKw, t)], level := .local, statute := st }
def p11hrVeh : List VehicleTax :=
  [{ name := p11hrPcmv, kinds := ["car", "motorcycle"], «when» := [(.age, 10, VehicleTax.noBound)], level := .local,    statute := "Zakon o lokalnim porezima čl. 11 st. 3: the tables stop at 10 years of age: older cars and motorcycles pay none" },  p11hrRow "car" (-1) 2 (p11hrCar 40 53 80 119 199) "Zakon o lokalnim porezima čl. 11 st. 3 t. 1: osobni automobili up to 2 years of age, EUR by kW",  p11hrRow "car" 2 5 (p11hrCar 33 46 66 93 159) "Zakon o lokalnim porezima čl. 11 st. 3 t. 1: osobni automobili 2 to 5 years of age, EUR by kW",  p11hrRow "car" 5 10 (p11hrCar 27 33 53 80 133) "Zakon o lokalnim porezima čl. 11 st. 3 t. 1: osobni automobili 5 to 10 years of age, EUR by kW",  p11hrRow "motorcycle" (-1) 2 (p11hrMoto 13 27 66 159) "Zakon o lokalnim porezima čl. 11 st. 3 t. 2: motocikli up to 2 years of age",  p11hrRow "motorcycle" 2 5 (p11hrMoto 11 20 53 133) "Zakon o lokalnim porezima čl. 11 st. 3 t. 2: motocikli 2 to 5 years of age",  p11hrRow "motorcycle" 5 10 (p11hrMoto 7 13 40 106) "Zakon o lokalnim porezima čl. 11 st. 3 t. 2: motocikli 5 to 10 years of age"]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Porez na cestovna motorna vozila (pass 11)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p11hrVeh g (firstOnly := true) }]

def absent : List Absent :=
  [{ oecd := .other, why := "none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: real estate transfer tax 4400; taxes and fees on games of chance and winnings 5126 / 5200 (§§ 14, 72); tax on road motor vehicles 5200; special tax on coffee and soft drinks 5128; special tax on motor vehicles 5200 (§ 83)" }]

def notes : List String := ["HR 5200 Porez na cestovna motorna vozila pass 11: consolidated text in force from 1 January 2024 (zakon.hr via the Internet Archive 2025-06-15, `hr/law/zlp_zakonhr_wb20250615.txt`); original NN 115/2016 (`hr/law/nn2016_115_2524_zlp.txt`) (grade B)", "HR 6000 gap pass: not levied (cited, B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(vehicleTaxUnknown "Porez na cestovna motorna vozila" p11hrVeh g).isEmpty then ["5200 Porez na cestovna motorna vozila: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Porez na cestovna motorna vozila" p11hrVeh g).isEmpty then ["5200 Porez na cestovna motorna vozila: a vehicle no rule reaches: quadricycles, vehicles other than cars and motorcycles (grade C)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 porez na cestovna motorna vozila: the age is read in calendar years since first registration (2 / 5 / 10-year boundaries fall in the lower column)"] else [])

#guard p11amt p11hrVeh { kind := "car", fuel := .petrol, engineKw := 85, firstRegYear := 2021 } == 66
#guard p11amt p11hrVeh { kind := "car", fuel := .petrol, engineKw := 55, firstRegYear := 2024 } == 40
#guard p11amt p11hrVeh { kind := "car", fuel := .petrol, engineKw := 56, firstRegYear := 2023 } == 53
#guard p11amt p11hrVeh { kind := "car", fuel := .petrol, engineKw := 140, firstRegYear := 2018 } == 133
#guard p11amt p11hrVeh { kind := "car", fuel := .petrol, engineKw := 140, firstRegYear := 2014 } == 0
#guard p11amt p11hrVeh { kind := "motorcycle", fuel := .petrol, engineKw := 60, firstRegYear := 2022 } == 53

end HrGlobal.Other
