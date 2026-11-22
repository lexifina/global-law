import SeGlobal.Pit
import TaxKernel.Global2

/-!
# SE 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes


## 5200 Fordonsskatt (pass 10, kernel 2.4.0, grade A)
Source: Vägtrafikskattelag (2006:227), Riksdagen (`se/law/vtsl2006_227.txt`).
* 8 §: grundbelopp 360 kronor a year; 9 §: koldioxidbelopp 22 kronor per g CO2/km above 111 g (11 kronor for alcohol and gas other than LPG)
* 9 a §: cars of fordonsår 2018 or later first taxable from 1 June 2022, for the first three years: 107 kronor per g above 75 up to 125 g and 132 kronor per g above 125 g (not for gas cars)
* 7 §, 10 §: diesel cars: (grundbelopp + koldioxidbelopp) x bränslefaktor 2,37 + miljötillägg 250 kronor (500 if first taxable before the end of 2007); diesel of fordonsår 2018 first taxable from 1 July 2018: + bränsletillägg 13,52 kronor per g CO2/km + miljötillägg
* the first three years are read by calendar year: cars first registered 2023-2025 are inside them for all of 2025; the text is the consolidation to SFS 2025:1369 (amendments to bilaga 2 only after Lag 2024:1134)


## year-in-force re-cite (pass 12, FT reviewer 6 Y-12)
* vägtrafikskattelag 2 kap. 9 a § as worded by Lag 2024:1134 applies from 1 February 2025; January 2025 falls under the old first and third paragraphs (one month of the year; not split)


## 5200 2 kap. 9 a §: the three-year window (pass 17, kernel 2.7.0)
* 9 a § (Lag 2024:1134): for cars of fordonsår 2018 or later first taxable on 1 June 2022 or later, the 107 / 132 kronor koldioxidbelopp applies instead of 9 § "under tid som infaller under de tre första åren" from first taxability
* Kernel: the ordinary 9 § part (22 kronor per g above 111) plus a window part with the difference (107 kronor per g from 75, 85 from 111, 110 from 125: 107 - 22 and 132 - 22 above 111), `partWindows := [{ part := 1, months := 36 }]`; cars first registered January-May 2022 are outside 9 a §; a 2022 car without the month is grade C
* Hand check (case se-veh-2022-08): petrol, 140 g/km, first registered August 2022: window August 2022-July 2025, 7 months of 2025: 360 + 22 x 29 + (36 x 107 + 14 x 85 + 15 x 110) x 7/12 = 360 + 638 + 6 692 x 7/12 = 4 901,67 kronor (= 360 + 638 x 5/12 + 7 330 x 7/12)

* **6000 not levied (cited, gap pass, grade B)**: European Commission TEDB, SE: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 499, 503, 516, 705, 890, 501, 512, 513, 517, 527-530, 708, 886, 3907, 5022, 5422, 5599, 5700, 5800, 5801) read against the OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 85 (6000: taxes on bases other than those of headings 1000-5000): none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: capital income tax and dividend withholding 1100; tax on life insurance premiums and on pension fund earnings 1100 / 1200; real estate tax and fee 4100; stamp duty 4400; payroll tax (särskild löneskatt) 3000 / 2200 (§ 47); sulphur, gravel, pesticide, nuclear, waste, chemicals, nicotine, plastic-bag and incineration taxes 5121 / 5128; motor vehicle tax 5200; lottery, gambling and air travel taxes 5126 (§ 72); traffic insurance tax 5126; bank deposit guarantee fee 5126 (§ 73) (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))


## 6000 Kyrkoavgift (Svenska kyrkan): not a tax (OECD guide § 6) (gap pass, grade C)
Source: Lag (1998:1591) om Svenska kyrkan 1 § (the Church of Sweden is an Evangelical Lutheran faith community); lag (1999:291) om avgift till registrerat trossamfund 1 § (state help in fixing, debiting and collecting the fees; kyrkoavgift under 7-8 §§ of the 1998 act), lexifina/sweden-law `1998/1591/1.md`, `1999/291/1.md` (HEAD 2026-11-16, wording since Lag 2024:490).
* OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 6: church taxes are included only in countries where the church forms part of general government; levies paid to non-government bodies are excluded even where compulsory, unless the government is more than an agent
* not a tax (OECD guide § 6): since 2000 the Church of Sweden is a registered faith community, not a state body; the Skatteverket only helps to fix, debit and collect the fee (agency capacity); the 1.x model does not charge it

