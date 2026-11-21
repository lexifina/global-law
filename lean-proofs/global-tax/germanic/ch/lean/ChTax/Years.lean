import ChTax.Params

/-!
# Tax year 2024 (round 6, improve-continental)

Federal (DBG) amounts for 2024, from the DBG consolidation "Stand am 16. Mai 2024" (fedlex filestore
`.../eli/cc/1991/1184_1184_1184/20240516/de/html/...-de-html-2.html`, `../law/dbg_2024-05-16.txt`), every amount
"Fassung gemäss Art. 4 der V des EFD vom 1. Sept. 2023 über die kalte Progression, in Kraft seit 1. Jan. 2024 (AS
2023 493)":
* Art. 36 Abs. 1: "bis 15 000 Franken Einkommen 0.00 und für je weitere 100 Franken Einkommen 0.77; für 32 800
  Franken Einkommen 137.05 ... 0.88 mehr; für 42 900 ... 225.90 ... 2.64; für 57 200 ... 603.40 ... 2.97; für 75 200
  ... 1138.00 ... 5.94; für 81 000 ... 1482.50 ... 6.60; für 107 400 ... 3224.90 ... 8.80; für 139 600 ... 6058.50 ...
  11.00; für 182 600 ... 10 788.50 ... 13.20; für 783 200 Franken Einkommen 90 067.70 für 783 300 Franken Einkommen
  90 079.50 und für je weitere 100 Franken Einkommen 11.50 mehr."
* Art. 36 Abs. 2: "bis 29 300 ... 0.00 ... 1.00; für 52 700 ... 234.00 ... 2.00; für 60 500 ... 390.00 ... 3.00;
  für 78 100 ... 918.00 ... 4.00; für 93 600 ... 1538.00 ... 5.00; für 107 200 ... 2218.00 ... 6.00; für 119 000
  ... 2926.00 ... 7.00; für 128 800 ... 3612.00 ... 8.00; für 136 600 ... 4236.00 ... 9.00; für 142 300 ... 4749.00
  ... 10.00; für 146 300 ... 5149.00 ... 11.00; für 148 300 ... 5369.00 ... 12.00; für 150 300 ... 5609.00 ...
  13.00; für 928 600 Franken Einkommen 106 788.00 für 928 700 Franken Einkommen 106 800.50 und ... 11.50 mehr."
* Art. 36 Abs. 2bis: "ermässigt sich um 259 Franken für jedes Kind"; Art. 35 Abs. 1 a "6700 Franken für jedes
  minderjährige ... Kind", c "2800 Franken für Ehepaare"; Art. 33 Abs. 1 g "1. 3600 Franken für Ehepaare ... 2. 1800
  Franken für die übrigen", Abs. 1bis b "um 700 Franken für jedes Kind"; Art. 33 Abs. 2 "50 Prozent, jedoch mindestens
  8500 Franken und höchstens 13 900 Franken".
* BVV 2 Art. 5 (Stand 1 Jan 2024, fedlex `.../eli/cc/1984/543_543_543/20240101/...-de-html-4.html`,
  `../law/hist/bvv2_20240101.html`): "Neue Beträge Franken ... 22 050 ... 25 725 ... 88 200 ... 3 675" (in force since
  1 Jan 2023, AS 2022 609).
* FamZG Art. 5 (Stand 1 Jan 2024, `../law/hist/famzg_20240101.html`): "Die Kinderzulage beträgt mindestens 200
  Franken pro Monat. Die Ausbildungszulage beträgt mindestens 250 Franken pro Monat." The EG FamZG ZH version in force
  in 2024 was not obtained: for children aged 12-15 the federal minimum 200 is used and flagged in `unsupported`.
