import DeGlobal.Pit
import TaxKernel.Global2

/-!
# DE 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (Kirchensteuer (Land church-tax laws, 8-9 % of income tax); Gewerbesteuer recorded under CIT): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: model (high revenue): Kirchensteuer 8 % / 9 % of the income tax (Land church-tax acts); needs a church-membership input


## Kirchensteuer, Berlin (pass 8, grade A)
Source: Kirchensteuerbeschluss of the Erzbistum Berlin for 2025 ff., Amtsblatt 12/2024 (`de/law/kistb_erzbistum_berlin_2025.txt`); service.berlin.de, Kirchensteuer - Festsetzung (`de/law/service_berlin_kirchensteuer.txt`); EStG § 51a (`de/law/estg_51a.txt`).
* KiStB § 2 (1): the church tax "beträgt ... 9 Prozent der Einkommensteuer (einschließlich Lohnsteuer, Kapitalertragsteuer), höchstens jedoch 3 Prozent" of the taxable income (Kappung)
* service.berlin.de: "Die Kirchensteuer beträgt 9%"; legal basis Kirchensteuergesetz Berlin
* EStG § 51a (2): the base is the income tax with the child allowances of § 32 (6) in every case
* The pilot's Land is Berlin (Grundsteuer, `DeGlobal/Basic.lean`); the 1.x detax line computes the Kirchensteuer as a surtax on the income tax when run with --kist=900 (9 %, the Berlin rate read here); no second charge is added, the 1.x output is unchanged.


## 5200 Kraftfahrzeugsteuer (pass 9, kernel 2.4.0, grade A)
Source: Kraftfahrzeugsteuergesetz 2002 §§ 3d, 9, 11, gesetze-im-internet.de (`de/law/kraftstg_9.txt`, `kraftstg_3d.txt`, `kraftstg_11.txt`).
* § 9 (1) Nr. 2 c (first registration from 1.1.2021): "für je 100 Kubikzentimeter Hubraum oder einem Teil davon 2 Euro für Fremdzündungsmotoren und 9,50 Euro für Selbstzündungsmotoren" plus per g CO2/km above 95: 2,00 EUR to 115, 2,20 to 135, 2,50 to 155, 2,90 to 175, 3,40 to 195, 4,00 above
* § 9 (1) Nr. 2 b (1.7.2009-31.12.2020): the same cm³ rates plus 2 EUR per g/km above 120 (to 2011), 110 (from 2012), 95 (from 2014)
* § 3d (1): electric vehicles first registered 18.5.2011-31.12.2030 are exempt for ten years, at most to 31.12.2035
* Germany's motor-vehicle tax is federal; it is modelled for cars, in whole euros, for the months held


## year-in-force re-cite (pass 12, FT reviewer 6 Y-12)
* KraftStG § 3d: the held text is the wording after 2025; the exemption of electric cars first registered from 2016 gives the same result for 2025

* **6000 Kirchensteuer (Berlin): reclassified (gap pass 2)**: not a tax (OECD guide § 6): the Kirchensteuer is levied by the churches, public-law religious societies outside general government; the Finanzamt collects it for them; the 1.x surtax option (--kist=900) is kept as it is and the default run (not a member) charges nothing (OECD: OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 6: church taxes are included only in countries where the church forms part of general government; levies paid to non-government bodies are excluded even where compulsory, unless the government is more than an agent; law: WRV Art. 137 (6) (via GG Art. 140): the religious societies that are public-law corporations are entitled to levy taxes on the basis of the civil tax lists under Land law (lexifina/germany-law `bund/gesetze/wrv/art-137.md`, commit b1f5fa6b7b04d); Kirchensteuergesetz Berlin as named by the Kirchensteuerbeschluss Erzbistum Berlin 2025 (`de/law/kistb_erzbistum_berlin_2025.txt`; the KiStG Berlin text itself is not held); EStG § 51a (`de/law/estg_51a.txt`); the OECD Revenue Statistics table for Germany (`tools/in_gap2/oecd/DEU.csv`, 2021-2024) has no church-tax line)
-/

namespace DeGlobal.Other
open TaxKernel TaxKernel.Global

/-- KraftStG § 9 (1) Nr. 2 b, c: 2 EUR (Fremdzündung) per started 100 cm³ -/
def p9deCcmP : QtyTable := { step := 100, steps := [(0, 2)], den := 100 }
/-- KraftStG § 9 (1) Nr. 2 b, c: 9,50 EUR (Selbstzündung) per started 100 cm³ -/
def p9deCcmD : QtyTable := { step := 100, steps := [(0, 950)], den := 10000 }
/-- KraftStG § 9 (1) Nr. 2 c: per g CO2/km above 95: 2,00 / 2,20 / 2,50 / 2,90 / 3,40 / 4,00 EUR -/
def p9deCo2c : QtyTable := { steps := [(95, 200), (115, 220), (135, 250), (155, 290), (175, 340), (195, 400)], den := 100 }
/-- KraftStG § 9 (1) Nr. 2 b: 2 EUR per g CO2/km above the threshold of the year of first registration -/
def p9deCo2b (thr : Int) : QtyTable := { steps := [(thr, 200)], den := 100 }
def p9deCar (fs : List VehicleFuel) (ccm co2 : QtyTable) (f t : Nat) (st : String) : VehicleTax :=
  { name := "Kraftfahrzeugsteuer", kinds := ["car"], fuels := fs, regFrom := f, regTo := t,   parts := [(.engineCcm, ccm), (.co2GKm, co2)], statute := st }
