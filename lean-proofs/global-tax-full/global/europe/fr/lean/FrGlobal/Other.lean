import FrGlobal.Pit
import TaxKernel.Global2

/-!
# FR 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (CVAE (CGI art. 1586 ter, being phased out); CFE (CGI art. 1447); taxe d'habitation on second homes): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: model (high revenue): CFE (CGI art. 1447) and CVAE (art. 1586 ter, being phased out); taxe d'habitation on second homes


## 5200 Taxe sur les émissions de CO2 des véhicules de tourisme (malus) (pass 10, kernel 2.4.0, grade B)
Source: Barème from Service Public (DILA), page F35947 "Taxe sur les émissions de CO2 des véhicules de tourisme (malus CO2)", table for 1 March - 31 December 2025, WLTP (Légifrance answers 403 and the Internet Archive holds no capture of L. 421-62 in its 2025 wording); L. 421-58 to L. 421-67 read in `fr/law/cibs_wb/LEGISCTA000044599051.html` and `LEGISCTA000044599077.html`.
* L. 421-59: the tax is a tariff per vehicle set by its CO2 emissions in the barème of the year of first registration (WLTP: L. 421-62)
* barème 2025 (from 1 March 2025): below 113 g/km 0 EUR; 113 g/km 50; 130 g/km 540; 150 g/km 3 119; 170 g/km 14 325; 192 g/km 67 467; above 192 g/km 70 000 (every gram in the table)
* L. 421-67: a vehicle whose energy source is exclusively electricity, hydrogen or both is exempt
* L. 421-60: 10 % less per started period of twelve months since first registration (used vehicles first registered abroad); L. 421-61 bis cap at 50 % of the price including taxes; L. 421-68 E85 abatements; family abatements: not applied (listed)
* January and February 2025 used the 2024 barème (threshold 118 g/km, `cibs_wb/LEGISCTA000044599051.html`): not split


## 5200 Taxe fixe sur les certificats d'immatriculation (pass 10, kernel 2.4.0, grade A)
Source: CIBS L. 421-37 to L. 421-40, Légifrance via the Internet Archive (`fr/law/cibs_wb/LEGISCTA000044598993.html`).
* L. 421-38: "Le montant de la taxe est égal à 11 €"; L. 421-39, 421-40: exempt certificates (address update, corrections, storm replacements)
* booked once for each vehicle registered in the year; a change of holder of a used vehicle is not in the input


## year-in-force re-cite (pass 12, FT reviewer 6 Y-12)
* malus CO2: the 2025 barème applies from 1 March 2025; January and February 2025 registrations fall under the 2024 barème (declared, not split; grade B kept)


## 5200 malus: first registrations before 1 March 2025 (pass 14, kernel 2.6.0)
Source: CIBS art. L. 421-62, Légifrance section LEGISCTA000044599051 as captured by the Internet Archive (version en vigueur au 15 juillet 2024, `fr/law/cibs_wb/LEGISCTA000044599051.html`).
* L. 421-62 (modified by loi n° 2023-1322 du 29 décembre 2023, art. 97) gives the WLTP barème for the years from 2024: 0 below 117 g/km, 50 euros at 118 g/km, rising by the gram to 55 023 euros at 193 g/km, 60 000 euros above (the text lists no line for 117 g/km itself; it is read with the 0 band)
* the next change is the 2025 finance law's barème, applied to first registrations from 1 March 2025 (pass 10); so a car first registered in January or February 2025 pays the 2024 barème, and a 2025 car whose month is not given is grade C
* Hand check (case fr-veh-feb): petrol car of 150 g/km first registered in February 2025: 2 205 euros (+ taxe fixe 11); case fr-veh-apr (April): 3 119 euros (+ 11)
-/

namespace FrGlobal.Other
open TaxKernel TaxKernel.Global

