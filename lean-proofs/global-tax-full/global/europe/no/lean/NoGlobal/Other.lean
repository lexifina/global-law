import NoGlobal.Pit
import TaxKernel.Global2

/-!
# NO 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes


## 5200 Trafikkforsikringsavgift (pass 11, kernel 2.4.0, grade A)
Source: Stortingsvedtak om avgift på trafikkforsikringer for 2025, Lovdata LTI/forskrift/2024-12-13-3212 (`no/law/stv_tfa2025.txt`).
* § 1: the tax is due on the compulsory motor liability insurance of Norwegian-registered vehicles; § 2: kroner per day by group and by the date of the contract's main renewal (before 1 March 2024 / 1 March 2024 to February 2025 / from 1 March 2025)
* group a (cars, vans and other vehicles listed): 8,38 / 7,60 / 6,38; group b (diesel without a factory particle filter): 9,84 / 9,11 / 7,93; group d (motorcycles): 6,10 / 5,23 / 5,39; group e (incl. vehicles of 30 years or more): 1,42 / 0,37 / 0,38; group f (electricity only, incl. fuel cells): 8,38 / 8,70 / 8,96
* the model takes a contract renewed on 1 January 2025 (the middle column for the whole year, x 365 days)


## 5200 Engangsavgift på motorvogner (pass 11, kernel 2.4.0, grade A)
Source: Stortingsvedtak om engangsavgift på motorvogner mv. for 2025, Lovdata LTI/forskrift/2024-12-13-3211 (`no/law/stv_engangs2025.txt`).
* § 2: for passenger cars (group a) 12,44 kr per kg of the egenvekt above 500 kg, in addition to § 3
* § 3: for piston combustion engines also egenvekt bands, NOx (85,88 kr per mg/km) and CO2 bands with deductions below 70 g/km: not modelled (NOx is not an input attribute)
* § 5: vrakpantavgift 2 400 kr per car of group a (booked with the registration)

* **6000 not levied (cited, gap pass, grade B)**: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVNOR v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/NOR.csv`, SHA256SUMS; general government S13; 2025 not yet published): heading 6000 total 0 in 2021-2024: the OECD books no revenue under heading 6000 in any of 2021-2024 (guide § 85: taxes on bases other than those of 1000-5000) (OECD Revenue Statistics 2021-2024 (2025 not yet published); no 6000 tax known in the national law read)
-/

namespace NoGlobal.Other
open TaxKernel TaxKernel.Global

/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1

/-- daily rates in øre x 365 (multiplierBp 100: kroner) -/
def p11noT (ks : List String) (fs : List VehicleFuel) (w : List (VehicleAttr × Int × Int)) (perDay : Int) (st : String) : VehicleTax :=
  { name := "Trafikkforsikringsavgift", kinds := ks, fuels := fs, «when» := w, fixed := perDay * 365, multiplierBp := 100, statute := st }
def p11noTfa : List VehicleTax :=
  [p11noT ["car", "van", "motorcycle"] [] [(.age, 29, VehicleTax.noBound)] 37 "Stortingsvedtak om avgift på trafikkforsikringer 2025 § 2, avgiftsgruppe e nr. 10 (30 years or older): 0,37 kr per day",  p11noT ["car", "van"] [.electric, .hydrogen] [] 870 "Stortingsvedtak om avgift på trafikkforsikringer 2025 § 2, avgiftsgruppe f (electricity only, incl. fuel cells): 8,70 kr per day (contract with hovedforfall from 1 March 2024 to February 2025)",  p11noT ["car", "van"] [.petrol, .diesel, .hybrid, .pluginHybrid, .lpg, .cng, .other] [] 760 "Stortingsvedtak om avgift på trafikkforsikringer 2025 § 2, avgiftsgruppe a: 7,60 kr per day (contract with hovedforfall from 1 March 2024 to February 2025)",  p11noT ["motorcycle"] [] [] 523 "Stortingsvedtak om avgift på trafikkforsikringer 2025 § 2, avgiftsgruppe d: 5,23 kr per day (contract with hovedforfall from 1 March 2024 to February 2025)"]
/-- engangsavgift § 2: 12,44 kr per kg of egenvekt above 500 kg (den 100: kroner); § 5: vrakpantavgift 2 400 kr -/
def p11noEng : List VehicleTax :=
  [{ name := "Engangsavgift på motorvogner", kinds := ["car"], fuels := [.electric, .hydrogen], occasion := .registration, fixed := 2400,    parts := [(.massKg, { steps := [(500, 1244)], den := 100 })],    statute := "Stortingsvedtak om engangsavgift på motorvogner mv. 2025 § 2 (12,44 kr per kg of egenvekt above 500 kg; § 3 applies only to piston combustion engines), § 5 (vrakpantavgift 2 400 kr)" }]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Trafikkforsikringsavgift (pass 11)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p11noTfa g (firstOnly := true) },
   { name := "5200 Engangsavgift på motorvogner (pass 11)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p11noEng g (firstOnly := true) }]

def absent : List Absent :=
  [{ oecd := .other, why := "the OECD books no revenue under heading 6000 in any of 2021-2024 (guide § 85: taxes on bases other than those of 1000-5000)" }]

def notes : List String := ["NO 5200 Trafikkforsikringsavgift pass 11: Lovdata (`no/law/stv_tfa2025.txt`) (grade A)", "NO 5200 Engangsavgift på motorvogner pass 11: Lovdata (`no/law/stv_engangs2025.txt`) (grade A)", "NO 6000 gap pass: not levied (cited, B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(vehicleTaxUnknown "Trafikkforsikringsavgift" p11noTfa g).isEmpty then ["5200 Trafikkforsikringsavgift: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Trafikkforsikringsavgift" p11noTfa g).isEmpty then ["5200 Trafikkforsikringsavgift: a vehicle no rule reaches: tractors, mopeds, motor equipment and other groups (grade C)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 trafikkforsikringsavgift: the insurance contract is taken as renewed on 1 January 2025 (column 'fra 1. mars 2024 t.o.m. februar 2025' all year); a renewal from March 2025 gives the lower last column (grade C for the split)"] else [])
  ++ (if g.vehicles.any (fun v => v.fuel == .diesel) then ["5200 trafikkforsikringsavgift: a diesel vehicle is taken as having a factory-fitted particle filter (group a, not b)"] else [])
  ++ (if !(vehicleTaxUnknown "Engangsavgift på motorvogner" p11noEng g).isEmpty then ["5200 Engangsavgift på motorvogner: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg && !(p11noEng.any (·.selects g.year v))) then ["5200 Engangsavgift på motorvogner: a vehicle no rule reaches: new cars with a combustion engine (§ 3 needs NOx), other groups (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg) then ["5200 engangsavgift: massKg is read as the egenvekt; the bruksfradrag for a used import (§ 4) is not applied"] else [])

#guard p11amt p11noTfa { kind := "car", fuel := .petrol, firstRegYear := 2020 } == 2774
#guard p11amt p11noTfa { kind := "car", fuel := .electric, firstRegYear := 2023 } == 3175
#guard p11amt p11noTfa { kind := "car", fuel := .petrol, firstRegYear := 1990 } == 135
#guard p11amt p11noTfa { kind := "motorcycle", fuel := .petrol, firstRegYear := 2015 } == 1908
#guard p11amt p11noEng { kind := "car", fuel := .electric, massKg := 2100, firstRegYear := 2025, newReg := true } == 22304
#guard p11amt p11noEng { kind := "car", fuel := .petrol, massKg := 1400, firstRegYear := 2025, newReg := true } == -1

end NoGlobal.Other
