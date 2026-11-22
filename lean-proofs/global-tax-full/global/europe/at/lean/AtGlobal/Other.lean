import AtGlobal.Pit
import TaxKernel.Global2

/-!
# AT 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (Kommunalsteuer and Dienstgeberbeitrag recorded under payroll; Stabilitätsabgabe (banks)): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor here: Kommunalsteuer and Dienstgeberbeitrag are payroll (P4); Stabilitätsabgabe is banks only


## 5200 Motorbezogene Versicherungssteuer (pass 10, kernel 2.4.0, grade A)
Source: Versicherungssteuergesetz 1953, RIS Bundesrecht konsolidiert, Fassung vom 01.07.2025 (`at/law/versstg_2025-07-01.txt`).
* § 6 (1): the motorbezogene Versicherungssteuer is due "für jeden Monat des Bestehens eines Versicherungsvertrages" of the motor liability insurance; the model books twelve months
* Z 2 lit. a (electric): per kW of the power less 45 kW, 0,25 EUR for the first 35, 0,35 for the next 25, 0,45 above, at least 10 kW; plus per kg of the own weight less 900 kg, 0,015 / 0,030 / 0,045 EUR for 500 / 700 / above, at least 200 kg
* Z 2 lit. b (first registered before 1 October 2020): per kW of the power less 24 kW, 0,62 EUR for the first 66, 0,66 for the next 20, 0,75 above, at least 6,20 EUR
* Z 2 lit. c (first registered after 30 September 2020, WLTP): 0,72 EUR per kW of the power less a deduction and 0,72 EUR per g CO2/km less a deduction, at least 5 kW and 5 g; deductions by year of first registration: kW 65 (2020) to 60 (2025), CO2 115 to 100 (3 g a year), weighted CO2 of plug-in hybrids 17 to 12
* § 6 (3): +6 / 8 / 10 % for half-yearly, quarterly or monthly payment of the premium: not applied (annual payment)


## 5200 Normverbrauchsabgabe (pass 10, kernel 2.4.0, grade A)
Source: Normverbrauchsabgabegesetz, RIS Bundesrecht konsolidiert, Fassung vom 01.07.2025 (`at/law/novag_2025-07-01.txt`).
* § 6 (2): rate in per cent = (CO2 g/km − 112) / 5, rounded to whole per cent, at most 50 %; above 200 g/km 50 EUR per g; less 350 EUR; no credit
* § 6 (7): from 1 January 2022, for the last time on 1 January 2024, each year the CO2 deduction falls by 5, the malus threshold by 15, the malus amount rises by 10 and the top rate by 10 points (2024: 97 g/km, 155 g/km, 80 EUR, 80 %); the yearly fall of the CO2 deduction goes on from 1 January 2025 by 3: for 2025, 94 g/km, 155 g/km, 80 EUR, 80 % (pass 12: the model had 97, FT reviewer 6 R4-8)
* § 6 (7) last sentence: a vehicle bought by an irrevocable written contract before 1 December 2024 and delivered before 1 April 2025 may keep the 2024 values (not modelled: the contract date is not an input)
* § 6 (4): combined WLTP CO2 (weighted combined for plug-in hybrids)

* FT review (sixth pass): electric cars owe the motorbezogene Versicherungssteuer from 1 April 2025 only (BGBl. I Nr. 7/2025, § 12 (1) Z 35); 9/12 of the annual amount for 2025.


## 6000 Kirchenbeitrag (katholische, evangelische, altkatholische Kirche): not a tax (OECD guide § 6) (gap pass, grade C)
Source: Gesetz über die Erhebung von Kirchenbeiträgen im Lande Österreich, GBlÖ Nr. 543/1939, § 1 (the churches are entitled to levy Kirchenbeiträge under contribution rules they issue) and § 3 (1)-(2) (the contributions are fixed and collected by the churches; civil courts; state approval), RIS open data NOR40006928, NOR40006930 (Gesetzesnummer 10009211, fetched 2026-11-22, `at/law/kibg_1939_p1.xml`, `at/law/kibg_1939_p3.xml`).
* OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 6: church taxes are included only in countries where the church forms part of general government; levies paid to non-government bodies are excluded even where compulsory, unless the government is more than an agent
* not a tax (OECD guide § 6): the churches fix and collect the contribution themselves; claims are enforced in the civil courts; the state only approves the contribution rules
-/

namespace AtGlobal.Other
open TaxKernel TaxKernel.Global

