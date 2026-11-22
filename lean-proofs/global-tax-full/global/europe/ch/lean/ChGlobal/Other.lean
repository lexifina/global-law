import ChGlobal.Pit
import TaxKernel.Global2

/-!
# CH 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (Kirchensteuer (ZH); Personalsteuer (ZH CHF 24)): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: model (small): Kirchensteuer ZH (multiplier of the cantonal simple tax) and Personalsteuer CHF 24


## 5200 Verkehrsabgabe (Kanton Zürich) (pass 13, kernel 2.5.0, grade B)
Source: Kanton Zürich, Strassenverkehrsamt, "Verkehrsabgabe für Auto & Kleinbus" (official guide; the VAG and VAV texts were not read).
* the yearly tax on cars, minibuses and light motor vehicles up to 3,5 t is the sum of an amount for the cylinder capacity (field 37) and one for the total weight (field 33)
* cylinder capacity: up to 1 200 cm3 CHF 69; then 88, 108, 128, 148 for each further 200 cm3 to 2 000; 2 001-2 500 CHF 208; then +150 per 500 cm3 to 6 000 (1 258); then +300 per 1 000 cm3 to 11 000 (2 758); +300 per further started 1 000 cm3
* total weight: up to 1 200 kg CHF 50; 70, 100, 130, 160, 190 for each further 200 kg to 2 200; then 310, 430, 550, 670, 790 to 3 200 kg; 3 201-3 500 kg CHF 930
* rebate: 80 % (efficiency category A) or 50 % (B) with at most 130 g CO2/km, in the year of first registration and the three following years (the category is not an input: not applied)
* Hand check (case ch-veh): petrol car of 1 984 cm3 and 1 950 kg total weight: 148 + 160 = CHF 308


## 6000 Personalsteuer (Stadt Zürich) and Kirchensteuer (ZH) (gap pass, grade C)
Source: Steuergesetz des Kantons Zürich (LS 631.1, Nachtrag 127, `ch/law/stgzh_127.txt`) §§ 199-201.
* § 199 (1): the political municipalities levy a Personalsteuer on the taxable natural persons resident in their area; (2) spouses each owe it in full; (3) from the year of majority
* § 200: the Personalsteuer is Fr. 24. Computed inside the 1.x line (ChTax.Basic: + Personalsteuer 24 per adult); no second charge; OECD heading 6000 (guide § 85: taxes on individuals in the form of a poll tax)
* § 201 (1): the parishes (Kirchgemeinden) of the cantonal church corporations may levy taxes under this act: OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 6: church taxes are included only in countries where the church forms part of general government; levies paid to non-government bodies are excluded even where compulsory, unless the government is more than an agent
-/

namespace ChGlobal.Other
open TaxKernel TaxKernel.Global

/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1

/-- Kanton Zürich, Verkehrsabgabe für Auto & Kleinbus (VAG LS 741.1, VAV LS 741.11; Strassenverkehrsamt tariff 2025) -/
def p13chZhCcm : QtyTable := QtyTable.ofCeilings [(1200, 69), (1400, 88), (1600, 108), (1800, 128), (2000, 148), (2500, 208), (3000, 358), (3500, 508), (4000, 658), (4500, 808), (5000, 958), (5500, 1108), (6000, 1258), (7000, 1558), (8000, 1858), (9000, 2158), (10000, 2458)] 2758
def p13chZhKg : QtyTable := QtyTable.ofCeilings [(1200, 50), (1400, 70), (1600, 100), (1800, 130), (2000, 160), (2200, 190), (2400, 310), (2600, 430), (2800, 550), (3000, 670), (3200, 790)] 930
def p13chZhVeh : List VehicleTax :=
  [ { name := "Verkehrsabgabe (Kanton Zürich)", kinds := ["car"], fuels := [.petrol, .diesel, .hybrid, .pluginHybrid, .lpg, .cng, .other],     when := [(.engineCcm, -1, 11000), (.massKg, -1, 3500)], parts := [(.engineCcm, p13chZhCcm), (.massKg, p13chZhKg)], level := .local,     statute := "Verkehrsabgabengesetz ZH (LS 741.1), Verkehrsabgabenverordnung (LS 741.11): Hubraum + Gesamtgewicht" } ]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Verkehrsabgabe (Kanton Zürich) (pass 13)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p13chZhVeh g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["CH 5200 Verkehrsabgabe (Kanton Zürich) pass 13: zh.ch, Verkehrsabgabe für Auto & Kleinbus, via the Internet Archive 2025-04-27 (`ch/law/zh_verkehrsabgabe_auto_wb20250427.html`) (grade B)", "CH gap pass: Personalsteuer (Stadt Zürich); Kirchensteuer (ZH); Other taxes (6200: military-service exemption tax and other items)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(vehicleTaxUnknown "Verkehrsabgabe (Kanton Zürich)" p13chZhVeh g).isEmpty then ["5200 Verkehrsabgabe (Kanton Zürich): a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Verkehrsabgabe (Kanton Zürich)" p13chZhVeh g).isEmpty then ["5200 Verkehrsabgabe (Kanton Zürich): a vehicle no rule reaches: electric and fuel-cell cars (their tariff was not read), cars above 3,5 t or 11 000 cm3, vans, motorcycles, lorries and trailers (grade C)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 Verkehrsabgabe (Zürich): the input's mass is read as the total weight (Gesamtgewicht, field 33); the canton is taken as Zürich for every vehicle"] else [])
  ++ (if g.vehicles.any (fun v => decide (2022 ≤ v.firstRegYear)) then ["5200 Verkehrsabgabe (Zürich): the 80 % / 50 % rebate for efficiency categories A and B (at most 130 g/km) in the first four years is not applied: the category is not an input (grade C)"] else [])

#guard p11amt p13chZhVeh { kind := "car", fuel := .petrol, engineCcm := 1984, massKg := 1950, firstRegYear := 2019 } == 308
#guard p11amt p13chZhVeh { kind := "car", fuel := .petrol, engineCcm := 1200, massKg := 1200, firstRegYear := 2019 } == 119
#guard p11amt p13chZhVeh { kind := "car", fuel := .diesel, engineCcm := 1201, massKg := 1201, firstRegYear := 2019 } == 158
#guard p11amt p13chZhVeh { kind := "car", fuel := .petrol, engineCcm := 2998, massKg := 2400, firstRegYear := 2019 } == 668
#guard p11amt p13chZhVeh { kind := "car", fuel := .petrol, engineCcm := 10500, massKg := 3500, firstRegYear := 2019 } == 3688
#guard p11amt p13chZhVeh { kind := "car", fuel := .hybrid, engineCcm := 1798, massKg := 1800, firstRegYear := 2019 } == 258
#guard p11amt p13chZhVeh { kind := "car", fuel := .electric, massKg := 2100, firstRegYear := 2023 } == -1
#guard p11amt p13chZhVeh { kind := "car", fuel := .petrol, engineCcm := 1984, massKg := 3600, firstRegYear := 2019 } == -1

end ChGlobal.Other
