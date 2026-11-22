import RoGlobal.Pit
import TaxKernel.Global2

/-!
# RO 2025: Other family not reached (grade C)

* 5200 Taxes on use of goods (motor vehicle taxes) (the country's motor-vehicle tax act): tried not read in the P7 pass; would unlock: the vehicle tax act and the 2025 rates (no vehicle field in the canonical entity: an asset of kind vehicle with an annual value would carry it)
* 6000 Other taxes (none recorded by the registry): tried registry row: no other notable tax; no provision read; would unlock: a statement in the statute or the tax authority's list of taxes for 2025

* **5200 triage (pass 7)**: blocked: the canonical input has no vehicle attributes (CO2, engine kW / cm3, mass, fuel, first registration); kernel request filed (R1 Europe pass 7); national vs municipal frame to be recorded with the act

* **6000 triage (pass 7)**: minor: no other national tax recorded by the registry; to confirm against the country's list of taxes


## 5200 Impozitul pe mijloacele de transport (pass 11, kernel 2.4.0, grade A)
Source: Codul fiscal, Legea nr. 227/2015, forma consolidată, legislatie.just.ro DetaliiDocument/171282 via the Internet Archive 2025-05-02 (`ro/law/cf_wb20250502.txt`).
* art. 470 (2): for motorcycles, cars, buses and other motor vehicles up to 12 t the tax is each group of 200 cmc or fraction of it times the row's amount: cars up to 1.600 cmc 8 lei, 1.601-2.000 cmc 18, 2.001-2.600 cmc 72, 2.601-3.000 cmc 144, above 3.000 cmc 290; motorcycles up to 1.600 cmc 8, above 9
* art. 470 (3): for hybrids the tax is reduced by at least 50 %, by decision of the local council: the model applies 50 %
* art. 469 (1) n): electrically driven motor vehicles are not taxed (a fuel-cell car is read as electrically driven)
* art. 491 (1): every amount in lei is indexed yearly by the local council for the previous year's inflation; art. 489: the council may add quotas: neither is applied (the statute's amounts are booked)

* **6000 not levied (cited, gap pass, grade B)**: European Commission TEDB, RO: list of the taxes in force on 1.7.2025 (types other direct and other indirect; taxIds 497, 801, 806, 884, 3301, 494, 1301) read against the OECD Revenue Statistics Interpretative Guide (Revenue Statistics 2021 edition, Internet Archive 2022-12-15, `tools/in_gap/oecd_interpretative_guide_wb20221215.pdf`) § 85 (6000: taxes on bases other than those of headings 1000-5000): none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: taxes on buildings and land 4100; tax on means of transport 5200; non-residents' income tax 1100 / 1200; environmental stamp 5200 (§ 83); judicial stamp fee: a court fee, non-tax (§ 14); tax on domestic crude oil and gas production 5128 (TEDB searches for the situation on 1.7.2025 (held as `tools/in_gap/tedb/search_*`))
-/

namespace RoGlobal.Other
open TaxKernel TaxKernel.Global

/-- guards: the amount of the first tax of `ts` that computes vehicle `v` in 2025 (-1: none computes it) -/
def p11amt (ts : List VehicleTax) (v : Vehicle) : Int :=
  match ts.find? (·.computes 2025 v) with
  | some t => t.amount 2025 v
  | none => -1

/-- Codul fiscal art. 470 alin. (2): lei for each group of 200 cmc or fraction of it, at the rate of the vehicle's row -/
def p11roCcm (r : Int) : QtyTable := QtyTable.perUnit r 200 (step := 200)
def p11roRow (k : String) (fs : List VehicleFuel) (lo hi r bp : Int) (st : String) : VehicleTax :=
  { name := "Impozitul pe mijloacele de transport", kinds := [k], fuels := fs, «when» := [(.engineCcm, lo, hi)],   parts := [(.engineCcm, p11roCcm r)], multiplierBp := bp, level := .local, statute := st }
def p11roIce : List VehicleFuel := [.petrol, .diesel, .lpg, .cng, .other]
def p11roHyb : List VehicleFuel := [.hybrid, .pluginHybrid]
def p11roCars (fs : List VehicleFuel) (bp : Int) (sfx : String) : List VehicleTax :=
  [p11roRow "car" fs (-1) 1600 8 bp s!"Codul fiscal art. 470 alin. (2) pct. I.1: autoturisme până la 1.600 cmc, 8 lei/200 cmc{sfx}",  p11roRow "car" fs 1600 2000 18 bp s!"Codul fiscal art. 470 alin. (2) pct. I.3: autoturisme 1.601-2.000 cmc, 18 lei/200 cmc{sfx}",  p11roRow "car" fs 2000 2600 72 bp s!"Codul fiscal art. 470 alin. (2) pct. I.4: autoturisme 2.001-2.600 cmc, 72 lei/200 cmc{sfx}",  p11roRow "car" fs 2600 3000 144 bp s!"Codul fiscal art. 470 alin. (2) pct. I.5: autoturisme 2.601-3.000 cmc, 144 lei/200 cmc{sfx}",  p11roRow "car" fs 3000 VehicleTax.noBound 290 bp s!"Codul fiscal art. 470 alin. (2) pct. I.6: autoturisme peste 3.000 cmc, 290 lei/200 cmc{sfx}"]