/-- VersStG 1953 § 6 (1) Z 2 lit. c: 0,72 EUR a month per unit above a deduction, at least 5 units: a year in cents -/
def p10atMin5 (d : Int) : QtyTable := { bands := [(0, 4320)], steps := [(d + 5, 864)] }
def p10atC (fs : List VehicleFuel) (y : Nat) (kw co2 : QtyTable) (st : String) : VehicleTax :=
  { name := "Motorbezogene Versicherungssteuer", kinds := ["car"], fuels := fs, regFrom := y, regTo := y,   parts := [(.engineKw, kw), (.co2GKm, co2)], multiplierBp := 100, statute := st }
/-- § 6 (1) Z 2 lit. a: electric, per kW of the power less 45 kW (at least 10): 0,25 / 0,35 / 0,45 EUR; per kg of the
own weight less 900 kg (at least 200): 0,015 / 0,030 / 0,045 EUR, a month (a year in cents) -/
def p10atEvKw : QtyTable := { bands := [(0, 3000)], steps := [(55, 300), (80, 420), (105, 540)] }
def p10atEvKg : QtyTable := { bands := [(0, 3600)], steps := [(1100, 18), (1400, 36), (2100, 54)] }
/-- § 6 (1) Z 2 lit. b: first registered before 1 October 2020, per kW of the power less 24 kW: 0,62 (66 kW) / 0,66
(20 kW) / 0,75 EUR a month, at least 6,20 EUR (a year in cents) -/
def p10atOld : QtyTable := { steps := [(24, 744), (90, 792), (110, 900)] }
def p10atVeh : List VehicleTax :=
  [{ name := "Motorbezogene Versicherungssteuer", kinds := ["car"], fuels := [.electric], parts := [(.engineKw, p10atEvKw), (.massKg, p10atEvKg)],    multiplierBp := 75, statute := "VersStG 1953 § 6 (1) Z 2 lit. a: rein elektrischer Antrieb, kW and own weight; due from 1 April 2025 only (§ 12 (1) Z 35, BGBl. I Nr. 7/2025; before, § 4 (3) Z 6 exempt): 9/12 of the year" },  p10atC [.petrol, .diesel, .hybrid, .lpg, .cng, .other] 2021 (p10atMin5 64) (p10atMin5 112) "VersStG 1953 § 6 (1) Z 2 lit. c sublit. bb, cc: first registration 2021: 0,72 EUR per kW above 64 kW and per g CO2/km above 112 g (at least 5 each), a month",  p10atC [.pluginHybrid] 2021 (p10atMin5 64) (p10atMin5 16) "VersStG 1953 § 6 (1) Z 2 lit. c sublit. aa, cc: first registration 2021: 0,72 EUR per kW above 64 kW and per g weighted CO2/km above 16 g (at least 5 each), a month",  p10atC [.petrol, .diesel, .hybrid, .lpg, .cng, .other] 2022 (p10atMin5 63) (p10atMin5 109) "VersStG 1953 § 6 (1) Z 2 lit. c sublit. bb, cc: first registration 2022: 0,72 EUR per kW above 63 kW and per g CO2/km above 109 g (at least 5 each), a month",  p10atC [.pluginHybrid] 2022 (p10atMin5 63) (p10atMin5 15) "VersStG 1953 § 6 (1) Z 2 lit. c sublit. aa, cc: first registration 2022: 0,72 EUR per kW above 63 kW and per g weighted CO2/km above 15 g (at least 5 each), a month",  p10atC [.petrol, .diesel, .hybrid, .lpg, .cng, .other] 2023 (p10atMin5 62) (p10atMin5 106) "VersStG 1953 § 6 (1) Z 2 lit. c sublit. bb, cc: first registration 2023: 0,72 EUR per kW above 62 kW and per g CO2/km above 106 g (at least 5 each), a month",  p10atC [.pluginHybrid] 2023 (p10atMin5 62) (p10atMin5 14) "VersStG 1953 § 6 (1) Z 2 lit. c sublit. aa, cc: first registration 2023: 0,72 EUR per kW above 62 kW and per g weighted CO2/km above 14 g (at least 5 each), a month",  p10atC [.petrol, .diesel, .hybrid, .lpg, .cng, .other] 2024 (p10atMin5 61) (p10atMin5 103) "VersStG 1953 § 6 (1) Z 2 lit. c sublit. bb, cc: first registration 2024: 0,72 EUR per kW above 61 kW and per g CO2/km above 103 g (at least 5 each), a month",  p10atC [.pluginHybrid] 2024 (p10atMin5 61) (p10atMin5 13) "VersStG 1953 § 6 (1) Z 2 lit. c sublit. aa, cc: first registration 2024: 0,72 EUR per kW above 61 kW and per g weighted CO2/km above 13 g (at least 5 each), a month",  p10atC [.petrol, .diesel, .hybrid, .lpg, .cng, .other] 2025 (p10atMin5 60) (p10atMin5 100) "VersStG 1953 § 6 (1) Z 2 lit. c sublit. bb, cc: first registration 2025: 0,72 EUR per kW above 60 kW and per g CO2/km above 100 g (at least 5 each), a month",  p10atC [.pluginHybrid] 2025 (p10atMin5 60) (p10atMin5 12) "VersStG 1953 § 6 (1) Z 2 lit. c sublit. aa, cc: first registration 2025: 0,72 EUR per kW above 60 kW and per g weighted CO2/km above 12 g (at least 5 each), a month",  { name := "Motorbezogene Versicherungssteuer", kinds := ["car"], fuels := [.petrol, .diesel, .hybrid, .pluginHybrid, .lpg, .cng, .other],    regTo := 2020, parts := [(.engineKw, p10atOld)], multiplierBp := 100, minAmount := 74,    statute := "VersStG 1953 § 6 (1) Z 2 lit. b: first registered before 1 October 2020, kW less 24, at least 6,20 EUR a month" }]
