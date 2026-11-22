import IsGlobal.Pit
import TaxKernel.Global2

/-!
# IS 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes


## 5200 Bifreiðagjald (pass 13, kernel 2.5.0, grade A)
Source: Lög um bifreiðagjald 1988 nr. 39, lagasafn Alþingis, útgáfa 156b, via the Internet Archive capture of 2025-11-30 (the live site answers with a browser check).
* 2. gr.: per period, a vehicle of own weight 3 500 kg or less pays 20 500 kr. for registered CO2 up to 168 g/km on the NEDC (evrópska aksturslotan) and 181 kr. per gram above; with WLTP (samræmda prófunaraðferðin) registration 20 500 kr. up to 204 g and 149 kr. per gram above; without registered CO2 the emission is 0,12 g per kg of own weight plus 50 g
* 2. gr.: above 3 500 kg own weight, 71 160 kr. plus 2,99 kr. per kg above 3 500 kg, at most 111 340 kr. per period
* 3. gr.: two periods a year (1 January-30 June, 1 July-31 December); a vehicle registered in the period pays in proportion to the time registered
* 4. gr. 1. mgr. c: vehicles older than 25 years at the start of the year, counted from the model year, are exempt; 2. mgr.: electric, hydrogen and methane vehicles pay the minimum
* The model books the year: 2 x the period amount (41 000 kr. minimum); convention: CO2 is WLTP for vehicles first registered from 2019, NEDC before; the first-registration year stands for the model year
* Hand check (case is-veh): petrol car of 2021, 230 g/km WLTP: per period 20 500 + 26 x 149 = 24 374, a year 48 748 kr.


## 5200 Bifreiðagjald by days held (pass 17, kernel 2.7.0)
* 3. gr. (útgáfa 156b, as above): gjalddagar 1 January for 1.1-30.6 and 1 July for 1.7-31.12; a newly registered vehicle pays in proportion to its registered time in the period, from the delivery of the plates; on a change of owner the rest of the period passes to the buyer and is refunded to the seller; on deregistration the rest is refunded
* Kernel: `dayPeriods := [("01-01", "06-30"), ("07-01", "12-31")]`: each period half of the year's amount x days held / days of the period; days held from `"heldFrom"`, else the first-registration day for a vehicle registered in 2025, else 1 January, to `"heldTo"`, else 31 December; registered in 2025 without the day: grade C
-/

namespace IsGlobal.Other
open TaxKernel TaxKernel.Global

/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1

/-- Lög nr. 39/1988 um bifreiðagjald 2. gr. (fjárhæðir L. 127/2024, from 1.1.2025), two half-year periods a year -/
def p13isRow (n : String) (fs : List VehicleFuel) (rf rt : Nat) (w : List (VehicleAttr × Int × Int)) (fixed : Int)
    (ps : List (VehicleAttr × QtyTable)) (mx : Int := -1) : VehicleTax :=
  { name := "Bifreiðagjald", kinds := ["car", "van", "truck", "bus"], fuels := fs, regFrom := rf, regTo := rt, when := w,   fixed := fixed, parts := ps, maxAmount := mx, dayPeriods := [("01-01", "06-30"), ("07-01", "12-31")], statute := "Lög nr. 39/1988 um bifreiðagjald " ++ n ++ "; 3. gr. (two periods, by days held)" }
