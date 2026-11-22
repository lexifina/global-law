import EsGlobal.Pit
import TaxKernel.Global2

/-!
# ES 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (Impuesto sobre Actividades Económicas (TRLRHL arts. 78-91); temporary bank and energy levies (Ley 38/2022)): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: model for companies: IAE (TRLRHL arts. 78-91), exempt below EUR 1 m turnover; temporary bank and energy levies sector-only (minor)


## 5200 Impuesto especial sobre determinados medios de transporte (pass 10, kernel 2.4.0, grade A)
Source: Ley 38/1992, de 28 de diciembre, de Impuestos Especiales, BOE-A-1992-28741, texto consolidado (`es/law/iedmt_ley38_1992.txt`); TRLRHL, BOE-A-2004-4214 (`es/law/trlrhl.txt`).
* art. 69 a): for new means of transport the base is the VAT base of the acquisition
* art. 70.1: epígrafe 1.º a) CO2 not above 120 g/km, b) a single motor that is not of internal combustion; 2.º above 120 and below 160; 3.º from 160 to below 200; 4.º a) 200 or more, b) emissions required but not proven
* art. 70.2 b) (where the autonomous community has approved no rates), Península e Illes Balears: 0,00 / 4,75 / 9,75 / 14,75 por 100 (Canarias 0 / 3,75 / 8,75 / 13,75)
* TRLRHL art. 95.1 A) turismos: below 8 caballos fiscales 12,62 EUR, 8-11,99 34,08, 12-15,99 71,94, 16-19,99 89,61, 20 and more 112,00; art. 95.4: municipalities may raise the tariff by a coefficient up to 2


## 5200 Impuesto sobre vehículos de tracción mecánica (pass 10, kernel 2.4.0, grade A)
Source: Texto refundido de la Ley Reguladora de las Haciendas Locales, BOE-A-2004-4214 (`es/law/trlrhl.txt`).
* the IVTM is booked at the art. 95.1 tariff (the statutory minimum); the reference municipality's coefficient (art. 95.4, up to 2) and bonificaciones (art. 95.6) are not read
-/

namespace EsGlobal.Other
open TaxKernel TaxKernel.Global

def p10esIedmtR (lo hi bp : Int) (st : String) : VehicleTax :=
  { name := "Impuesto especial sobre determinados medios de transporte", kinds := ["car"], occasion := .registration,   when := [(.co2GKm, lo, hi)], parts := [(.value, QtyTable.perUnit bp 10000)], statute := st }
/-- Ley 38/1992 art. 69 a), 70 (Península e Illes Balears, no autonomous rates): first definitive registration in Spain -/
def p10esIedmt : List VehicleTax :=
  [{ name := "Impuesto especial sobre determinados medios de transporte", kinds := ["car"], occasion := .registration,    fuels := [.electric, .hydrogen], statute := "Ley 38/1992 art. 70.1 epígrafe 1.º b), 70.2 b): a single motor that is not of internal combustion, 0 por 100" },  { name := "Impuesto especial sobre determinados medios de transporte", kinds := ["car"], occasion := .registration,    when := [(.co2GKm, -1, 120)], statute := "Ley 38/1992 art. 70.1 epígrafe 1.º a), 70.2 b): CO2 not above 120 g/km, 0 por 100" },  p10esIedmtR 120 159 475 "Ley 38/1992 art. 69 a), 70.1 epígrafe 2.º, 70.2 b): CO2 above 120 and below 160 g/km, 4,75 por 100",  p10esIedmtR 159 199 975 "Ley 38/1992 art. 69 a), 70.1 epígrafe 3.º, 70.2 b): CO2 from 160 to below 200 g/km, 9,75 por 100",  p10esIedmtR 199 1000000 1475 "Ley 38/1992 art. 69 a), 70.1 epígrafe 4.º a), 70.2 b): CO2 of 200 g/km or more, 14,75 por 100"]