def p11roVeh : List VehicleTax :=
  [{ name := "Impozitul pe mijloacele de transport", kinds := ["car", "motorcycle"], fuels := [.electric, .hydrogen], level := .local,    statute := "Codul fiscal art. 469 alin. (1) lit. n): autovehiculele acționate electric are not taxed" }]
  ++ p11roCars p11roIce 10000 ""
  ++ p11roCars p11roHyb 5000 "; art. 470 alin. (3): hibride, reduced by 50 % (the statutory minimum reduction)"
  ++ [p11roRow "motorcycle" (p11roIce ++ p11roHyb) (-1) 1600 8 10000 "Codul fiscal art. 470 alin. (2) pct. I.1: motociclete până la 1.600 cmc, 8 lei/200 cmc",     p11roRow "motorcycle" (p11roIce ++ p11roHyb) 1600 VehicleTax.noBound 9 10000 "Codul fiscal art. 470 alin. (2) pct. I.2: motociclete peste 1.600 cmc, 9 lei/200 cmc"]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5200 Impozitul pe mijloacele de transport (pass 11)", covers := [.useOfGoods],
     run := fun args g prev =>
       vehicleTaxCharges p11roVeh g (firstOnly := true) }]

def absent : List Absent :=
  [{ oecd := .other, why := "none of the taxes the TEDB lists for 2025 is levied on a base outside headings 1000-5000: taxes on buildings and land 4100; tax on means of transport 5200; non-residents' income tax 1100 / 1200; environmental stamp 5200 (§ 83); judicial stamp fee: a court fee, non-tax (§ 14); tax on domestic crude oil and gas production 5128" }]

def notes : List String := ["RO 5200 Impozitul pe mijloacele de transport pass 11: legislatie.just.ro via the Internet Archive, 2025-05-02 (`ro/law/cf_wb20250502.txt`; unchanged in the 2025-11-25 capture) (grade A)", "RO 6000 gap pass: not levied (cited, B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !(vehicleTaxUnknown "Impozitul pe mijloacele de transport" p11roVeh g).isEmpty then ["5200 Impozitul pe mijloacele de transport: a vehicle lacks an attribute the rate needs (grade C)"] else [])
  ++ (if !(vehicleTaxUnmatched "Impozitul pe mijloacele de transport" p11roVeh g).isEmpty then ["5200 Impozitul pe mijloacele de transport: a vehicle no rule reaches: buses, lorries (art. 470 (2) I.7-I.9, (5)-(7) by axles and mass), trailers, other kinds (grade C)"] else [])
  ++ (if !g.vehicles.isEmpty then ["5200 impozitul pe mijloacele de transport: the statute's amounts of art. 470 (2) are booked without the Bucharest council's 2025 indexation (art. 491) and additional quotas (art. 489) (grade C for the local part)"] else [])
  ++ (if g.vehicles.any (fun v => v.months < 12) then ["5200 impozitul pe mijloacele de transport: the tax is owed for the whole year by the owner at 31 December of the previous year (a vehicle acquired in the year from the next 1 January); the model prorates by months held"] else [])

#guard p11amt p11roVeh { kind := "car", fuel := .petrol, engineCcm := 1598, firstRegYear := 2019 } == 64
#guard p11amt p11roVeh { kind := "car", fuel := .diesel, engineCcm := 1968, firstRegYear := 2019 } == 180
#guard p11amt p11roVeh { kind := "car", fuel := .petrol, engineCcm := 1600, firstRegYear := 2019 } == 64
#guard p11amt p11roVeh { kind := "car", fuel := .petrol, engineCcm := 1601, firstRegYear := 2019 } == 162
#guard p11amt p11roVeh { kind := "car", fuel := .petrol, engineCcm := 2001, firstRegYear := 2019 } == 792
#guard p11amt p11roVeh { kind := "car", fuel := .diesel, engineCcm := 3000, firstRegYear := 2019 } == 2160
#guard p11amt p11roVeh { kind := "car", fuel := .petrol, engineCcm := 3001, firstRegYear := 2019 } == 4640
#guard p11amt p11roVeh { kind := "car", fuel := .hybrid, engineCcm := 1798, firstRegYear := 2019 } == 81
#guard p11amt p11roVeh { kind := "car", fuel := .electric, firstRegYear := 2023 } == 0
#guard p11amt p11roVeh { kind := "motorcycle", fuel := .petrol, engineCcm := 1800, firstRegYear := 2020 } == 81
#guard p11amt p11roVeh { kind := "truck", fuel := .diesel, engineCcm := 7000, firstRegYear := 2020 } == -1

end RoGlobal.Other
