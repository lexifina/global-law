import TaxKernel

/-!
# Switzerland 2025: every parameter with its source

Texts read (kept in `~/cmp20/germanic/ch/law/`):
* DBG (SR 642.11), Fedlex consolidation in force 1 Jan 2025 (`dbg_20250101.html`, filestore
  `.../eli/cc/1991/1184_1184_1184/20250101/de/html/...-de-html-16.html`); the 2025 amounts are the
  "Fassung gemäss V des EFD vom 22. Aug. 2024 über die kalte Progression, in Kraft seit 1. Jan. 2025 (AS 2024 479)".
* StG ZH (LS 631.1), zhlex Nachtrag 127 (pages dated "1. 1. 25 - 127"; `stgzh_127.pdf`); the amounts are the
  "Fassung gemäss V über den Ausgleich der kalten Progression ... ab 1. Januar 2024 vom 28. Juni 2023 (OS 78, 319)",
  unchanged until Nachtrag 131 (1 Jan 2026).
* Berufskostenverordnung (SR 642.118.1) Anhang, consolidation 1 Jan 2023 (still in force 2025).
* AHVG, IVG, EOG, AVIG, UVV, BVG, BVV 2, BVV 3, AHVV, FamZG: Fedlex consolidations in force mid-2025.
* EG FamZG ZH (LS 836.1), Nachtrag 127 (1 Jan 2025).
* Steuerfüsse 2025 (Kanton 98 %, Stadt Zürich 119 %, Kirchen 10 %): ESTV Steuerrechner, `TaxRates` of a 2025
  calculation for TaxLocationID 800100000 (Zürich 8001), fetched 2026-11-19 (`refs/estv_probe1.json`), and the
  OECD's Taxing Wages 2025 lines (217 % = 98 + 119 reproduces SLT to the Rappen).
Money: francs (`Int`); taxes in Rappen (Rp) where the statute prints Rappen; rates in basis points.
-/

namespace ChTax
open TaxKernel

/-! ## Federal: DBG -/

/-- A row of a DBG Art. 36 tariff as printed: "für `lo` Franken Einkommen `base` und für je weitere 100 Franken
Einkommen `per100` mehr" (amounts in Rappen). -/
structure TRow where
  lo : Int
  baseRp : Int
  per100Rp : Int
  deriving Repr, DecidableEq

/-- DBG Art. 36 Abs. 1 (Grundtarif, 2025): "bis 15 200 Franken Einkommen 0.00 und für je weitere 100 Franken
Einkommen 0.77; für 33 200 Franken Einkommen 138.60 ... 0.88 mehr; für 43 500 ... 229.20 ... 2.64; für 58 000 ...
612.00 ... 2.97; für 76 100 ... 1 149.55 ... 5.94; für 82 000 ... 1 500.00 ... 6.60; für 108 800 ... 3 268.80 ...
8.80; für 141 500 ... 6 146.40 ... 11.00; für 184 900 ... 10 920.40 ... 13.20; für 793 300 Franken Einkommen
91 229.20; für 793 400 Franken Einkommen 91 241.00 und für je weitere 100 Franken Einkommen 11.50 mehr." -/
def fedSingleRows : List TRow :=
  [⟨15200, 0, 77⟩, ⟨33200, 13860, 88⟩, ⟨43500, 22920, 264⟩, ⟨58000, 61200, 297⟩, ⟨76100, 114955, 594⟩,
   ⟨82000, 150000, 660⟩, ⟨108800, 326880, 880⟩, ⟨141500, 614640, 1100⟩, ⟨184900, 1092040, 1320⟩,
   ⟨793400, 9124100, 1150⟩]

/-- DBG Art. 36 Abs. 2 (Verheiratetentarif, 2025): "bis 29 700 Franken Einkommen 0.00 und für je weitere 100
Franken Einkommen 1.00; für 53 400 ... 237.00 ... 2.00 mehr; ... für 152 300 ... 5 686.00 ... 13.00; für 940 800
Franken Einkommen 108 191.00; für 940 900 Franken Einkommen 108 203.50 und für je weitere 100 Franken Einkommen
11.50 mehr." -/
def fedMarriedRows : List TRow :=
  [⟨29700, 0, 100⟩, ⟨53400, 23700, 200⟩, ⟨61300, 39500, 300⟩, ⟨79100, 92900, 400⟩, ⟨94900, 156100, 500⟩,
   ⟨108600, 224600, 600⟩, ⟨120500, 296000, 700⟩, ⟨130500, 366000, 800⟩, ⟨138300, 428400, 900⟩,
   ⟨144200, 481500, 1000⟩, ⟨148200, 521500, 1100⟩, ⟨150300, 544600, 1200⟩, ⟨152300, 568600, 1300⟩,
   ⟨940900, 10820350, 1150⟩]

