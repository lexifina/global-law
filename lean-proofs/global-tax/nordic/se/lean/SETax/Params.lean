import TaxKernel

/-!
# Sweden, inkomstår 2025: parameters (every number with its source)

All amounts in whole kronor (`Int`), rates in basis points (`TaxKernel.BP = 10000`; 30,60 % = 3060).
Sources (full list with URLs in `refs/PARAMS.md`):

* Prisbasbelopp 2025 = 58 800 kr, inkomstbasbelopp 2025 = 80 600 kr: Skatteverket, *Teknisk beskrivning
  SKV 433, 2025, utgåva 35* (2024-12-16), avsnitt 1: "Prisbasbeloppet för 2025 har fastställts till 58 800 kr" /
  "Inkomstbasbeloppet ... har fastställts till 80 600 kr"; also Skatteverket *Belopp och procentsatser för
  inkomståret 2025* (2025-01-16).
* Skiktgräns 2025 = 625 800 kr: IL 65 kap. 5 § (Lag 2023:796: base 598 500 kr for 2024, indexed by KPI June/June
  + 2 percentage points, "avrundas uppåt till helt hundratal kronor"); amount from SKV 433 avsnitt 7.2:
  "20 procent av den del av den beskattningsbara förvärvsinkomsten som överstiger 625 800 kr".
* Stockholm 2025: kommunalskatt 18,22 % + regionskatt 12,38 % = 30,60 %; begravningsavgift 0,07 % (Stockholm is
  its own begravningshuvudman, begravningslagen 9 kap. 2, 4 §§). Skatteverket open data *Skattesatser kommuner
  2025* (skatteverket.entryscape.net/store/9/resource/2407, rows "01 80;STOCKHOLM"), SCB OE0101
  Kommunalskatter2000 (region 0180, 2025: 30.60 / 18.22 / 12.38).
* National average total municipal rate 2025 = 32,41 % (SCB OE0101, region 00): the rate the OECD's Taxing Wages
  uses for Sweden (its SLT = 32,41 % of taxable income, `harness/oecd_check.py`).
-/

namespace SETax
open TaxKernel