* **6000: absence withdrawn (gap pass 2)**: gap pass 2: the cited absence of the gap pass (TEDB list read against the guide) is withdrawn: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVSWE v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/SWE.csv`, SHA256SUMS; general government S13; 2025 not yet published) books revenue under heading 6000: 6200 total 2 617, 3 294, 2 057, 2 465 million SEK in 2021-2024 (unnamed); the national taxes behind it not read
-/

namespace SeGlobal.Other
open TaxKernel TaxKernel.Global

/-- Vägtrafikskattelag (2006:227) 2 kap. 8-10 §§ (öre a year; multiplierBp 100 gives kronor) -/
def p10seCar (fs : List VehicleFuel) (f t : Nat) (fixed : Int) (co2 : QtyTable) (st : String) : VehicleTax :=
  { name := "Fordonsskatt", kinds := ["car"], fuels := fs, regFrom := f, regTo := t, fixed := fixed,   parts := [(.co2GKm, co2)], multiplierBp := 100, statute := st }
def p10seNonDiesel : List VehicleFuel := [.petrol, .hybrid, .pluginHybrid, .electric, .lpg, .hydrogen, .other]
def p10seVeh : List VehicleTax :=
  [p10seCar [.cng] 2006 0 36000 { steps := [(111, 1100)] } "2 kap. 7-9 §§: grundbelopp 360 kr, 11 kr per g CO2/km above 111 (gas other than LPG)",  p10seCar p10seNonDiesel 2023 0 36000 { steps := [(75, 10700), (125, 13200)] } "2 kap. 7, 8, 9 a §§: first three years: 360 kr, 107 kr per g above 75 to 125, 132 kr per g above 125",  p10seCar [.diesel] 2023 0 61000 { steps := [(0, 1352), (75, 12052), (125, 14552)] } "2 kap. 7, 8, 9 a, 10 §§: first three years, diesel: 360 kr + 107 / 132 kr per g + bränsletillägg 13,52 kr per g + miljötillägg 250 kr",  p10seCar p10seNonDiesel 2006 2022 36000 { steps := [(111, 2200)] } "2 kap. 7-9 §§: grundbelopp 360 kr, 22 kr per g CO2/km above 111",  p10seCar [.diesel] 2018 2022 61000 { steps := [(0, 1352), (111, 3552)] } "2 kap. 7 § tredje stycket, 8-10 §§: diesel of fordonsår 2018 or later: 360 kr + 22 kr per g above 111 + bränsletillägg 13,52 kr per g + miljötillägg 250 kr",  p10seCar [.diesel] 2008 2017 110320 { steps := [(111, 5214)] } "2 kap. 7 § andra stycket, 8-10 §§: diesel: (360 kr + 22 kr per g above 111) x bränslefaktor 2,37 + miljötillägg 250 kr",  p10seCar [.diesel] 2006 2007 135320 { steps := [(111, 5214)] } "2 kap. 7 § andra stycket, 8-10 §§: diesel: (360 kr + 22 kr per g above 111) x 2,37 + miljötillägg 500 kr (taxable before the end of 2007)"]
/-- p17 (kernel 2.7.0): 2 kap. 9 a § as a window part: the 107 / 132 kronor amounts less the 9 § 22 kronor above 111 g, for the
months of the first three years after the car became taxable (`partWindows`, 36 months from the month of first registration) -/
def p17seWinDiff : QtyTable := { steps := [(75, 10700), (111, 8500), (125, 11000)] }
def p17seCarW (fs : List VehicleFuel) (f t : Nat) (w : List (VehicleAttr × Int × Int)) (fixed : Int) (co2 : QtyTable) (st : String) : VehicleTax :=
  { p10seCar fs f t fixed co2 st with when := w, parts := [(.co2GKm, co2), (.co2GKm, p17seWinDiff)], partWindows := [{ part := 1, months := 36 }] }
def p17seOrd : QtyTable := { steps := [(111, 2200)] }
def p17seDsl : QtyTable := { steps := [(0, 1352), (111, 3552)] }
/-- 9 a § reaches cars of fordonsår 2018 or later first taxable from 1 June 2022 (not gas other than LPG): first registered
2023-2025, or 2022 from June (`firstRegMonth` 6-12); a 2022 car without the month is not placed (grade C) -/
def p17seVeh : List VehicleTax :=
  [ p10seVeh[0]!,   p17seCarW p10seNonDiesel 2023 0 [] 36000 p17seOrd "2 kap. 7-9, 9 a §§: 360 kr + 22 kr per g above 111; first three years: 107 kr per g above 75 to 125 and 132 kr above 125 instead (window part)",   p17seCarW [.diesel] 2023 0 [] 61000 p17seDsl "2 kap. 7, 8, 9, 9 a, 10 §§: diesel: 360 kr + 22 kr per g above 111 + bränsletillägg 13,52 kr per g + miljötillägg 250 kr; first three years 107 / 132 kr per g instead of 22 (window part)",   p17seCarW p10seNonDiesel 2022 2022 [(.firstRegMonth, 5, 12)] 36000 p17seOrd "2 kap. 7-9, 9 a §§ (first taxable June-December 2022): 360 kr + 22 kr per g above 111; 107 / 132 kr per g instead to the end of the three years (window part)",   p17seCarW [.diesel] 2022 2022 [(.firstRegMonth, 5, 12)] 61000 p17seDsl "2 kap. 7-10 §§, 9 a § (diesel first taxable June-December 2022): 360 kr + 22 kr per g above 111 + 13,52 kr per g + 250 kr; 107 / 132 kr per g instead to the end of the three years (window part)",   p10seCar p10seNonDiesel 2006 2021 36000 p17seOrd "2 kap. 7-9 §§: grundbelopp 360 kr, 22 kr per g CO2/km above 111",   { p10seCar p10seNonDiesel 2022 2022 36000 p17seOrd "2 kap. 7-9 §§ (first taxable January-May 2022, outside 9 a §): 360 kr, 22 kr per g CO2/km above 111" with when := [(.firstRegMonth, 0, 5)] },   p10seCar [.diesel] 2018 2021 61000 p17seDsl "2 kap. 7 § tredje stycket, 8-10 §§: diesel of fordonsår 2018 or later: 360 kr + 22 kr per g above 111 + bränsletillägg 13,52 kr per g + miljötillägg 250 kr",   { p10seCar [.diesel] 2022 2022 61000 p17seDsl "2 kap. 7 § tredje stycket, 8-10 §§ (diesel first taxable January-May 2022, outside 9 a §): 360 kr + 22 kr per g above 111 + 13,52 kr per g + 250 kr" with when := [(.firstRegMonth, 0, 5)] },   p10seVeh[5]!, p10seVeh[6]! ]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Fordonsskatt (pass 10; 9 a § window, pass 17)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p17seVeh g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["SE 5200 Fordonsskatt pass 10: data.riksdagen.se, ändrad t.o.m. SFS 2025:1369; 9 a § as worded by Lag (2024:1134) (`se/law/vtsl2006_227.txt`) (grade A)", "SE year-in-force re-cite (pass 12): vägtrafikskattelag 2 kap. 9 a § as worded by Lag 2024:1134 applies from 1 February 2025; January 2025 falls under the old first and third paragraphs (one month ", "SE 5200 pass 17 (kernel 2.7.0): 2 kap. 9 a § as a window part (partWindows, 36 months): a car first taxable from June 2022 pays the 107 / 132 kronor amounts only for the months of 2025 inside its first three years", "SE gap pass: Kyrkoavgift (Svenska kyrkan)", "SE 6000 gap pass 2: cited absence withdrawn (OECD Revenue Statistics book revenue under 6000)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(vehicleTaxUnknown "Fordonsskatt" p17seVeh g).isEmpty then ["5200 Fordonsskatt: a vehicle lacks an attribute the rate needs, or (first registered in 2022) the month that places it in or out of 9 a § and ends its window (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Fordonsskatt" p17seVeh g).isEmpty then ["5200 Fordonsskatt: a vehicle no rule reaches: cars of fordonsår before 2006, light buses and lorries, motorcycles (180 kr), heavy vehicles (bilaga 2) (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.fuel == .hybrid || v.fuel == .pluginHybrid) then ["5200 fordonsskatt: a hybrid is taken as not driven by diesel"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 fordonsskatt: the reduction of 2 kap. 11 § (cars at home in a municipality of bilaga 1) is not applied"] else [])
  ++ (if g.vehicles.any (fun v => 2022 ≤ v.firstRegYear) then ["5200 fordonsskatt 9 a §: the three years are counted as 36 whole months from the month of first registration (the last part-month is not counted); January 2025 is taken under the wording of Lag 2024:1134 (in force 1.2.2025)"] else [])
  ++ (if true then ["6000 Other taxes (6000): not modelled (grade C: gap pass 2, OECD Revenue Statistics book revenue under 6000)"] else [])

#guard (p10seVeh[1]!).amount 2025 { kind := "car", co2GKm := 120, fuel := .petrol, firstRegYear := 2024 } == 5175
#guard (p10seVeh[1]!).amount 2025 { kind := "car", co2GKm := 150, fuel := .petrol, firstRegYear := 2024 } == 9010
#guard (p10seVeh[2]!).amount 2025 { kind := "car", co2GKm := 120, fuel := .diesel, firstRegYear := 2024 } == 7047
#guard (p10seVeh[3]!).amount 2025 { kind := "car", co2GKm := 150, fuel := .petrol, firstRegYear := 2015 } == 1218
#guard (p10seVeh[5]!).amount 2025 { kind := "car", co2GKm := 130, fuel := .diesel, firstRegYear := 2012 } == 2093
#guard (p10seVeh[1]!).amount 2025 { kind := "car", co2GKm := 0, fuel := .electric, firstRegYear := 2024 } == 360
#guard p17seVeh.length == 11
#guard (p17seVeh[5]!).amount 2025 { kind := "car", co2GKm := 150, fuel := .petrol, firstRegYear := 2015 } == 1218
#guard (p17seVeh[6]!).computes 2025 { kind := "car", co2GKm := 150, fuel := .petrol, firstRegYear := 2022, firstRegMonth := 3 }
#guard !(p17seVeh[6]!).computes 2025 { kind := "car", co2GKm := 150, fuel := .petrol, firstRegYear := 2022, firstRegMonth := 6 }
#guard (p17seVeh[3]!).computes 2025 { kind := "car", co2GKm := 150, fuel := .petrol, firstRegYear := 2022, firstRegMonth := 6 }
#guard !(p17seVeh[3]!).computes 2025 { kind := "car", co2GKm := 150, fuel := .petrol, firstRegYear := 2022 }

end SeGlobal.Other