/-- The same Grundtarif as a band sum (kernel `Schedule`, rate per franc in bp = Rappen per 100 francs); the
band 793 300-793 400 carries the printed step 91 241.00 - 91 229.20 = 11.80. The OECD computes this way. -/
def fedSingleSched : Schedule :=
  Schedule.ofList [(0, 0), (15200, 77), (33200, 88), (43500, 264), (58000, 297), (76100, 594), (82000, 660),
    (108800, 880), (141500, 1100), (184900, 1320), (793300, 1180), (793400, 1150)]

/-- The Verheiratetentarif as a band sum (step 940 800-940 900: 108 203.50 - 108 191.00 = 12.50). -/
def fedMarriedSched : Schedule :=
  Schedule.ofList [(0, 0), (29700, 100), (53400, 200), (61300, 300), (79100, 400), (94900, 500), (108600, 600),
    (120500, 700), (130500, 800), (138300, 900), (144200, 1000), (148200, 1100), (150300, 1200), (152300, 1300),
    (940800, 1250), (940900, 1150)]

/-- DBG Art. 36 Abs. 2bis: "Der so ermittelte Steuerbetrag ermässigt sich um 263 Franken für jedes Kind". -/
def fedChildCreditRp : Int := 26300
/-- DBG Art. 36 Abs. 3: "Steuerbeträge unter 25 Franken werden nicht erhoben." -/
def fedMinTaxRp : Int := 2500
/-- DBG Art. 35 Abs. 1 lit. a: "6800 Franken für jedes minderjährige oder in der beruflichen oder schulischen
Ausbildung stehende Kind". -/
def fedKidDeduction : Int := 6800
/-- DBG Art. 35 Abs. 1 lit. c: "2800 Franken für Ehepaare, die in rechtlich und tatsächlich ungetrennter Ehe
leben". -/
def fedMarriedDeduction : Int := 2800
/-- DBG Art. 33 Abs. 1 lit. g Ziff. 1/2: "3700 Franken für Ehepaare ... 1800 Franken für die übrigen". -/
def fedInsMarried : Int := 3700
def fedInsOther : Int := 1800
/-- DBG Art. 33 Abs. 1bis lit. b: "um 700 Franken für jedes Kind". -/
def fedInsPerKid : Int := 700
/-- DBG Art. 33 Abs. 2: "vom niedrigeren Erwerbseinkommen 50 Prozent, jedoch mindestens 8600 Franken und
höchstens 14 100 Franken abgezogen". -/
def fedTwoEarnerMin : Int := 8600
def fedTwoEarnerMax : Int := 14100
/-- DBG Art. 20 Abs. 1bis: qualifying dividends "sind im Umfang von 70 Prozent steuerbar" (participation of at
least 10 %). -/
def fedQualDivBp : Int := 7000
/-- DBG Art. 38 Abs. 2: capital benefits from pensions taxed "zu einem Fünftel der Tarife nach Artikel 36". -/
def fedCapitalDivisor : Int := 5

/-- Berufskostenverordnung (SR 642.118.1) Anhang Ziff. 1, "Übrige Berufskosten (Art. 7 Abs. 1): 3 % des
Nettolohns, mindestens im Jahr 2000.—, höchstens im Jahr 4000.—" (also applied by the ESTV calculator for ZH). -/
def berufBp : Int := 300
def berufMin : Int := 2000
def berufMax : Int := 4000

/-! ## Canton of Zürich: StG ZH (LS 631.1), Nachtrag 127 -/

/-- StG ZH § 35 Abs. 1 (Grundtarif): "0% für die ersten Fr. 6 900, 2% für die weiteren Fr. 4 900, 3% ... 4 800,
4% ... 7 900, 5% ... 9 600, 6% ... 11 000, 7% ... 12 900, 8% ... 17 400, 9% ... 33 600, 10% ... 33 200,
11% ... 52 700, 12% ... 68 400, 13% für Einkommensteile über Fr. 263 300". -/
def zhSingle : Schedule :=
  Schedule.ofList [(0, 0), (6900, 200), (11800, 300), (16600, 400), (24500, 500), (34100, 600), (45100, 700),
    (58000, 800), (75400, 900), (109000, 1000), (142200, 1100), (194900, 1200), (263300, 1300)]