/-- NoVAG 1991 § 6 (2), (7) for 2025: rate (CO2 − 94) / 5 per cent, rounded to whole per cent (r % for CO2 from 92 + 5r
to 96 + 5r g/km; § 6 (7): the CO2 deduction falls by 3 from 1 January 2025, 97 − 3 = 94), at most 80 %; plus 80 EUR per g/km above 155; less 350 EUR; never below 0 -/
def p10atNovaR (r : Int) : VehicleTax :=
  { name := "Normverbrauchsabgabe", kinds := ["car"], occasion := .registration,   when := [(.co2GKm, 91 + 5 * r, if r == 80 then 1000000 else 96 + 5 * r)],   fixed := -350, parts := [(.value, QtyTable.perUnit r 100), (.co2GKm, { steps := [(155, 80)] })],   statute := s!"NoVAG 1991 § 6 (2), (7): {r} % of the net price, malus 80 EUR per g/km above 155, less 350 EUR" }
def p10atNova : List VehicleTax :=
  { name := "Normverbrauchsabgabe", kinds := ["car"], occasion := .registration, when := [(.co2GKm, -1, 96)],    fixed := -350, parts := [(.co2GKm, { steps := [(155, 80)] })],    statute := "NoVAG 1991 § 6 (2), (7): CO2 up to 96 g/km, 0 %; less 350 EUR; never below 0" }
  :: (List.range 80).map (fun (i : Nat) => p10atNovaR ((i : Int) + 1))

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Motorbezogene Versicherungssteuer (pass 10)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p10atVeh g (firstOnly := true) },
   { name := "5200 Normverbrauchsabgabe (pass 10)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p10atNova g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["AT 5200 Motorbezogene Versicherungssteuer pass 10: RIS, Fassung vom 1. Juli 2025 (`at/law/versstg_2025-07-01.txt`) (grade A)", "AT 5200 Normverbrauchsabgabe pass 10: RIS, Fassung vom 1. Juli 2025 (`at/law/novag_2025-07-01.txt`); § 6 (7) identical in the Fassung vom 31.12.2025 (`at/law/novag_2025-12-31.txt`) (grade A)", "AT gap pass: Kirchenbeitrag (katholische, evangelische, altkatholische Kirche)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["6000 Other taxes recorded by the registry: not modelled (grade C: the registry's row (background, not a read text); not modelled)"] else [])
  ++ (if !(vehicleTaxUnknown "Motorbezogene Versicherungssteuer" p10atVeh g).isEmpty then ["5200 Motorbezogene Versicherungssteuer: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Motorbezogene Versicherungssteuer" p10atVeh g).isEmpty then ["5200 Motorbezogene Versicherungssteuer: a vehicle no rule reaches: cars first registered after 2025, cars of 2021-2025 without WLTP CO2 (lit. d), motorcycles, vans, lorries (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.firstRegYear == 2020) then ["5200 motorbezogene Versicherungssteuer: a car first registered in 2020 is taken under lit. b (before 1 October 2020)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 motorbezogene Versicherungssteuer: annual payment of the premium assumed (§ 6 (3) surcharges of 6-10 % not applied); the 6,20 EUR monthly minimum is booked as 74 EUR a year"] else [])
  ++ (if !(vehicleTaxUnknown "Normverbrauchsabgabe" p10atNova g).isEmpty then ["5200 Normverbrauchsabgabe: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg && !(p10atNova.any (·.selects g.year v))) then ["5200 Normverbrauchsabgabe: a vehicle no rule reaches: cars without CO2 (§ 6 (6) cylinder-capacity rule not modelled), motorcycles, vans (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg) then ["5200 NoVA: the vehicle's value is taken as the net price (Bemessungsgrundlage, NoVAG § 5); a used car imported and first registered in Austria is taxed on the same table"] else [])
  ++ (if g.vehicles.any (fun v => v.fuel == .electric) then ["5200 motorbezogene Versicherungssteuer: an electric car is taxed from 1 April 2025 only (VersStG § 12 (1) Z 35; exempt before under § 4 (3) Z 6): 9/12 of the annual § 6 (1) Z 2 lit. a amount"] else [])

#guard (p10atMin5 60).amount 110 == 43200
#guard (p10atMin5 100).amount 130 == 25920
#guard (p10atMin5 100).amount 90 == 4320
#guard p10atEvKw.amount 80 == 10500
#guard p10atEvKg.amount 2100 == 34200
#guard p10atEvKg.amount 1000 == 3600
#guard p10atOld.amount 100 == 57024
#guard ((p10atVeh.filter (·.computes 2025 { kind := "car", engineKw := 110, co2GKm := 130, fuel := .petrol, firstRegYear := 2025 })).head!).amount 2025 { kind := "car", engineKw := 110, co2GKm := 130, fuel := .petrol, firstRegYear := 2025 } == 691
#guard ((p10atVeh.filter (·.computes 2025 { kind := "car", engineKw := 85, fuel := .diesel, firstRegYear := 2015 })).head!).amount 2025 { kind := "car", engineKw := 85, fuel := .diesel, firstRegYear := 2015 } == 453
#guard (p10atNovaR 7).amount 2025 { kind := "car", co2GKm := 130, value := 30000, firstRegYear := 2025, newReg := true } == 1750
#guard (p10atNovaR 13).amount 2025 { kind := "car", co2GKm := 160, value := 30000, firstRegYear := 2025, newReg := true } == 3950
#guard ((p10atNova.filter (·.computes 2025 { kind := "car", co2GKm := 130, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := "car", co2GKm := 130, value := 30000, firstRegYear := 2025, newReg := true } == 1750
#guard ((p10atNova.filter (·.computes 2025 { kind := "car", co2GKm := 99, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := "car", co2GKm := 99, value := 30000, firstRegYear := 2025, newReg := true } == 0
#guard ((p10atNova.filter (·.computes 2025 { kind := "car", co2GKm := 100, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := "car", co2GKm := 100, value := 30000, firstRegYear := 2025, newReg := true } == 0
#guard ((p10atNova.filter (·.computes 2025 { kind := "car", co2GKm := 105, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := "car", co2GKm := 105, value := 30000, firstRegYear := 2025, newReg := true } == 250
#guard ((p10atNova.filter (·.computes 2025 { kind := "car", co2GKm := 96, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := "car", co2GKm := 96, value := 30000, firstRegYear := 2025, newReg := true } == 0
#guard ((p10atNova.filter (·.computes 2025 { kind := "car", co2GKm := 117, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := "car", co2GKm := 117, value := 30000, firstRegYear := 2025, newReg := true } == 1150
#guard ((p10atNova.filter (·.computes 2025 { kind := "car", co2GKm := 173, value := 30000, firstRegYear := 2025, newReg := true })).head!).amount 2025 { kind := "car", co2GKm := 173, value := 30000, firstRegYear := 2025, newReg := true } == 5890
#guard ((p10atVeh.filter (·.computes 2025 { kind := "car", engineKw := 80, massKg := 2100, fuel := .electric, firstRegYear := 2023 })).head!).amount 2025 { kind := "car", engineKw := 80, massKg := 2100, fuel := .electric, firstRegYear := 2023 } == 335

end AtGlobal.Other