/-- CIBS L. 421-62, barème WLTP for vehicles first registered from 1 March to 31 December 2025 (euros): below 113 g/km 0,
113 g/km 50, …, 192 g/km 67 467, above 192 g/km 70 000 -/
def p10frMalus : QtyTable := QtyTable.ofCeilings [(112, 0), (113, 50), (114, 75), (115, 100), (116, 125), (117, 150), (118, 170), (119, 190), (120, 210), (121, 230), (122, 240), (123, 260), (124, 280), (125, 310), (126, 330), (127, 360), (128, 400), (129, 450), (130, 540), (131, 650), (132, 740), (133, 818), (134, 898), (135, 983), (136, 1074), (137, 1172), (138, 1276), (139, 1386), (140, 1504), (141, 1629), (142, 1761), (143, 1901), (144, 2049), (145, 2205), (146, 2370), (147, 2544), (148, 2726), (149, 2918), (150, 3119), (151, 3331), (152, 3552), (153, 3784), (154, 4026), (155, 4279), (156, 4543), (157, 4818), (158, 5105), (159, 5404), (160, 5715), (161, 6126), (162, 6537), (163, 7248), (164, 7959), (165, 8770), (166, 9681), (167, 10692), (168, 11803), (169, 13014), (170, 14325), (171, 15736), (172, 17247), (173, 18858), (174, 20569), (175, 22380), (176, 24291), (177, 26302), (178, 28413), (179, 30624), (180, 32935), (181, 35346), (182, 37857), (183, 40468), (184, 43179), (185, 45990), (186, 48901), (187, 51912), (188, 55023), (189, 58134), (190, 61245), (191, 64356), (192, 67467)] 70000
/-- CIBS L. 421-62 as modified by loi n° 2023-1322 art. 97, barème WLTP "pour les années à compter de 2024": below 117 g/km 0, 118 g/km 50, …, 193 g/km 55 023, above 193 g/km 60 000 (euros); in force for first registrations up to 28 February 2025 -/
def p14frMalus24 : QtyTable := QtyTable.ofCeilings [(117, 0), (118, 50), (119, 75), (120, 100), (121, 125), (122, 150), (123, 170), (124, 190), (125, 210), (126, 230), (127, 240), (128, 260), (129, 280), (130, 310), (131, 330), (132, 360), (133, 400), (134, 450), (135, 540), (136, 650), (137, 740), (138, 818), (139, 898), (140, 983), (141, 1074), (142, 1172), (143, 1276), (144, 1386), (145, 1504), (146, 1629), (147, 1761), (148, 1901), (149, 2049), (150, 2205), (151, 2370), (152, 2544), (153, 2726), (154, 2918), (155, 3119), (156, 3331), (157, 3552), (158, 3784), (159, 4026), (160, 4279), (161, 4543), (162, 4818), (163, 5105), (164, 5404), (165, 5715), (166, 6126), (167, 6537), (168, 7248), (169, 7959), (170, 8770), (171, 9681), (172, 10692), (173, 11803), (174, 13014), (175, 14325), (176, 15736), (177, 17247), (178, 18858), (179, 20569), (180, 22380), (181, 24291), (182, 26302), (183, 28413), (184, 30624), (185, 32935), (186, 35346), (187, 37857), (188, 40468), (189, 43179), (190, 45990), (191, 48901), (192, 51912), (193, 55023)] 60000
def p10frVeh : List VehicleTax :=
  [{ name := "Taxe sur les émissions de CO2 des véhicules de tourisme (malus)", kinds := ["car"], occasion := .registration,    fuels := [.electric, .hydrogen], statute := "CIBS L. 421-67: a vehicle whose energy source is exclusively electricity, hydrogen or both is exempt" },  { name := "Taxe sur les émissions de CO2 des véhicules de tourisme (malus)", kinds := ["car"], occasion := .registration,    regFrom := 2025, regTo := 2025, regFromDate := "2025-03-01", parts := [(.co2GKm, p10frMalus)],    statute := "CIBS L. 421-59 1°, L. 421-62: barème WLTP of the year of first registration (2025, from 1 March 2025)" }, { name := "Taxe sur les émissions de CO2 des véhicules de tourisme (malus)", kinds := ["car"], occasion := .registration, regFrom := 2025, regTo := 2025, regToDate := "2025-02-28", parts := [(.co2GKm, p14frMalus24)], statute := "CIBS L. 421-59 1°, L. 421-62 (loi n° 2023-1322 art. 97): barème WLTP for first registrations from 1 January to 28 February 2025" }]
