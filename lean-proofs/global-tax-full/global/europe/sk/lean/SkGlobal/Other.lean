import SkGlobal.Pit
import TaxKernel.Global2

/-!
# SK 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes recorded by the registry (Bank levy (osobitný odvod); licence fees): tried the registry's row (background, not a read text); not modelled; would unlock: the statutes named in the registry row

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor here: bank levy is sector-only; licence fees small


## 5200 Daň z motorových vozidiel (pass 10, kernel 2.4.0, grade A)
Source: Zákon č. 361/2014 Z. z. o dani z motorových vozidiel, Slov-Lex, znenie účinné od 1. 1. 2025 (`sk/law/dmv361_20250101.txt`).
* § 2 ods. 1: "Predmetom dane je vozidlo, ktoré je evidované v Slovenskej republike a používa sa na podnikanie": a company's vehicles are taxed, a household's vehicles are not (cited 0)
* § 5 ods. 2: base for L and M1 = cylinder capacity in cm3; ods. 1: electric vehicles by kW, príloha č. 1: 0 EUR
* príloha č. 1 (from 2025): to 150 cm3 50 EUR; 150-900 62; 900-1200 80; 1200-1500 115; 1500-2000 148; 2000-3000 180; above 3000 218
* § 7 ods. 1: the rate applies for the first 36 months from first registration, then +10 %, +20 %, +30 %, +40 % for each further 36 months, +50 % after 180 months; ods. 2: 50 % less for hybrids, CNG/LNG and hydrogen vehicles

* **6000 not levied (cited, gap pass, grade B)**: European Commission TEDB, SK: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 553, 559, 816, 817) read against the OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 85 (6000: taxes on bases other than those of headings 1000-5000): none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: motor vehicle tax 5200; immovable property tax 4100; taxes on lotteries 5126; the registry's two items: the bank levy (osobitný odvod) is a 5126 tax (§ 73) and the radio and TV licence fee is a non-tax payment where a public broadcaster provides the service (§ 14) (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))
-/

namespace SkGlobal.Other
open TaxKernel TaxKernel.Global

/-- Zákon 361/2014 Z. z. príloha č. 1 (od 1. 1. 2025): M1 by cylinder capacity, EUR a year -/
def p10skCcm : QtyTable := QtyTable.ofCeilings [(150, 50), (900, 62), (1200, 80), (1500, 115), (2000, 148), (3000, 180)] 218
/-- § 7 (1): +10 % / 20 % / 30 % / 40 % / 50 % after 36 / 72 / 108 / 144 / 180 months (read by calendar years) -/
def p10skAge : List (Int × Int) := [(0, 10000), (3, 11000), (6, 12000), (9, 13000), (12, 14000), (15, 15000)]
def p10skVeh : List VehicleTax :=
  [{ name := "Daň z motorových vozidiel", kinds := ["car", "motorcycle"], fuels := [.electric],    statute := "zákon 361/2014 Z. z. § 5 (1), príloha č. 1: a vehicle whose only energy source is electricity, 0 EUR" },  { name := "Daň z motorových vozidiel", kinds := ["car", "motorcycle"], fuels := [.hybrid, .pluginHybrid, .cng, .hydrogen],    parts := [(.engineCcm, p10skCcm)], ageFactors := p10skAge, multiplierBp := 5000,    statute := "zákon 361/2014 Z. z. § 5 (2), § 6 (1), § 7 (1), (2), príloha č. 1: hybrid, CNG/LNG or hydrogen: 50 % less" },  { name := "Daň z motorových vozidiel", kinds := ["car", "motorcycle"], fuels := [.petrol, .diesel, .lpg, .other],    parts := [(.engineCcm, p10skCcm)], ageFactors := p10skAge,    statute := "zákon 361/2014 Z. z. § 5 (2), § 6 (1), § 7 (1), príloha č. 1" }]
/-- § 2 (1): only a vehicle used for business is subject to the tax; a household's vehicle is not -/
def p10skHh : List VehicleTax :=
  [{ name := "Daň z motorových vozidiel", statute := "zákon 361/2014 Z. z. § 2 ods. 1: predmetom dane je vozidlo, ktoré sa používa na podnikanie: a household's vehicle is not subject" }]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Daň z motorových vozidiel (pass 10)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges (if g.entity == .company then p10skVeh else p10skHh) g (firstOnly := true) }]

def absent : List Absent :=
  [{ oecd := .other, why := "none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: motor vehicle tax 5200; immovable property tax 4100; taxes on lotteries 5126; the registry's two items: the bank levy (osobitný odvod) is a 5126 tax (§ 73) and the radio and TV licence fee is a non-tax payment where a public broadcaster provides the service (§ 14)" }]

def notes : List String := ["SK 5200 Daň z motorových vozidiel pass 10: Slov-Lex, znenie od 1. 1. 2025 (`sk/law/dmv361_20250101.txt`) (grade A)", "SK 6000 gap pass: not levied (cited, B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(vehicleTaxUnknown "Daň z motorových vozidiel" (if g.entity == .company then p10skVeh else p10skHh) g).isEmpty then ["5200 Daň z motorových vozidiel: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Daň z motorových vozidiel" (if g.entity == .company then p10skVeh else p10skHh) g).isEmpty then ["5200 Daň z motorových vozidiel: a vehicle no rule reaches: company vehicles other than L and M1 (N1-N3, M2-M3 by weight and axles, trailers) (grade C)"] else [])
  ++ (if g.entity == .company && !g.vehicles.isEmpty then ["5200 daň z motorových vozidiel: the 36-month periods of § 7 (1) are read by calendar years since first registration; a company's vehicles are taken as used for business all year"] else [])

#guard p10skCcm.amount 1598 == 148
#guard p10skCcm.amount 1500 == 115
#guard p10skCcm.amount 3500 == 218
#guard (p10skVeh[2]!).amount 2025 { kind := "car", engineCcm := 1598, fuel := .diesel, firstRegYear := 2019 } == 177
#guard (p10skVeh[1]!).amount 2025 { kind := "car", engineCcm := 1798, fuel := .hybrid, firstRegYear := 2024 } == 74
#guard (p10skHh.head!).amount 2025 { kind := "car", engineCcm := 1598, fuel := .petrol, firstRegYear := 2019 } == 0

end SkGlobal.Other