/-- StG ZH § 35 Abs. 2 (Verheiratetentarif, also for single parents living with children): "0% für die ersten
Fr. 13 900, 2% ... 6 300, 3% ... 8 000, 4% ... 9 700, 5% ... 11 100, 6% ... 14 300, 7% ... 31 800, 8% ... 31 900,
9% ... 47 900, 10% ... 57 200, 11% ... 62 100, 12% ... 71 600, 13% für Einkommensteile über Fr. 365 800". -/
def zhMarried : Schedule :=
  Schedule.ofList [(0, 0), (13900, 200), (20200, 300), (28200, 400), (37900, 500), (49000, 600), (63300, 700),
    (95100, 800), (127000, 900), (174900, 1000), (232100, 1100), (294200, 1200), (365800, 1300)]

/-- StG ZH § 34 Abs. 1 lit. a: Kinderabzug "je Fr. 9300". -/
def zhKidDeduction : Int := 9300
/-- StG ZH § 31 Abs. 1 lit. g: "Fr. 5800 für in ungetrennter Ehe lebende Steuerpflichtige und von Fr. 2900 für die
übrigen ... erhöhen sich diese Abzüge um Fr. 1300 für jedes Kind". -/
def zhInsMarried : Int := 5800
def zhInsOther : Int := 2900
def zhInsPerKid : Int := 1300
/-- StG ZH § 31 Abs. 2: "vom Erwerbseinkommen, das ein Ehegatte unabhängig von Beruf, Geschäft oder Gewerbe des
anderen Ehegatten erzielt, Fr. 6100 abgezogen". -/
def zhTwoEarner : Int := 6100
/-- StG ZH § 20 Abs. 1bis: qualifying dividends "sind im Umfang von 50 Prozent steuerbar". -/
def zhQualDivBp : Int := 5000
/-- StG ZH § 37 Abs. 1: capital benefits at the rate of "einem Zwanzigstel der Kapitalleistung"; "die einfache
Staatssteuer beträgt jedoch mindestens 2 Prozent". -/
def zhCapitalDivisor : Int := 20
def zhCapitalMinBp : Int := 200
/-- StG ZH § 200: "Die Personalsteuer beträgt Fr. 24." (§ 199 Abs. 2: "Ehegatten schulden je die volle
Personalsteuer"; Abs. 3: from the year of majority.) -/
def zhPersonalTax : Int := 24

/-- Steuerfüsse 2025 (StG ZH § 2 Abs. 2: "Der Kantonsrat setzt ... den Steuerfuss in Prozenten der einfachen
Staatssteuer fest"): canton 98 %, City of Zürich 119 %, reformed and Roman Catholic church 10 % each
(ESTV Steuerrechner 2025, TaxRates IncomeRateCanton 98, IncomeRateCity 119, IncomeRateProtestant 10,
IncomeRateRoman 10; the canton's 98 % is also what the OECD's 2025 SLT implies). -/
def zhCantonMult : Multiplier := { name := "cantonZH", rate := 9800 }
def zhCityMult : Multiplier := { name := "cityZurich", rate := 11900 }
def zhChurchReformedMult : Multiplier := { name := "churchReformed", rate := 1000 }
def zhChurchCatholicMult : Multiplier := { name := "churchCatholic", rate := 1000 }

/-! ## Social insurance (employee side) -/

/-- AHV/IV/EO employee share 5.3 % (AHVG Art. 5 Abs. 1 "4,35 Prozent"; IVG Art. 3 Abs. 1 "1,4 Prozent" split
equally, Art. 3 Abs. 1bis; EOG Art. 27 Abs. 2 at most 0.5 % split equally) = 4.35 + 0.70 + 0.25. -/
def ahvEmployeeBp : Int := 530
/-- AHVV Art. 6quater Abs. 1: after the reference age "nur für den Teil ... der ... den Freibetrag von 16 800
Franken im Jahr übersteigt". Reference age 65 (AHVG Art. 21 Abs. 1). -/
def ahvRetireeFree : Int := 16800
def referenceAge : Nat := 65
/-- Self-employed: AHVG Art. 8 Abs. 1 "8,1 Prozent" (income "auf die nächsten 100 Franken abgerundet"), IVG Art. 3
Abs. 1 "1,4 Prozent", EOG Art. 27 Abs. 2 0.5 %: 10.0 % in all above 60 500. -/
def ahvSelfBp : Int := 810
def ivEoSelfBp : Int := 190
/-- AHVV Art. 21 Abs. 1, sinkende Beitragsskala (AHV part, bp) for 10 100 ≤ income < 60 500. -/
def ahvSelfScale : List (Int × Int) :=
  [(10100, 435), (17600, 445), (23000, 455), (25500, 465), (28000, 475), (30500, 485), (33000, 505),
   (35500, 525), (38000, 545), (40500, 565), (43000, 585), (45500, 605), (48000, 635), (50500, 665),
   (53000, 695), (55500, 725), (58000, 755), (60500, 810)]
/-- AVIG Art. 3 Abs. 2-3: "Bis zum ... Höchstbetrag des versicherten Verdienstes der obligatorischen
Unfallversicherung beträgt der Beitragssatz 2,2 Prozent"; "Arbeitgeber und Arbeitnehmer tragen den Beitrag je zur
Hälfte". UVV Art. 22 Abs. 1: "Der Höchstbetrag des versicherten Verdienstes beläuft sich auf 148 200 Franken". -/
def alvEmployeeBp : Int := 110
def uvgMaxInsured : Int := 148200

/-- BVG Art. 7 Abs. 1 (entry threshold "mehr als 22 680 Franken"), Art. 8 Abs. 1 ("der Teil des Jahreslohnes von
26 460 bis und mit 90 720 Franken"), BVV 2 Art. 5 / Art. 8 Abs. 2 minimum coordinated wage ("mindestens 3780
Franken"), Art. 16 credits (25-34: 7, 35-44: 10, 45-54: 15, 55-65: 18 % of the coordinated wage). The employee
pays half (Art. 66 Abs. 1: the employer pays at least as much as all employees together). -/
def bvgEntry : Int := 22680
def bvgCoordLo : Int := 26460
def bvgCoordHi : Int := 90720
def bvgCoordMin : Int := 3780
def bvgCreditBp (age : Nat) : Int :=
  if age < 25 then 0 else if age < 35 then 700 else if age < 45 then 1000 else if age < 55 then 1500
  else if age < 65 then 1800 else 0
/-- OECD Taxing Wages convention for the employee's occupational pension contribution (not a statute): 7.83 % of
the wage above 26 460, uncapped (reproduces the OECD's 2025 DSSCIT − EECSSC for S67, S100 and S167 to 1e-10). -/
def oecdBvgBp : Int := 783

/-- BVV 3 Art. 7 Abs. 1 lit. a: Säule 3a "bis 8 Prozent des oberen Grenzbetrages nach Artikel 8 Absatz 1 BVG"
= 8 % × 90 720 = 7 257.60, published as 7 258; lit. b without a pension fund "bis 20 Prozent des
Erwerbseinkommens, jedoch höchstens bis 40 Prozent des oberen Grenzbetrages" = 36 288. -/
def p3aCapWithBvg : Int := 7258
def p3aCapWithout : Int := 36288

/-! ## Family allowances (cash benefits) -/

/-- FamZG Art. 5 Abs. 1-2 (minimum 215 Kinderzulage, 268 Ausbildungszulage per month) and EG FamZG ZH § 4 Abs. 1-2:
"Die Mindesthöhe der Kinderzulage beträgt monatlich Fr. 215 bis zum Ende des Monates, in welchem das Kind das zwölfte
Altersjahr vollendet, danach monatlich Fr. 268"; "Die Mindesthöhe der Ausbildungszulage beträgt monatlich Fr. 268".
Kinderzulage up to 16 (FamZG Art. 3 Abs. 1 lit. a), Ausbildungszulage 16-25 (lit. b; assumed in education). -/
def kzYoung : Int := 215
def kzOld : Int := 268
def azMonthly : Int := 268
/-- FamZG Art. 13 Abs. 3: entitled who pays AHV contributions on an annual income "mindestens dem halben jährlichen
Betrag der minimalen vollen Altersrente der AHV" (2025: 1 260 × 12 / 2 = 7 560). -/
def famzgMinIncome : Int := 7560
/-- FamZG Art. 19 Abs. 1bis-2: earners below that minimum count as non-employed; they get the allowances only if
"das steuerbare Einkommen den anderthalbfachen Betrag einer maximalen vollen Altersrente der AHV nicht übersteigt"
(maximum full pension = twice the minimum, AHVG Art. 34 Abs. 3: 2 × 1 260 × 12 = 30 240; × 1.5 = 45 360). -/
def famzgNonEarnerMax : Int := 45360

end ChTax