/-- The year's parameters. `kommun` is the hemortskommun's total rate (kommunalskatt + regionskatt), IL 65 kap.
3 §: "summan av de skattesatser för kommunalskatt och regionskatt som gäller i hemortskommunen". -/
structure Params where
  year : Nat := 2025
  /-- prisbasbelopp (SFB 2 kap. 6-7 §§) -/
  pbb : Int := 58800
  /-- inkomstbasbelopp (SFB 58 kap. 26-27 §§) -/
  ibb : Int := 80600
  /-- IL 65 kap. 5 § skiktgräns -/
  skiktgrans : Int := 625800
  /-- IL 65 kap. 5 §: "20 procent" -/
  stateRate : Int := 2000
  /-- IL 65 kap. 7 §: "30 procent av överskottet i inkomstslaget kapital" -/
  capitalRate : Int := 3000
  /-- kommunal + regional rate, bp (Stockholm 2025: 30,60 %) -/
  kommun : Int := 3060
  /-- begravningsavgift, bp (Stockholm 2025: 0,07 %) -/
  begravning : Int := 7
  /-- begravningsavgift in thousandths of a percent (10⁻⁵), when a rate with three decimals is given (round 15:
  EUROMOD's national averages 0,261 / 0,258 / 0,277 / 0,293 %, `--euromod`); `none` = use `begravning` -/
  begravning100k : Option Int := none
  /-- public service-avgift (lag 2018:1893, 5 §): "1 procent av avgiftsunderlaget" -/
  psRate : Int := 100
  /-- lag 2018:1893, 4 § (Lag 2024:1251): underlag "högst ... 1,55 gånger det inkomstbasbelopp", in thousandths -/
  psCapIbbMilli : Int := 1550
  /-- 67 kap. 7 § third and fourth steps (thousandths of pbb, bp): 2025 "1,813 ... 19,9 procent ... 2,776". -/
  jsaMidK : Int := 1813
  jsaRate : Int := 1990
  jsaTopK : Int := 2776
  /-- Age (reached during the year) from which the 66+ rules apply: "har fyllt 66 år vid beskattningsårets ingång"
  (2024-2025) = age ≥ 67; "fyllt 65" (2022-2023) = age ≥ 66. -/
  oldAge : Nat := 67
  /-- 2022-2024 (SKV 433 avsnitt 7.5.2): above 13,54 PBB the reduction is "minskat med 3 procent av skillnaden
  mellan arbetsinkomsten och 13,54 PBB" (removed for 2025). -/
  jsaPhaseOut : Bool := false
  /-- The OECD convention parameters are in use (`--oecd`). -/
  oecdConv : Bool := false
  deriving Repr, Inhabited

/-- Inkomstår 2025, Stockholm municipality (default). -/
def p2025 : Params := {}

/-- Inkomstår 2025 with the national average municipal rate 32,41 % and no begravningsavgift: the OECD's
Taxing Wages convention for Sweden. -/
def p2025oecd : Params := { kommun := 3241, begravning := 0, oecdConv := true }

/-! ## Inkomstår 2022-2024 (round 3, 2026-11-19)

Source for every amount: Skatteverket, *Teknisk beskrivning för skattetabeller* SKV 433 for 2022 (utgåva 32,
2021-12-14), 2023 (utgåva 33, 2022-12-20) and 2024 (utgåva 34, 2023-12-12), saved in `refs/skv433/`; it states
the parameters of IL as amended for each year. Municipal rates: SCB OE0101 Kommunalskatter2000 (API, saved as
`refs/raw/scb_0180_2022_2024.json`, `scb_00_2022_2024.json`).
* Prisbasbelopp 48 300 / 52 500 / 57 300; inkomstbasbelopp 71 000 / 74 300 / 76 200 ("Prisbasbeloppet för 2022 har
  fastställts till 48 300 kr", etc.).
* Skiktgräns (65 kap. 5 §): "överstiger 540 700 kr" (2022), "598 500 kr" (2023), 598 500 (2024: "Beloppet har inte
  förändrats").
* Jobbskatteavdrag (67 kap. 7 §), SKV 433 avsnitt 7.5.2: 2022 and 2023 "1,812 PBB ... ökat med 12,8 procent av
  arbetsinkomsten mellan 3,24 och 8,08 PBB", above 8,08 PBB "2,432 PBB"; 2024 "1,813 PBB ... 16,43 procent",
  "2,608 PBB". Age rule: "inte fyllt 65 år" (2022, 2023), "inte fyllt 66 år" (2024).
* Public service-avgift maximum: "71 000 x 1,870" (2022), "74 300 x 1,75" (2023), "76 200 x 1,60" (2024), 1 %.
* Grundavdrag (63 kap.), allmän pensionsavgift and skattereduktion för förvärvsinkomst: same rules as 2025 in all
  three descriptions (pbb-based amounts).
* Stockholm (0180): 29,82 % (2022, 2023), 30,36 % (2024); whole country (00): 32,24 % (2022, 2023), 32,37 % (2024).
* Begravningsavgift Stockholm 2022-2024: not sourced; the 2025 rate 0,07 % is used (stated in `unsupported`).
* Barnbidrag (SFB 15 kap. 3, 8 §§): 1 250 kr and the flerbarnstillägg amounts as 2025 (unchanged text). -/
def p2022 : Params :=
  { year := 2022, pbb := 48300, ibb := 71000, skiktgrans := 540700, kommun := 2982, psCapIbbMilli := 1870,
    jsaMidK := 1812, jsaRate := 1280, jsaTopK := 2432, oldAge := 66, jsaPhaseOut := true }
def p2023 : Params :=
  { year := 2023, pbb := 52500, ibb := 74300, skiktgrans := 598500, kommun := 2982, psCapIbbMilli := 1750,
    jsaMidK := 1812, jsaRate := 1280, jsaTopK := 2432, oldAge := 66, jsaPhaseOut := true }
def p2024 : Params :=
  { year := 2024, pbb := 57300, ibb := 76200, skiktgrans := 598500, kommun := 3036, psCapIbbMilli := 1600,
    jsaMidK := 1813, jsaRate := 1643, jsaTopK := 2608, oldAge := 67, jsaPhaseOut := true }

/-- The year's parameters; with the OECD convention the national average rate and no begravningsavgift. -/
def yearParams (base : Params) (y : Nat) : Params :=
  let q := if y = 2022 then p2022 else if y = 2023 then p2023 else if y = 2024 then p2024 else base
  if y ≥ 2025 then base
  else if base.oecdConv then { q with kommun := (if y = 2024 then 3237 else 3224), begravning := 0, oecdConv := true }
  else q

/-! ## Allmän pensionsavgift: lag (1994:1744) -/

/-- 4 §: no fee "om inkomsterna understiger 42,3 procent av ... prisbasbeloppet": the smallest income in whole
kronor that does not fall below 0,423 × pbb (24 872,40 kr in 2025, so 24 873). -/
def feeFloor (p : Params) : Int := ceilDiv (423 * p.pbb) 1000

/-- 3 § tredje stycket: income above "8,07 gånger ... inkomstbasbeloppet" is disregarded (650 442 kr in 2025). -/
def feeCeiling (p : Params) : Int := 807 * p.ibb / 100

/-- Lag (1994:1744) as a kernel `Contribution`: 2 § "allmän pensionsavgift med 7 procent"; 3 § "Avgiften
avrundas till närmast hela hundratal kronor. Avgift som slutar på 50 kronor avrundas till närmast lägre
hundratal kronor" (`Round.halfDown`, step 100). The income itself is first rounded down to hundreds (3 § första
stycket: "var för sig avrundas till närmast lägre hundratal kronor"), done by the caller. -/
def pensionFee (p : Params) : Contribution :=
  { name := "allmanPensionsavgift", sched := Schedule.flat 700, floor := feeFloor p, ceiling := feeCeiling p,
    round := { mode := .halfDown, step := 100 } }

/-- IL 65 kap. 5 §: 20 % above the skiktgräns, on beskattningsbar förvärvsinkomst (a kernel `Schedule`). -/
def stateSchedule (p : Params) : Schedule := Schedule.flatAbove p.skiktgrans p.stateRate

/-- IL 65 kap. 3 §: the municipal tax is one flat rate on beskattningsbar förvärvsinkomst. -/
def municipalSchedule (p : Params) : Schedule := Schedule.flat p.kommun

/-- The Nordic dual income tax (kernel `Dual`): IL 65 kap. 7 § 30 % on the capital surplus; 67 kap. 10 §
underskott: "30 procent av den del av underskottet som inte överstiger 100 000 kronor och med 21 procent av det
återstående underskottet". The earned side is not one schedule in Sweden (municipal + state + credits), so the
model uses the kernel's capital and deficit schedules and computes the earned side itself. -/
def dual (p : Params) : Dual :=
  { earned := Schedule.flat 0, capital := Schedule.flat p.capitalRate,
    deficit := Schedule.ofList [(0, 3000), (100000, 2100)] }

/-! ## Barnbidrag: socialförsäkringsbalken 15 kap. (amounts per month) -/

/-- SFB 15 kap. 3 §: "Allmänt barnbidrag lämnas med 1 250 kronor i månaden för varje barn". -/
def barnbidragMonth : Int := 1250

/-- SFB 15 kap. 8 §: flerbarnstillägg per month for the n-th child: "150 kronor ... för det andra barnet, 580
kronor ... för det tredje barnet, 1 010 kronor ... för det fjärde barnet, och 1 250 kronor ... för det femte barnet
och varje ytterligare barn". -/
def flerbarnstillaggMonth : Nat → Int
  | 0 => 0
  | 1 => 0
  | 2 => 150
  | 3 => 150 + 580
  | 4 => 150 + 580 + 1010
  | n + 5 => 150 + 580 + 1010 + 1250 * (n + 1)

/-- Annual barnbidrag + flerbarnstillägg for `n` children who get allmänt barnbidrag all year (SFB 15 kap. 4 §:
"till och med det kvartal då barnet fyller 16 år"). -/
def barnbidragYear (n : Nat) : Int := 12 * (barnbidragMonth * n + flerbarnstillaggMonth n)

/-! ## Egenavgifter (socialavgiftslagen 2000:980, 3 kap.) for self-employment -/

/-- Egenavgifter 2025 "Född 1959 eller senare 28,97 procent", "Född 1938 till 1958 10,21 procent" (Skatteverket,
*Belopp och procentsatser för inkomståret 2025*). -/
def egenavgiftRate (age : Nat) : Int := if age ≥ 67 then 1021 else 2897

end SETax
