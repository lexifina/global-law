import ItGlobal.Pit
import TaxKernel.Global2

/-!
# IT 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (IRAP (D.Lgs. 446/1997) recorded under CIT; imposta di bollo on financial statements (DPR 642/1972)): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor here: IRAP recorded under CIT (P2); imposta di bollo on documents small


## 5200 Tassa automobilistica regionale (bollo) (pass 11, kernel 2.4.0, grade B)
Source: Regione Lazio, Determinazione n. G16786 dell'11/12/2024 "Tariffario Anno 2025 delle Tasse Automobilistiche della Regione Lazio" and its allegato, regione.lazio.it (`it/law/lazio_dd_g16786.txt`, `it/law/lazio_tariffario2025_g16786.pdf`).
* the tax is based on the engine's maximum power in kW from the registration certificate and on its Euro class: Euro 0 3,30 / 4,95; Euro 1 3,19 / 4,79; Euro 2 3,08 / 4,62; Euro 3 2,97 / 4,46; Euro 4, 5, 6 2,84 / 4,26 EUR per kW up to 100 kW / per kW above (the national L. 296/2006 tariff raised by 10 % under D.Lgs. 504/1992 art. 24)
* minimum 21,02 EUR; amounts are rounded to the cent (the model books whole euros, rounded down, and a 21 EUR minimum)
* exempt: electric cars for five years from first registration, cars from the 30th year after construction; cars running only or also on electricity, methane, LPG or hydrogen pay 2,84 EUR per kW whatever the class
* grade B: the region's official tariff table, read by OCR from the published PDF; the regional law text is not on disk
-/

namespace ItGlobal.Other
open TaxKernel TaxKernel.Global

/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1

/-- euro cents per kW up to 100 kW, and per kW above 100 kW (den 100: whole euros, rounded down) -/
def p11itKw (a b : Int) : QtyTable := { steps := [(0, a), (100, b)], den := 100 }
def p11itBollo : String := "Tassa automobilistica regionale (bollo)"
def p11itRow (lo hi a b : Int) (st : String) : VehicleTax :=
  { name := p11itBollo, kinds := ["car"], fuels := [.petrol, .diesel, .hybrid, .pluginHybrid], «when» := [(.euroClass, lo, hi)],   parts := [(.engineKw, p11itKw a b)], minAmount := 21, level := .local, statute := st }
def p11itVeh : List VehicleTax :=
  [{ name := p11itBollo, kinds := ["car"], «when» := [(.age, 29, VehicleTax.noBound)], level := .local,    statute := "Regione Lazio, tariffario 2025, esenzioni 2): cars from the 30th year after construction are exempt" },  { name := p11itBollo, kinds := ["car"], fuels := [.electric], «when» := [(.age, -1, 4)], level := .local,    statute := "Regione Lazio, tariffario 2025, esenzioni 4) (D.P.R. 39/1953): electric cars, five years from first registration" },  { name := p11itBollo, kinds := ["car"], fuels := [.electric, .lpg, .cng, .hydrogen], parts := [(.engineKw, QtyTable.perUnit 284 100)],    minAmount := 21, level := .local,    statute := "Regione Lazio, tariffario 2025, esenzioni 5): cars running only or also on electricity, methane, LPG or hydrogen, 2,84 EUR per kW whatever the Euro class" },  p11itRow (-1) 0 330 495 "Regione Lazio, tariffario 2025: Euro 0, 3,30 EUR per kW up to 100 kW, 4,95 EUR per kW above",  p11itRow 0 1 319 479 "Regione Lazio, tariffario 2025: Euro 1, 3,19 EUR per kW up to 100 kW, 4,79 EUR per kW above",  p11itRow 1 2 308 462 "Regione Lazio, tariffario 2025: Euro 2, 3,08 EUR per kW up to 100 kW, 4,62 EUR per kW above",  p11itRow 2 3 297 446 "Regione Lazio, tariffario 2025: Euro 3, 2,97 EUR per kW up to 100 kW, 4,46 EUR per kW above",  p11itRow 3 VehicleTax.noBound 284 426 "Regione Lazio, tariffario 2025: Euro 4, 5, 6, 2,84 EUR per kW up to 100 kW, 4,26 EUR per kW above"]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Tassa automobilistica regionale (bollo) (pass 11)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p11itVeh g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["IT 5200 Tassa automobilistica regionale (bollo) pass 11: tariffario 2025, valid from 1 January 2025 (`it/law/lazio_dd_g16786.txt`, `it/law/lazio_tariffario2025_g16786.pdf`; the table is an image, read by OCR: `lazio_tariffario2025_g16786_ocr.txt`) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["6000 Other taxes recorded by the registry: not modelled (grade C: the registry's row (background, not a read text); not modelled)"] else [])
  ++ (if !(vehicleTaxUnknown "Tassa automobilistica regionale (bollo)" p11itVeh g).isEmpty then ["5200 Tassa automobilistica regionale (bollo): a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Tassa automobilistica regionale (bollo)" p11itVeh g).isEmpty then ["5200 Tassa automobilistica regionale (bollo): a vehicle no rule reaches: motorcycles, mopeds, lorries, buses and other classes (other rows of the tariffario) (grade C)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 bollo: the region of Roma (Lazio) is taken; the year of first registration stands for the year of construction (30-year exemption); amounts in whole euros (rounded down)"] else [])
  ++ (if g.vehicles.any (fun v => (v.fuel == .hybrid || v.fuel == .pluginHybrid) && v.firstRegYear == 2022) then ["5200 bollo: a hybrid first registered in 2022 may still be in Lazio's three-year exemption (tariffario, esenzioni 5)): taxed at the Euro-class tariff"] else [])
  ++ (if g.vehicles.any (fun v => 185 < v.engineKw) then ["5200 superbollo (D.L. 98/2011 art. 23 c. 21, 20 EUR per kW above 185 kW) not modelled (grade C)"] else [])

#guard p11amt p11itVeh { kind := "car", fuel := .petrol, engineKw := 110, euroClass := 6, firstRegYear := 2019 } == 326
#guard p11amt p11itVeh { kind := "car", fuel := .diesel, engineKw := 90, euroClass := 3, firstRegYear := 2004 } == 267
#guard p11amt p11itVeh { kind := "car", fuel := .petrol, engineKw := 120, euroClass := 0, firstRegYear := 1998 } == 429
#guard p11amt p11itVeh { kind := "car", fuel := .petrol, engineKw := 100, euroClass := 1, firstRegYear := 1996 } == 319
#guard p11amt p11itVeh { kind := "car", fuel := .petrol, engineKw := 101, euroClass := 2, firstRegYear := 2000 } == 312
#guard p11amt p11itVeh { kind := "car", fuel := .petrol, engineKw := 5, euroClass := 6, firstRegYear := 2020 } == 21
#guard p11amt p11itVeh { kind := "car", fuel := .lpg, engineKw := 110, euroClass := 6, firstRegYear := 2020 } == 312
#guard p11amt p11itVeh { kind := "car", fuel := .electric, engineKw := 150, euroClass := 6, firstRegYear := 2023 } == 0
#guard p11amt p11itVeh { kind := "car", fuel := .electric, engineKw := 150, euroClass := 6, firstRegYear := 2018 } == 426
#guard p11amt p11itVeh { kind := "car", fuel := .petrol, engineKw := 150, euroClass := 0, firstRegYear := 1990 } == 0
#guard p11amt p11itVeh { kind := "car", fuel := .petrol, engineKw := 110, firstRegYear := 2019 } == -1

end ItGlobal.Other
