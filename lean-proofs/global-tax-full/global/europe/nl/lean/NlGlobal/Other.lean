import NlGlobal.Pit
import TaxKernel.Global2

/-!
# NL 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes


## 5200 Motorrijtuigenbelasting (pass 10, kernel 2.4.0, grade A)
Source: Wet op de motorrijtuigenbelasting 1994, wetten.overheid.nl, geldig op 01-07-2025 (`nl/law/mrb_g2025.txt`).
* art. 23 lid 1: per period of three months, 20,86 EUR (500 kg or less), 28,30 (600), 35,96 (700), 46,94 (800), 62,43 at 900 kg plus 16,78 per 100 kg above 900 kg up to 3200 kg, 460,76 at 3300 kg plus 11,66 per 100 kg above
* art. 22 lid 1 b 1°: the eigen massa is rounded to the nearest 100 kg, 50 kg rounded down
* art. 23 lid 2: a brandstoftoeslag except for cars driven only by petrol, electricity, hydrogen or a combination: a. diesel 81,77 (500 kg) to 148,69 at 900 kg plus 16,10 per 100 kg; b. other fuels 95,93 to 167,23 plus 17,71; lid 3: CNG/LNG and factory LPG nil to 800 kg, then 18,51 plus 18,51 per 100 kg
* art. 23 lid 4, 5: diesel cars with particulate emissions above 5 mg/km pay 19 % more; without a registered value and a first admission before 1 September 2009 they are presumed above
* art. 23b lid 1: CO2 0 g/km pays a quarter, above 0 up to 50 g/km three quarters of the art. 23 tax
* the model books the hoofdsom (rijksdeel) for a year (four periods), rounded down to whole euros once; the provincial opcenten are not modelled

* **6000 not levied (cited, gap pass, grade B)**: European Commission TEDB, NL: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 435, 447, 682, 790, 4022, 443, 444, 685, 791, 874, 2781, 3828) read against the OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 85 (6000: taxes on bases other than those of headings 1000-5000): none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: dividend withholding tax 1100 / 1200; tax on games of chance 5126; road tax on heavy vehicles and motor vehicles tax 5200; inheritance and gift tax 4300; tax on rental housing 4100; BPM 5200 (§ 83); tap-water and waste taxes 5128; real estate transfer tax 4400 and insurance premium tax 5126; bank tax 5126 (§ 73); real estate tax 4100 (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))

* **6000: absence withdrawn (gap pass 2)**: gap pass 2: the cited absence of the gap pass (TEDB list read against the guide) is withdrawn: OECD Revenue Statistics detailed table (sdmx.oecd.org, OECD.CTP.TPS DSD_REV_OECD@DF_REVNLD v2.0, fetched 2026-11-22 with a plain research user-agent, copy `tools/in_gap2/oecd/NLD.csv`, SHA256SUMS; general government S13; 2025 not yet published) books revenue under heading 6000: 6100 administrative levies 73; 6200 other taxes 93, Caribbean Netherlands 244, wage tax reductions 722 million EUR (2024); the national taxes behind it not read
-/

namespace NlGlobal.Other
open TaxKernel TaxKernel.Global

/-- Wet MRB 1994 art. 23 lid 1 (personenauto), per three months, in cents, for the eigen massa rounded by art. 22 lid 1 b 1° -/
def p10nlBase (r : Int) : Int :=
  if r ≤ 500 then 2086 else if r ≤ 600 then 2830 else if r ≤ 700 then 3596 else if r ≤ 800 then 4694
  else if r ≤ 3200 then 6243 + 1678 * ((r - 900) / 100) else 46076 + 1166 * ((r - 3300) / 100)
/-- art. 23 lid 2 a: brandstoftoeslag dieselolie (cents per three months) -/
def p10nlDiesel (r : Int) : Int :=
  if r ≤ 500 then 8177 else if r ≤ 600 then 9678 else if r ≤ 700 then 11179 else if r ≤ 800 then 12707
  else 14869 + 1610 * ((r - 900) / 100)
/-- art. 23 lid 2 b: brandstoftoeslag, other fuels (cents per three months) -/
def p10nlOther (r : Int) : Int :=
  if r ≤ 500 then 9593 else if r ≤ 600 then 11499 else if r ≤ 700 then 13406 else if r ≤ 800 then 15310
  else 16723 + 1771 * ((r - 900) / 100)
/-- art. 23 lid 3: CNG / LNG: nihil to 800 kg, 18,51 at 900 kg plus 18,51 per 100 kg above (cents per three months) -/
def p10nlGas (r : Int) : Int := if r ≤ 800 then 0 else 1851 + 1851 * ((r - 900) / 100)
/-- A year (four periods of three months, cents) on the eigen massa in kg: art. 22 lid 1 b 1° rounds to the nearest
100 kg, 50 kg down, so the band of r kg starts at r − 49 kg -/
def p10nlYear (f : Int → Int) : QtyTable :=
  { bands := (List.range 120).map fun (i : Nat) => let j : Int := i; (if i == 0 then (0 : Int) else 451 + 100 * j, 4 * f (500 + 100 * j)) }
def p10nlCar (fs : List VehicleFuel) (ps : List (VehicleAttr × QtyTable)) (bp : Int) (st : String) (f t : Nat := 0)
    (w : List (VehicleAttr × Int × Int) := []) : VehicleTax :=
  { name := "Motorrijtuigenbelasting (hoofdsom)", kinds := ["car"], fuels := fs, regFrom := f, regTo := t, when := w,   parts := ps, multiplierBp := bp, statute := st }