/-- CIBS L. 421-38: taxe fixe on the issue of a registration certificate, 11 € -/
def p10frFixe : List VehicleTax :=
  [{ name := "Taxe fixe sur les certificats d'immatriculation", occasion := .registration, fixed := 11,    statute := "CIBS L. 421-30 1°, L. 421-38: 11 €" }]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Taxe sur les émissions de CO2 des véhicules de tourisme (malus) (pass 10)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p10frVeh g (firstOnly := true) },
   { name := "5200 Taxe fixe sur les certificats d'immatriculation (pass 10)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p10frFixe g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["FR 5200 Taxe sur les émissions de CO2 des véhicules de tourisme (malus) pass 10: barème from 1 March 2025 (service-public.gouv.fr, vérifié le 21 février 2026); L. 421-59, L. 421-67 Légifrance via the Internet Archive (2024-02-23) (grade B)", "FR 5200 Taxe fixe sur les certificats d'immatriculation pass 10: Légifrance via the Internet Archive (2025-01-24) (grade A)", "FR year-in-force re-cite (pass 12): malus CO2: the 2025 barème applies from 1 March 2025; January and February 2025 registrations fall under the 2024 barème (declared, not split; grade B kept)", "FR 5200 malus split at 1 March 2025 (kernel 2.6.0 regToDate / regFromDate): barème 2024 (loi 2023-1322 art. 97, Légifrance version of 15 July 2024) to 28 February, barème 2025 from 1 March (pass 14)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["6000 Other taxes recorded by the registry: not modelled (grade C: the registry's row (background, not a read text); not modelled)"] else [])
  ++ (if !(vehicleTaxUnknown "Taxe sur les émissions de CO2 des véhicules de tourisme (malus)" p10frVeh g).isEmpty then ["5200 Taxe sur les émissions de CO2 des véhicules de tourisme (malus): a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg && !(p10frVeh.any (·.selects g.year v))) then ["5200 Taxe sur les émissions de CO2 des véhicules de tourisme (malus): a vehicle no rule reaches: vehicles first registered before 2025 and registered in France in 2025 (used imports: earlier barèmes, L. 421-60 décote), NEDC and non-EU-approved vehicles (L. 421-63, 421-64), vehicles other than cars (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg && 0 ≤ v.value && 2 * p10frMalus.amount v.co2GKm > v.value) then ["5200 malus: the cap at 50 % of the price including taxes (L. 421-61 bis) is not applied (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg && v.firstRegYear == 2025) then ["5200 malus: a car first registered in 2025 without its month is not charged (grade C: the barème changed on 1 March 2025); family, disability and E85 abatements (L. 421-65 ff., L. 421-68) are not applied"] else [])
  ++ (if !(vehicleTaxUnknown "Taxe fixe sur les certificats d'immatriculation" p10frFixe g).isEmpty then ["5200 Taxe fixe sur les certificats d'immatriculation: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.newReg && !(p10frFixe.any (·.selects g.year v))) then ["5200 Taxe fixe sur les certificats d'immatriculation: a vehicle no rule reaches: none (every vehicle registered in the year) (grade C)"] else [])

#guard p10frMalus.amount 112 == 0
#guard p10frMalus.amount 113 == 50
#guard p10frMalus.amount 130 == 540
#guard p10frMalus.amount 192 == 67467
#guard p10frMalus.amount 193 == 70000
#guard p10frMalus.amount 0 == 0
#guard (p10frVeh.filter (·.selects 2025 { kind := "car", co2GKm := 150, fuel := .petrol, firstRegYear := 2022, newReg := true })).isEmpty
#guard (p10frFixe.head!).amount 2025 { kind := "car", firstRegYear := 2025 } == 11
#guard p14frMalus24.amount 117 == 0
#guard p14frMalus24.amount 118 == 50
#guard p14frMalus24.amount 150 == 2205
#guard p14frMalus24.amount 193 == 55023
#guard p14frMalus24.amount 194 == 60000
#guard (p10frVeh[1]!).amount 2025 { kind := "car", co2GKm := 150, fuel := .petrol, firstRegYear := 2025, firstRegMonth := 4, newReg := true } == 3119
#guard (p10frVeh[2]!).amount 2025 { kind := "car", co2GKm := 150, fuel := .petrol, firstRegYear := 2025, firstRegMonth := 2, newReg := true } == 2205
#guard (p10frVeh.filter (·.selects 2025 { kind := "car", co2GKm := 150, fuel := .petrol, firstRegYear := 2025, firstRegMonth := 2, newReg := true })).length == 1
#guard (p10frVeh.filter (·.selects 2025 { kind := "car", co2GKm := 150, fuel := .petrol, firstRegYear := 2025, firstRegMonth := 3, newReg := true })).length == 1

end FrGlobal.Other