* StG ZH tariff and deductions 2024 = 2025 (the 2025 amounts are the "Fassung gemäss V über den Ausgleich der kalten
  Progression ... ab 1. Januar 2024 vom 28. Juni 2023 (OS 78, 319)", Params.lean); Steuerfüsse 2024 canton 98 % and
  City of Zürich 119 % (ESTV Steuerrechner, TaxYear 2024, TaxLocationID 800100000, `TaxRates`;
  `../refs/hist/estv_probe_2024.json`) = 2025.
* Not obtained for 2024: BVV 3 Art. 7 (Säule 3a caps; the 2025 caps are used, flagged when pension contributions are
  given). AHV/IV/EO 5,3 % and ALV 1,1 % unchanged.
-/

namespace ChTax
open TaxKernel

structure FedYear where
  year : Nat
  single : List TRow
  married : List TRow
  singleSched : Schedule
  marriedSched : Schedule
  childCreditRp : Int
  kidDed : Int
  marriedDed : Int
  insMarried : Int
  insOther : Int
  insPerKid : Int
  twoMin : Int
  twoMax : Int
  bvgEntry : Int
  bvgCoordLo : Int
  bvgCoordHi : Int
  bvgCoordMin : Int
  kzYoung : Int
  kzOld : Int
  az : Int
  /-- Canton of Zürich (round 7): § 35 tariffs, § 34 Kinderabzug, § 31 insurance and two-earner deductions, the
  cantonal Steuerfuss. -/
  zhSingle : Schedule
  zhMarried : Schedule
  zhKid : Int
  zhInsMarried : Int
  zhInsOther : Int
  zhInsPerKid : Int
  zhTwo : Int
  zhCanton : Multiplier
  /-- Säule 3a caps (BVV 3 Art. 7 Abs. 1 a / b), round 8. -/
  p3aWith : Int
  p3aWithout : Int

def fed2025 : FedYear :=
  { year := 2025, single := fedSingleRows, married := fedMarriedRows, singleSched := fedSingleSched,
    marriedSched := fedMarriedSched, childCreditRp := fedChildCreditRp, kidDed := fedKidDeduction,
    marriedDed := fedMarriedDeduction, insMarried := fedInsMarried, insOther := fedInsOther, insPerKid := fedInsPerKid,
    twoMin := fedTwoEarnerMin, twoMax := fedTwoEarnerMax, bvgEntry := bvgEntry, bvgCoordLo := bvgCoordLo,
    bvgCoordHi := bvgCoordHi, bvgCoordMin := bvgCoordMin, kzYoung := kzYoung, kzOld := kzOld, az := azMonthly,
    zhSingle := zhSingle, zhMarried := zhMarried, zhKid := zhKidDeduction, zhInsMarried := zhInsMarried,
    zhInsOther := zhInsOther, zhInsPerKid := zhInsPerKid, zhTwo := zhTwoEarner, zhCanton := zhCantonMult,
    p3aWith := p3aCapWithBvg, p3aWithout := p3aCapWithout }

def fedSingleRows2024 : List TRow :=
  [⟨15000, 0, 77⟩, ⟨32800, 13705, 88⟩, ⟨42900, 22590, 264⟩, ⟨57200, 60340, 297⟩, ⟨75200, 113800, 594⟩,
   ⟨81000, 148250, 660⟩, ⟨107400, 322490, 880⟩, ⟨139600, 605850, 1100⟩, ⟨182600, 1078850, 1320⟩,
   ⟨783300, 9007950, 1150⟩]

def fedMarriedRows2024 : List TRow :=
  [⟨29300, 0, 100⟩, ⟨52700, 23400, 200⟩, ⟨60500, 39000, 300⟩, ⟨78100, 91800, 400⟩, ⟨93600, 153800, 500⟩,
   ⟨107200, 221800, 600⟩, ⟨119000, 292600, 700⟩, ⟨128800, 361200, 800⟩, ⟨136600, 423600, 900⟩,
   ⟨142300, 474900, 1000⟩, ⟨146300, 514900, 1100⟩, ⟨148300, 536900, 1200⟩, ⟨150300, 560900, 1300⟩,
   ⟨928700, 10680050, 1150⟩]

/-- The same tariffs as band sums (the step 783 200-783 300 carries 90 079.50 - 90 067.70 = 11.80; 928 600-928 700
carries 12.50). -/
def fedSingleSched2024 : Schedule :=
  Schedule.ofList [(0, 0), (15000, 77), (32800, 88), (42900, 264), (57200, 297), (75200, 594), (81000, 660),
    (107400, 880), (139600, 1100), (182600, 1320), (783200, 1180), (783300, 1150)]
def fedMarriedSched2024 : Schedule :=
  Schedule.ofList [(0, 0), (29300, 100), (52700, 200), (60500, 300), (78100, 400), (93600, 500), (107200, 600),
    (119000, 700), (128800, 800), (136600, 900), (142300, 1000), (146300, 1100), (148300, 1200), (150300, 1300),
    (928600, 1250), (928700, 1150)]

def fed2024 : FedYear :=
  { fed2025 with
    year := 2024
    single := fedSingleRows2024
    married := fedMarriedRows2024
    singleSched := fedSingleSched2024
    marriedSched := fedMarriedSched2024
    childCreditRp := 25900
    kidDed := 6700
    marriedDed := 2800
    insMarried := 3600
    insOther := 1800
    insPerKid := 700
    twoMin := 8500
    twoMax := 13900
    bvgEntry := 22050
    bvgCoordLo := 25725
    bvgCoordHi := 88200
    bvgCoordMin := 3675
    kzYoung := 200
    kzOld := 250
    az := 250
    p3aWith := 7056
    p3aWithout := 35280 }

/-! ## Tax years 2022 and 2023 (round 7)

* DBG Stand 1 Jan 2022 (fedlex filestore `.../eli/cc/1991/1184_1184_1184/20220101/de/html/...-de-html-7.html`,
  `../law/hist/dbg_20220101.txt`; amounts "Fassung gemäss Art. 2 Abs. 1 der V des EFD vom 2. Sept. 2021 über die kalte
  Progression"): Art. 36 Abs. 1 "bis 14 500 ... 0.77; für 31 600 ... 131.65 ... 0.88; 41 400 ... 217.90 ... 2.64;
  55 200 ... 582.20 ... 2.97; 72 500 ... 1096.00 ... 5.94; 78 100 ... 1428.60 ... 6.60; 103 600 ... 3111.60 ... 8.80;
  134 600 ... 5839.60 ... 11.00; 176 000 ... 10 393.60 ... 13.20; für 755 200 Franken Einkommen 86 848.00 und ...
  11.50"; Abs. 2 "bis 28 300 ... 1.00; 50 900 ... 226 ... 2; 58 400 ... 376 ... 3; 75 300 ... 883 ... 4; 90 300 ...
  1483 ... 5; 103 400 ... 2138 ... 6; 114 700 ... 2816 ... 7; 124 200 ... 3481 ... 8; 131 700 ... 4081 ... 9;
  137 300 ... 4585 ... 10; 141 200 ... 4975 ... 11; 143 100 ... 5184 ... 12; 145 000 ... 5412 ... 13; für 895 800
  ... 103 016.00 für 895 900 ... 103 028.50 und ... 11.50"; Abs. 2bis 251; Art. 35 Abs. 1 a 6500, c 2600; Art. 33
  Abs. 1 g 3500 / 1700, Abs. 1bis b 700; Abs. 2 8100 / 13 400.
* DBG Stand 1 Jan 2023 (`../law/dbg_2023-01-01.txt`; "V des EFD vom 16. Sept. 2022 über die kalte Progression"):
  Abs. 1 "bis 14 800 ... 0.77; 32 200 ... 133.95 ... 0.88; 42 200 ... 221.95 ... 2.64; 56 200 ... 591.55 ... 2.97;
  73 900 ... 1117.20 ... 5.94; 79 600 ... 1455.75 ... 6.60; 105 500 ... 3165.15 ... 8.80; 137 200 ... 5954.75 ...
  11.00; 179 400 ... 10 596.75 ... 13.20; für 769 600 ... 88 503.15 für 769 700 ... 88 515.50 und ... 11.50"; Abs. 2
  "bis 28 800 ... 1.00; 51 800 ... 230 ... 2; 59 400 ... 382 ... 3; 76 700 ... 901 ... 4; 92 000 ... 1513 ... 5;
  105 400 ... 2183 ... 6; 116 900 ... 2873 ... 7; 126 500 ... 3545 ... 8; 134 200 ... 4161 ... 9; 139 900 ... 4674
  ... 10; 143 800 ... 5064 ... 11; 145 800 ... 5284 ... 12; 147 700 ... 5512 ... 13; für 912 600 ... 104 949.00 und
  ... 11.50"; Abs. 2bis 255; Art. 35 6600 / 2700; Art. 33 3600 / 1800 / 700; 8300 / 13 600.
* BVV 2 Art. 5 (`../law/hist/bvv2_20240101.html`): "Bisherige Beträge 21 510 ... 25 095 ... 86 040 ... 3 585" (2022),
  "Neue Beträge 22 050 ... 25 725 ... 88 200 ... 3 675" in force since 1 Jan 2023 (AS 2022 609).
* FamZG Art. 5 minima 200 / 250 (`../law/hist/famzg_20240101.html`), the same wording 2022-2024; Zürich's own rate for
  ages 12-15 not sourced (federal minimum, flagged).
* StG ZH Nachtrag 115 (published 1 Jan 2022, repealed 1 Jul 2023) and Nachtrag 121 (1 Jul 2023 - 1 Jan 2024), zhlex
  (notes.zh.ch WebView PDFs saved in `../law/hist/zh/`): the same amounts in §§ 31-35 (compared line by line): § 35 Abs. 1
  "0% für die ersten Fr. 6 700, 2% ... 4 700, 3% ... 4 700, 4% ... 7 600, 5% ... 9 300, 6% ... 10 700, 7% ... 12 400,
  8% ... 16 900, 9% ... 32 500, 10% ... 32 200, 11% ... 51 000, 12% ... 66 200, 13% für Einkommensteile über Fr.
  254 900"; Abs. 2 "13 500, 6 100, 7 700, 9 400, 10 700, 13 900, 30 800, 30 800, 46 400, 55 400, 60 100, 69 300, über
  Fr. 354 100"; § 34 Kinderabzug "je Fr. 9000"; § 31 "Fr. 5200 ... Fr. 2600 ... Fr. 1300 für jedes Kind", Abs. 2
  "Fr. 5900"; § 200 Personalsteuer Fr. 24. Nachtrag 123 (in force 2024) has the same amounts as Nachtrag 127 (2025).
* Steuerfuss: canton 99 % in 2022 and 2023, City of Zürich 119 % (ESTV Steuerrechner TaxRates, TaxYear 2022 / 2023,
  `../refs/hist/estv_probe_2022.json`, `_2023.json`).
* Berufskostenverordnung Anhang (3 %, 2 000 - 4 000): the consolidation of 1 Jan 2023 (`../law/berufskostenv_2023-01-01`),
  wording "Fassung gemäss ... V des EFD vom 6. März 2015, in Kraft seit 1. Jan. 2016": unchanged 2022-2025.
-/

def zhSingle2022 : Schedule :=
  Schedule.ofList [(0, 0), (6700, 200), (11400, 300), (16100, 400), (23700, 500), (33000, 600), (43700, 700),
    (56100, 800), (73000, 900), (105500, 1000), (137700, 1100), (188700, 1200), (254900, 1300)]
def zhMarried2022 : Schedule :=
  Schedule.ofList [(0, 0), (13500, 200), (19600, 300), (27300, 400), (36700, 500), (47400, 600), (61300, 700),
    (92100, 800), (122900, 900), (169300, 1000), (224700, 1100), (284800, 1200), (354100, 1300)]

def fed2023 : FedYear :=
  { fed2024 with
    year := 2023
    single := [⟨14800, 0, 77⟩, ⟨32200, 13395, 88⟩, ⟨42200, 22195, 264⟩, ⟨56200, 59155, 297⟩, ⟨73900, 111720, 594⟩,
      ⟨79600, 145575, 660⟩, ⟨105500, 316515, 880⟩, ⟨137200, 595475, 1100⟩, ⟨179400, 1059675, 1320⟩,
      ⟨769700, 8851550, 1150⟩]
    married := [⟨28800, 0, 100⟩, ⟨51800, 23000, 200⟩, ⟨59400, 38200, 300⟩, ⟨76700, 90100, 400⟩, ⟨92000, 151300, 500⟩,
      ⟨105400, 218300, 600⟩, ⟨116900, 287300, 700⟩, ⟨126500, 354500, 800⟩, ⟨134200, 416100, 900⟩,
      ⟨139900, 467400, 1000⟩, ⟨143800, 506400, 1100⟩, ⟨145800, 528400, 1200⟩, ⟨147700, 551200, 1300⟩,
      ⟨912600, 10494900, 1150⟩]
    singleSched := Schedule.ofList [(0, 0), (14800, 77), (32200, 88), (42200, 264), (56200, 297), (73900, 594),
      (79600, 660), (105500, 880), (137200, 1100), (179400, 1320), (769600, 1235), (769700, 1150)]
    marriedSched := Schedule.ofList [(0, 0), (28800, 100), (51800, 200), (59400, 300), (76700, 400), (92000, 500),
      (105400, 600), (116900, 700), (126500, 800), (134200, 900), (139900, 1000), (143800, 1100), (145800, 1200),
      (147700, 1300), (912600, 1150)]
    childCreditRp := 25500
    kidDed := 6600
    marriedDed := 2700
    insMarried := 3600
    insOther := 1800
    insPerKid := 700
    twoMin := 8300
    twoMax := 13600
    zhSingle := zhSingle2022
    zhMarried := zhMarried2022
    zhKid := 9000
    zhInsMarried := 5200
    zhInsOther := 2600
    zhInsPerKid := 1300
    zhTwo := 5900
    zhCanton := { name := "cantonZH", rate := 9900 } }

def fed2022 : FedYear :=
  { fed2023 with
    year := 2022
    single := [⟨14500, 0, 77⟩, ⟨31600, 13165, 88⟩, ⟨41400, 21790, 264⟩, ⟨55200, 58220, 297⟩, ⟨72500, 109600, 594⟩,
      ⟨78100, 142860, 660⟩, ⟨103600, 311160, 880⟩, ⟨134600, 583960, 1100⟩, ⟨176000, 1039360, 1320⟩,
      ⟨755200, 8684800, 1150⟩]
    married := [⟨28300, 0, 100⟩, ⟨50900, 22600, 200⟩, ⟨58400, 37600, 300⟩, ⟨75300, 88300, 400⟩, ⟨90300, 148300, 500⟩,
      ⟨103400, 213800, 600⟩, ⟨114700, 281600, 700⟩, ⟨124200, 348100, 800⟩, ⟨131700, 408100, 900⟩,
      ⟨137300, 458500, 1000⟩, ⟨141200, 497500, 1100⟩, ⟨143100, 518400, 1200⟩, ⟨145000, 541200, 1300⟩,
      ⟨895900, 10302850, 1150⟩]
    singleSched := Schedule.ofList [(0, 0), (14500, 77), (31600, 88), (41400, 264), (55200, 297), (72500, 594),
      (78100, 660), (103600, 880), (134600, 1100), (176000, 1320), (755200, 1150)]
    marriedSched := Schedule.ofList [(0, 0), (28300, 100), (50900, 200), (58400, 300), (75300, 400), (90300, 500),
      (103400, 600), (114700, 700), (124200, 800), (131700, 900), (137300, 1000), (141200, 1100), (143100, 1200),
      (145000, 1300), (895800, 1250), (895900, 1150)]
    childCreditRp := 25100
    kidDed := 6500
    marriedDed := 2600
    insMarried := 3500
    insOther := 1700
    twoMin := 8100
    twoMax := 13400
    bvgEntry := 21510
    bvgCoordLo := 25095
    bvgCoordHi := 86040
    bvgCoordMin := 3585
    p3aWith := 6883
    p3aWithout := 34416 }

/-! ## Round 8: family allowances 2022-2024 and Säule 3a caps 2022-2024

* EG FamZG ZH (LS 836.1) Nachtrag 111, in force 1 Jan 2021 - 1 Jan 2025 (zhlex version list
  `erlass-836_1-2009_01_19-2009_07_01-111.html`; PDF `../law/hist/zh/egfamzg_111.pdf`), § 4 Abs. 1: "Die Mindesthöhe
  der Kinderzulage beträgt monatlich Fr. 200 bis zum Ende des Monates, in welchem das Kind das zwölfte Altersjahr
  vollendet, danach monatlich Fr. 250." Abs. 2: Ausbildungszulage "monatlich Fr. 250". So 2022-2024: 200 / 250 / 250
  (`kzYoung`, `kzOld`, `az`; the round-6 federal-minimum stand-in for ages 12-15 is replaced).
* BVV 3 Art. 7 Abs. 1 (`../law/bvv3_2025-01-01.txt`): "a. jährlich bis 8 Prozent des oberen Grenzbetrages nach Artikel 8
  Absatz 1 BVG ...; b. jährlich bis 20 Prozent des Erwerbseinkommens, jedoch höchstens bis 40 Prozent des oberen
  Grenzbetrages". With the year's oberer Grenzbetrag (BVV 2 Art. 5: 86 040 in 2022, 88 200 in 2023-2024, 90 720 in 2025)
  and rounding to the franc as for 2025 (8 % x 90 720 = 7 257.60 -> 7 258, the model's cited value): 2022 6 883 / 34 416,
  2023-2024 7 056 / 35 280.
-/
#guard (8 * 90720 + 50) / 100 = p3aCapWithBvg && 40 * 90720 / 100 = p3aCapWithout
#guard (8 * 88200 + 50) / 100 = 7056 && 40 * 88200 / 100 = 35280
#guard (8 * 86040 + 50) / 100 = 6883 && 40 * 86040 / 100 = 34416

def fedFor (y : Nat) : FedYear :=
  if y = 2022 then fed2022 else if y = 2023 then fed2023 else if y = 2024 then fed2024 else fed2025
def yearSupported (y : Nat) : Bool := 2022 ≤ y && y ≤ 2025

#guard (fed2023.single.zip fed2023.single.tail).all fun (a, b) =>
  b.lo = 769700 || (a.baseRp + (b.lo - a.lo) / 100 * a.per100Rp - b.baseRp).natAbs ≤ 5
#guard (fed2022.married.zip fed2022.married.tail).all fun (a, b) =>
  b.lo = 895900 || (a.baseRp + (b.lo - a.lo) / 100 * a.per100Rp - b.baseRp).natAbs ≤ 5

-- the printed rows continue each other to within 5 Rappen (the printed amounts are rounded: 15 000 -> 32 800 runs to
-- 137.06, printed 137.05; the printed amounts are the law and are used as printed)
#guard fedSingleRows2024.zip fedSingleRows2024.tail |>.all fun (a, b) =>
  b.lo = 783300 || (a.baseRp + (b.lo - a.lo) / 100 * a.per100Rp - b.baseRp).natAbs ≤ 5
#guard fedMarriedRows2024.zip fedMarriedRows2024.tail |>.all fun (a, b) =>
  b.lo = 928700 || (a.baseRp + (b.lo - a.lo) / 100 * a.per100Rp - b.baseRp).natAbs ≤ 5

end ChTax
