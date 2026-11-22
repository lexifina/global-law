import ByGlobal.Pit
import TaxKernel.Global2

/-!
# BY 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes


## 5200 Транспортный налог (pass 11, kernel 2.4.0, grade A)
Source: Налоговый кодекс Республики Беларусь, Особенная часть, pravo.by via the Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`).
* ст. 307-2: the object is a vehicle registered with the State Automobile Inspection; not objects: vehicles made no later than 1991, and M1 cars driven only by an electric motor to 31 December 2025
* ст. 307-4: the base is the number of vehicles; ст. 307-5 п. 1, приложение 27: annual rates in roubles by permitted maximum mass
* приложение 27 п. 2.1 (individuals): up to 1,5 t 70, to 1,75 t 92, to 2 t 116, to 2,25 t 138, to 2,5 t 161, to 3 t 183, above 3 t 253; п. 1.1 (organisations): up to 1 t 183, to 2 t 237, to 3 t 289, above 3 t 368
* ст. 307-7 п. 4: a vehicle registered in the year is taxed from the month after registration (the model prorates by months held); п. 11: the high-comfort list multiplies the rate (not modelled)
-/

namespace ByGlobal.Other
open TaxKernel TaxKernel.Global

/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1

def p11byInd : QtyTable := QtyTable.ofCeilings [(1500, 70), (1750, 92), (2000, 116), (2250, 138), (2500, 161), (3000, 183)] 253
def p11byOrg : QtyTable := QtyTable.ofCeilings [(1000, 183), (2000, 237), (3000, 289)] 368
def p11byZero : List VehicleTax :=
  [{ name := "Транспортный налог", kinds := ["car"], fuels := [.electric],    statute := "НК ст. 307-2 п. 2: M1 cars driven only by an electric motor are not an object of the tax to 31 December 2025" },  { name := "Транспортный налог", kinds := ["car"], regTo := 1991,    statute := "НК ст. 307-2 п. 2: vehicles made no later than 1991 are not an object of the tax" }]
def p11byVeh (company : Bool) : List VehicleTax :=
  p11byZero ++ [{ name := "Транспортный налог", kinds := ["car"], parts := [(.massKg, if company then p11byOrg else p11byInd)],   statute := if company then "НК ст. 307-5 п. 1, ст. 307-7 п. 1, приложение 27 п. 1.1: organisation, passenger car by permitted maximum mass (BYN a year)"
               else "НК ст. 307-5 п. 1, ст. 307-7 п. 1, приложение 27 п. 2.1: individual, passenger car by permitted maximum mass (BYN a year)" }]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Транспортный налог (pass 11)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges (p11byVeh (g.entity == .company)) g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["BY 5200 Транспортный налог pass 11: pravo.by via the Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["6000 Other taxes: not modelled (grade C: registry row: no other notable tax; no provision read)"] else [])
  ++ (if !(vehicleTaxUnknown "Транспортный налог" (p11byVeh (g.entity == .company)) g).isEmpty then ["5200 Транспортный налог: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Транспортный налог" (p11byVeh (g.entity == .company)) g).isEmpty then ["5200 Транспортный налог: a vehicle no rule reaches: motorcycles, lorries, buses, trailers (приложение 27 other points) (grade C)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 транспортный налог: massKg is read as the permitted maximum mass (разрешенная максимальная масса); the 50 % / 75 % rates for veterans and disabled persons (ст. 307-5 п. 2, 3) are not applied"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 транспортный налог: a vehicle on the Council of Ministers' high-comfort list (ст. 307-7 п. 11) is taxed at the plain rate (grade C for the increase)"] else [])

#guard p11amt (p11byVeh false) { kind := "car", fuel := .petrol, massKg := 1850, firstRegYear := 2018 } == 116
#guard p11amt (p11byVeh false) { kind := "car", fuel := .petrol, massKg := 1500, firstRegYear := 2018 } == 70
#guard p11amt (p11byVeh false) { kind := "car", fuel := .diesel, massKg := 3100, firstRegYear := 2018 } == 253
#guard p11amt (p11byVeh true) { kind := "car", fuel := .diesel, massKg := 1850, firstRegYear := 2018 } == 237
#guard p11amt (p11byVeh true) { kind := "car", fuel := .diesel, massKg := 3100, firstRegYear := 2018 } == 368
#guard p11amt (p11byVeh false) { kind := "car", fuel := .electric, massKg := 2100, firstRegYear := 2023 } == 0
#guard p11amt (p11byVeh false) { kind := "car", fuel := .petrol, massKg := 1300, firstRegYear := 1990 } == 0

end ByGlobal.Other