/-- TRLRHL art. 95.1 A) turismos, in cents, by caballos fiscales (whole CVF): below 8, 8-11,99, 12-15,99, 16-19,99, 20 and more -/
def p10esIvtmT : QtyTable := QtyTable.ofCeilings [(7, 1262), (11, 3408), (15, 7194), (19, 8961)] 11200
def p10esIvtm : List VehicleTax :=
  [{ name := "Impuesto sobre vehículos de tracción mecánica", kinds := ["car"], parts := [(.fiscalHp, p10esIvtmT)],    multiplierBp := 100, level := .local,    statute := "TRLRHL (RDLeg. 2/2004) art. 95.1 A): cuadro de tarifas, turismos (without a municipal coefficient, art. 95.4)" }]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Impuesto especial sobre determinados medios de transporte (pass 10)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p10esIedmt g (firstOnly := true) },
   { name := "5200 Impuesto sobre vehículos de tracción mecánica (pass 10)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p10esIvtm g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["ES 5200 Impuesto especial sobre determinados medios de transporte pass 10: BOE texto consolidado, fetched 2026-11-21 (`es/law/iedmt_ley38_1992.txt`) (grade A)", "ES 5200 Impuesto sobre vehículos de tracción mecánica pass 10: BOE texto consolidado, fetched 2026-11-21 (`es/law/trlrhl.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["6000 Other taxes recorded by the registry: not modelled (grade C: the registry's row (background, not a read text); not modelled)"] else [])
  ++ (if !(vehicleTaxUnknown "Impuesto especial sobre determinados medios de transporte" p10esIedmt g).isEmpty then ["5200 Impuesto especial sobre determinados medios de transporte: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg && !(p10esIedmt.any (·.selects g.year v))) then ["5200 Impuesto especial sobre determinados medios de transporte: a vehicle no rule reaches: cars without CO2 (epígrafe 4.º b) applies only where the measurement is required and not proven), motorcycles, other vehicles (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg) then ["5200 IEDMT: the vehicle's value is taken as the VAT base of its acquisition (art. 69 a)); a used car first registered in Spain (art. 69 b), market value) is not distinguished; Península rates (no Canarias, no autonomous rates)"] else [])
  ++ (if !(vehicleTaxUnknown "Impuesto sobre vehículos de tracción mecánica" p10esIvtm g).isEmpty then ["5200 Impuesto sobre vehículos de tracción mecánica: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Impuesto sobre vehículos de tracción mecánica" p10esIvtm g).isEmpty then ["5200 Impuesto sobre vehículos de tracción mecánica: a vehicle no rule reaches: vehicles other than turismos (autobuses, camiones, tractores, remolques, ciclomotores y motocicletas) (grade C)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 IVTM: the municipal coefficient (TRLRHL art. 95.4) and bonificaciones (art. 95.6) are not applied: the art. 95.1 tariff is booked (grade C for the municipal part)"] else [])
  ++ (if g.vehicles.any (fun v => v.months < 12) then ["5200 IVTM: part-year prorating is by quarters (art. 96.3), the model prorates by months"] else [])

#guard (p10esIedmtR 120 159 475 "").amount 2025 { kind := "car", co2GKm := 140, value := 30000, firstRegYear := 2025 } == 1425
#guard ((p10esIedmt.filter (·.computes 2025 { kind := "car", co2GKm := 120, value := 30000, fuel := .petrol, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := "car", co2GKm := 120, value := 30000, fuel := .petrol, firstRegYear := 2025 } == 0
#guard ((p10esIedmt.filter (·.computes 2025 { kind := "car", co2GKm := 160, value := 30000, fuel := .petrol, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := "car", co2GKm := 160, value := 30000, fuel := .petrol, firstRegYear := 2025 } == 2925
#guard ((p10esIedmt.filter (·.computes 2025 { kind := "car", co2GKm := 200, value := 30000, fuel := .diesel, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := "car", co2GKm := 200, value := 30000, fuel := .diesel, firstRegYear := 2025 } == 4425
#guard (p10esIedmt.filter (·.computes 2025 { kind := "car", co2GKm := 150, value := 30000, fuel := .petrol, firstRegYear := 2020 })).isEmpty
#guard p10esIvtmT.amount 7 == 1262
#guard p10esIvtmT.amount 11 == 3408
#guard p10esIvtmT.amount 12 == 7194
#guard p10esIvtmT.amount 20 == 11200
#guard (p10esIvtm.head!).amount 2025 { kind := "car", fiscalHp := 11, fuel := .petrol, firstRegYear := 2019 } == 34

end EsGlobal.Other
