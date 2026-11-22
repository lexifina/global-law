import UaGlobal.Pit
import TaxKernel.Global2

/-!
# UA 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes


## 5200 Транспортний податок (pass 11, kernel 2.4.0, grade A)
Source: Податковий кодекс України, zakon.rada.gov.ua via the Internet Archive 2025-06-20 (`ua/law/ptk_wb20250620.txt`); Закон України № 4059-IX "Про Державний бюджет України на 2025 рік" via the Internet Archive 2025-05-31 (`ua/law/budget2025_4059.txt`).
* п. 267.2.1: the object is a car of which no more than five years (inclusive) have passed since the year of manufacture and whose average market value exceeds 375 minimum wages set by law on 1 January of the year
* budget law 2025 ст. 8: minimum wage from 1 January 2025, 8 000 UAH a month: threshold 3 000 000 UAH
* п. 267.4: 25 000 UAH a year for each such car; п. 267.6.2: a car acquired in the year is taxed from the month of acquisition (the model prorates by months held)
-/

namespace UaGlobal.Other
open TaxKernel TaxKernel.Global

/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1

def p11uaVeh : List VehicleTax :=
  [{ name := "Транспортний податок", kinds := ["car"], «when» := [(.age, 5, VehicleTax.noBound)], level := .local,    statute := "ПКУ п. 267.2.1: only cars of which no more than five years have passed since the year of manufacture are taxable" },  { name := "Транспортний податок", kinds := ["car"], «when» := [(.value, -1, 3000000)], level := .local,    statute := "ПКУ п. 267.2.1: only cars whose average market value exceeds 375 minimum wages (375 x 8 000 = 3 000 000 UAH on 1 January 2025) are taxable" },  { name := "Транспортний податок", kinds := ["car"], «when» := [(.age, -1, 5), (.value, 3000000, VehicleTax.noBound)], fixed := 25000, level := .local,    statute := "ПКУ п. 267.2.1, 267.4: 25 000 UAH a year for each car of at most five years with an average market value above 375 minimum wages" }]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Транспортний податок (pass 11)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p11uaVeh g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["UA 5200 Транспортний податок pass 11: ПКУ via the Internet Archive 2025-06-20 (`ua/law/ptk_wb20250620.txt`); budget law via the Internet Archive 2025-05-31 (`ua/law/budget2025_4059.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["6000 Other taxes: not modelled (grade C: registry row: no other notable tax; no provision read)"] else [])
  ++ (if !(vehicleTaxUnknown "Транспортний податок" p11uaVeh g).isEmpty then ["5200 Транспортний податок: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Транспортний податок" p11uaVeh g).isEmpty then ["5200 Транспортний податок: a vehicle no rule reaches: vehicles other than passenger cars (not objects of the tax) (grade C)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 транспортний податок: the vehicle's value stands for the ministry's average market value and its first-registration year for the year of manufacture"] else [])

#guard p11amt p11uaVeh { kind := "car", fuel := .petrol, value := 3500000, firstRegYear := 2022 } == 25000
#guard p11amt p11uaVeh { kind := "car", fuel := .petrol, value := 3500000, firstRegYear := 2020 } == 25000
#guard p11amt p11uaVeh { kind := "car", fuel := .petrol, value := 3500000, firstRegYear := 2019 } == 0
#guard p11amt p11uaVeh { kind := "car", fuel := .petrol, value := 3000000, firstRegYear := 2023 } == 0
#guard p11amt p11uaVeh { kind := "car", fuel := .petrol, value := 3000001, firstRegYear := 2023 } == 25000

end UaGlobal.Other