/-- multiplierBp: cents to euros (100), × 1/4 (25) or 3/4 (75) by art. 23b, × 1,19 (119) by art. 23 lid 4 -/
def p10nlVeh : List VehicleTax :=
  [p10nlCar [.electric, .hydrogen] [(.massKg, p10nlYear p10nlBase)] 25 "Wet MRB 1994 art. 23b lid 1 a: CO2 0 g/km, a quarter of the art. 23 tax",  p10nlCar [.pluginHybrid] [(.massKg, p10nlYear p10nlBase)] 75 "Wet MRB 1994 art. 23b lid 1 b: CO2 above 0 up to 50 g/km, three quarters of the art. 23 tax" (w := [(.co2GKm, 0, 50)]),  p10nlCar [.petrol, .hybrid, .pluginHybrid] [(.massKg, p10nlYear p10nlBase)] 100 "Wet MRB 1994 art. 22 lid 1 b, art. 23 lid 1 (benzine: no brandstoftoeslag, lid 2)",  p10nlCar [.diesel] [(.massKg, p10nlYear p10nlBase), (.massKg, p10nlYear p10nlDiesel)] 119 "Wet MRB 1994 art. 23 lid 1, 2 a, 4, 5: brandstoftoeslag diesel and fijnstoftoeslag 19 % (presumed for a first admission before 1 September 2009)" (t := 2008),  p10nlCar [.diesel] [(.massKg, p10nlYear p10nlBase), (.massKg, p10nlYear p10nlDiesel)] 100 "Wet MRB 1994 art. 23 lid 1, 2 a: brandstoftoeslag diesel" (f := 2009),  p10nlCar [.cng] [(.massKg, p10nlYear p10nlBase), (.massKg, p10nlYear p10nlGas)] 100 "Wet MRB 1994 art. 23 lid 1, 3: CNG/LNG",  p10nlCar [.other] [(.massKg, p10nlYear p10nlBase), (.massKg, p10nlYear p10nlOther)] 100 "Wet MRB 1994 art. 23 lid 1, 2 b: other fuels"]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Motorrijtuigenbelasting (pass 10)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p10nlVeh g (firstOnly := true) }]

def absent : List Absent :=
  []

def notes : List String := ["NL 5200 Motorrijtuigenbelasting pass 10: wetten.overheid.nl, geldend op 1 juli 2025 (`nl/law/mrb_g2025.txt`) (grade A)", "NL 6000 gap pass 2: cited absence withdrawn (OECD Revenue Statistics book revenue under 6000)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(vehicleTaxUnknown "Motorrijtuigenbelasting" p10nlVeh g).isEmpty then ["5200 Motorrijtuigenbelasting: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Motorrijtuigenbelasting" p10nlVeh g).isEmpty then ["5200 Motorrijtuigenbelasting: a vehicle no rule reaches: LPG cars (art. 23 lid 2 b or 3 by installation type), bestelauto, motorrijwiel, vrachtauto, autobus (grade C)"] else [])
  ++ (if g.vehicles.any (fun v => v.fuel == .diesel && 2009 ≤ v.firstRegYear) then ["5200 Motorrijtuigenbelasting: a diesel car first admitted from 2009 is taken as emitting at most 5 mg/km of particulates (no fijnstoftoeslag, art. 23 lid 4); 2009 is read as from 1 September"] else [])
  ++ (if g.vehicles.any (fun v => v.fuel == .hybrid || v.fuel == .pluginHybrid) then ["5200 Motorrijtuigenbelasting: a hybrid is taken as petrol-electric (no brandstoftoeslag, art. 23 lid 2)"] else [])
  ++ (if g.vehicles.any (fun v => v.fuel == .pluginHybrid && v.co2GKm < 0) then ["5200 Motorrijtuigenbelasting: a plug-in hybrid without CO2 is booked at the full art. 23 tax (art. 23b lid 1 b not tested)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 Motorrijtuigenbelasting: provinciale opcenten (Provinciewet art. 222) not modelled (grade C)"] else [])
  ++ (if true then ["6000 Other taxes (6000): not modelled (grade C: gap pass 2, OECD Revenue Statistics book revenue under 6000)"] else [])

#guard (p10nlYear p10nlBase).amount 550 == 8344
#guard (p10nlYear p10nlBase).amount 551 == 11320
#guard (p10nlYear p10nlBase).amount 1320 == 51820
#guard (p10nlYear p10nlBase).amount 1350 == 51820
#guard (p10nlYear p10nlBase).amount 1351 == 58532
#guard (p10nlYear p10nlDiesel).amount 1320 == 85236
#guard (p10nlYear p10nlBase).amount 3400 == 188968
#guard (p10nlVeh[2]!).amount 2025 { kind := "car", massKg := 1320, fuel := .petrol, firstRegYear := 2021 } == 518
#guard (p10nlVeh[4]!).amount 2025 { kind := "car", massKg := 1320, fuel := .diesel, firstRegYear := 2015 } == 1370
#guard (p10nlVeh[3]!).amount 2025 { kind := "car", massKg := 1320, fuel := .diesel, firstRegYear := 2007 } == 1630
#guard (p10nlVeh[0]!).amount 2025 { kind := "car", massKg := 1800, fuel := .electric, firstRegYear := 2023 } == 213
#guard ((p10nlVeh.filter (·.computes 2025 { kind := "car", massKg := 1320, fuel := .diesel, firstRegYear := 2015 })).head!).multiplierBp == 100
#guard (p10nlVeh.filter (·.selects 2025 { kind := "car", massKg := 1320, fuel := .lpg, firstRegYear := 2015 })).isEmpty

end NlGlobal.Other