def p13isVeh : List VehicleTax :=
  [ p13isRow "4. gr. 1. mgr. c (older than 25 years: exempt)" [] 0 1999 [] 0 [],   p13isRow "4. gr. 2. mgr. b (electric, hydrogen) and a (methane): the 2. gr. minimum" [.electric, .hydrogen, .cng] 2000 0 [] 41000 [],   p13isRow "2. gr. 1. mgr., 4. málsl.: own weight above 3 500 kg" [] 2000 0 [(.massKg, 3500, -1)] 142320
      [(.massKg, { steps := [(3500, 598)], den := 100 })] 222680,   p13isRow "2. gr. 1. mgr.: WLTP CO2 (samræmda prófunaraðferðin), up to 204 g" [] 2019 0 [] 41000 [(.co2GKm, { steps := [(204, 298)] })],   p13isRow "2. gr. 1. mgr.: NEDC CO2 (evrópska aksturslotan), up to 168 g" [] 2000 2018 [] 41000 [(.co2GKm, { steps := [(168, 362)] })] ]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Bifreiðagjald (pass 13)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p13isVeh g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["IS 5200 Bifreiðagjald pass 13: althingi.is lagasafn útgáfa 156b (Íslensk lög 1. september 2025) via the Internet Archive 2025-11-30 (`is/law/bifreidagjald_l39_1988_utg156b_wb20251130.html`); the amounts are those of L. 127/2024, in force from 1.1.2025; L. 104/2024 (from 1.9.2025) changed only 4. gr. 1. mgr. a (who is exempt) (grade A)", "IS 5200 pass 17 (kernel 2.7.0): bifreiðagjald by days held in each half-year period (lög 39/1988 3. gr.: newly registered vehicles pay in proportion to the registered time; a change of owner or deregistration moves or refunds the rest of the period): VehicleTax.dayPeriods"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["6000 Other taxes: not modelled (grade C: registry row: no other notable tax; no provision read)"] else [])
  ++ (if !(vehicleTaxUnknown "Bifreiðagjald" p13isVeh g).isEmpty then ["5200 Bifreiðagjald: a vehicle lacks an attribute the rate needs, or (registered or acquired in 2025) the day it was registered or acquired: 3. gr. charges each half-year period by the days held (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Bifreiðagjald" p13isVeh g).isEmpty then ["5200 Bifreiðagjald: a vehicle no rule reaches: motorcycles, trailers and vehicles without registered CO2 (the 0,12 g/kg + 50 g rule needs the own weight) (grade C)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 bifreiðagjald: the input's CO2 is read as WLTP for vehicles first registered from 2019 and as NEDC before (the act charges by the registered cycle); the first-registration year stands for the model year in the 25-year exemption"] else [])
  ++ (if g.vehicles.any (fun v => v.fuel == .electric || v.fuel == .pluginHybrid) then ["5200 kílómetragjald (lög 101/2023) on electric and plug-in hybrid cars not modelled: it is charged per km driven, not an input (grade C)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 bifreiðagjald 3. gr.: a vehicle held part of a period pays for the days held: from first registration (the plates' delivery is taken as the first-registration day) or the registered change of owner (\"heldFrom\"), to deregistration or sale (\"heldTo\"); without these the whole year is charged"] else [])

#guard p11amt p13isVeh { kind := "car", fuel := .petrol, co2GKm := 150, firstRegYear := 2021 } == 41000
#guard p11amt p13isVeh { kind := "car", fuel := .petrol, co2GKm := 230, firstRegYear := 2021 } == 48748
#guard p11amt p13isVeh { kind := "car", fuel := .petrol, co2GKm := 204, firstRegYear := 2021 } == 41000
#guard p11amt p13isVeh { kind := "car", fuel := .diesel, co2GKm := 180, firstRegYear := 2015 } == 45344
#guard p11amt p13isVeh { kind := "car", fuel := .diesel, co2GKm := 168, firstRegYear := 2015 } == 41000
#guard p11amt p13isVeh { kind := "car", fuel := .electric, firstRegYear := 2023 } == 41000
#guard p11amt p13isVeh { kind := "car", fuel := .petrol, co2GKm := 300, firstRegYear := 1999 } == 0
#guard p11amt p13isVeh { kind := "truck", fuel := .diesel, massKg := 12000, firstRegYear := 2020 } == 193150
#guard p11amt p13isVeh { kind := "truck", fuel := .diesel, massKg := 20000, firstRegYear := 2020 } == 222680
#guard p11amt p13isVeh { kind := "car", fuel := .petrol, firstRegYear := 2021 } == -1

end IsGlobal.Other