def p9dePetrol : List VehicleFuel := [.petrol, .lpg, .cng]
def p9deVeh : List VehicleTax :=
  [p9deCar p9dePetrol p9deCcmP p9deCo2c 2021 0 "KraftStG § 9 (1) Nr. 2 c (Fremdzündung)",  p9deCar [.diesel] p9deCcmD p9deCo2c 2021 0 "KraftStG § 9 (1) Nr. 2 c (Selbstzündung)",  p9deCar p9dePetrol p9deCcmP (p9deCo2b 95) 2014 2020 "KraftStG § 9 (1) Nr. 2 b cc (Fremdzündung, über 95 g/km)",  p9deCar [.diesel] p9deCcmD (p9deCo2b 95) 2014 2020 "KraftStG § 9 (1) Nr. 2 b cc (Selbstzündung, über 95 g/km)",  p9deCar p9dePetrol p9deCcmP (p9deCo2b 110) 2012 2013 "KraftStG § 9 (1) Nr. 2 b bb (Fremdzündung, über 110 g/km)",  p9deCar [.diesel] p9deCcmD (p9deCo2b 110) 2012 2013 "KraftStG § 9 (1) Nr. 2 b bb (Selbstzündung, über 110 g/km)",  p9deCar p9dePetrol p9deCcmP (p9deCo2b 120) 2009 2011 "KraftStG § 9 (1) Nr. 2 b aa (Fremdzündung, über 120 g/km)",  p9deCar [.diesel] p9deCcmD (p9deCo2b 120) 2009 2011 "KraftStG § 9 (1) Nr. 2 b aa (Selbstzündung, über 120 g/km)",  { name := "Kraftfahrzeugsteuer", kinds := ["car"], fuels := [.electric], regFrom := 2016,    statute := "KraftStG § 3d (1): Elektrofahrzeuge first registered 18.5.2011-31.12.2030 exempt for ten years (to 31.12.2035 at most)" }]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Kraftfahrzeugsteuer (pass 9)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p9deVeh g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["DE 6000 Kirchensteuer: KiStB Erzbistum Berlin 2025 § 2 (1), EStG § 51a (A)", "DE 5200 Kraftfahrzeugsteuer pass 9: gesetze-im-internet.de, fetched 2026-11-21 (grade A)", "DE year-in-force re-cite (pass 12): KraftStG § 3d: the held text is the wording after 2025; the exemption of electric cars first registered from 2016 gives the same result for 2025", "DE 6000 Kirchensteuer (Berlin): reclassified (gap pass 2): not a tax (OECD guide § 6): the Kirchensteuer is levied by the churches, public-law religious societies outside general government; the Finanzamt collects it for them; the 1.x surtax option (--kist=900) is kept as it is and the default run (not a member) charges nothing"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if true then ["6000 Other taxes recorded by the registry: not modelled (grade C: the registry's row (background, not a read text); not modelled)"] else [])
  ++ (if g.entity != .company && !(args.any (·.startsWith "--kist=")) then ["6000 Kirchensteuer: computed by the 1.x model as a surtax only with --kist=900 (Berlin, KiStB § 2 (1)); without it the household is taken as not a member of a church levying it"] else [])
  ++ (if !(vehicleTaxUnknown "Kraftfahrzeugsteuer" p9deVeh g).isEmpty then ["5200 Kraftfahrzeugsteuer: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Kraftfahrzeugsteuer" p9deVeh g).isEmpty then ["5200 Kraftfahrzeugsteuer: a vehicle no rule reaches: cars first registered before 2009 (Euro-class rates, § 9 (1) Nr. 2 a), hybrids (engine type not given), electric cars of 2011-2015 (weight rates, § 9 (2)), motorcycles, motor caravans, vans and lorries (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.firstRegYear == 2009) then ["5200 Kraftfahrzeugsteuer: a car first registered in 2009 is taken under § 9 (1) Nr. 2 b (only from 1 July 2009; earlier: Nr. 2 a)"] else [])
  ++ (if g.vehicles.any (fun v => v.fuel == .electric && v.firstRegYear == 2015) then ["5200 Kraftfahrzeugsteuer: an electric car of 2015 leaves the § 3d exemption during 2025 (not split)"] else [])

#guard p9deCcmP.amount 1598 == 32
#guard p9deCcmD.amount 1968 == 190
#guard p9deCo2c.amount 150 == 121
#guard p9deCo2c.amount 95 == 0
#guard (p9deVeh.head!).amount 2025 { kind := "car", engineCcm := 1598, co2GKm := 150, fuel := .petrol, firstRegYear := 2022 } == 153
#guard (p9deVeh[1]!).amount 2025 { kind := "car", engineCcm := 1968, co2GKm := 130, fuel := .diesel, firstRegYear := 2023 } == 263
#guard (p9deVeh[2]!).amount 2025 { kind := "car", engineCcm := 1395, co2GKm := 120, fuel := .petrol, firstRegYear := 2016 } == 78

end DeGlobal.Other
